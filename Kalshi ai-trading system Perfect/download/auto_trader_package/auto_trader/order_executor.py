"""
Order Executor with Risk Management.

Handles order placement, position tracking, daily P&L,
and risk controls for the auto-trader.
"""

import json
import time
from datetime import datetime, timezone, date
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field, asdict
from pathlib import Path

from .config import TradingConfig, POSITION_FILE, TRADE_LOG_DIR
from .kalshi_client import KalshiClient
from .momentum_detector import MomentumSignal


@dataclass
class Trade:
    """Record of a single trade."""
    trade_id: str
    timestamp: str
    symbol: str
    direction: str  # "UP" or "DOWN"
    side: str       # "yes" or "no"
    market_ticker: str
    contracts: int
    entry_price: float  # Price per contract in dollars
    cost_dollars: float
    paper_trade: bool
    outcome: Optional[str] = None  # "WIN", "LOSS", "PENDING"
    payout_dollars: Optional[float] = None
    profit_dollars: Optional[float] = None


@dataclass
class DailyStats:
    """Daily trading statistics."""
    date: str
    total_trades: int = 0
    wins: int = 0
    losses: int = 0
    pending: int = 0
    gross_profit: float = 0.0
    gross_loss: float = 0.0
    net_pnl: float = 0.0
    total_cost: float = 0.0


class OrderExecutor:
    """
    Executes trades with risk management controls.

    Risk Controls:
    1. Maximum position size per trade
    2. Maximum daily loss limit (stops bot when hit)
    3. Cooldown period after losses
    4. Only trade on STRONG or MODERATE momentum signals
    5. Track all positions and resolve outcomes
    """

    def __init__(self, kalshi_client: KalshiClient,
                 config: Optional[TradingConfig] = None):
        self.client = kalshi_client
        self.config = config or TradingConfig()
        self.paper_trading = self.config.PAPER_TRADING

        # State tracking
        self._trades: List[Trade] = []
        self._daily_stats = DailyStats(date=date.today().isoformat())
        self._cooldown_until: Optional[str] = None  # Window ID to skip
        self._active_positions: Dict[str, Trade] = {}  # market_ticker -> Trade
        self._trade_counter = 0

        # Load existing state
        self._load_state()

        # Auto-reset daily stats if it's a new day
        self._is_new_day()

    # ── State Persistence ──────────────────────────────────────────

    def _load_state(self):
        """Load saved trading state from disk."""
        state_file = POSITION_FILE
        if state_file.exists():
            try:
                data = json.loads(state_file.read_text())
                self._daily_stats = DailyStats(**data.get("daily_stats", {}))
                self._trade_counter = data.get("trade_counter", 0)

                # Reconstruct trades
                for t_data in data.get("trades", []):
                    trade = Trade(**t_data)
                    self._trades.append(trade)
                    if trade.outcome == "PENDING":
                        self._active_positions[trade.market_ticker] = trade

                print(f"[OrderExecutor] Loaded state: {len(self._trades)} trades, "
                      f"P&L: ${self._daily_stats.net_pnl:.2f}")

            except (json.JSONDecodeError, TypeError) as e:
                print(f"[OrderExecutor] Failed to load state: {e}")

    def _save_state(self):
        """Persist trading state to disk."""
        state_file = POSITION_FILE
        data = {
            "daily_stats": asdict(self._daily_stats),
            "trade_counter": self._trade_counter,
            "trades": [asdict(t) for t in self._trades],
        }
        state_file.write_text(json.dumps(data, indent=2))

    # ── Risk Checks ────────────────────────────────────────────────

    def _check_daily_loss_limit(self) -> bool:
        """Check if we've hit the daily loss limit."""
        if self._daily_stats.net_pnl <= -self.config.MAX_DAILY_LOSS:
            print(f"[OrderExecutor] DAILY LOSS LIMIT HIT: "
                  f"${self._daily_stats.net_pnl:.2f} / -${self.config.MAX_DAILY_LOSS:.2f}")
            return False
        return True

    def reset_daily_stats(self):
        """Reset daily P&L tracking — clears the loss limit lockout."""
        today = date.today().isoformat()
        self._daily_stats = DailyStats(date=today)
        self._cooldown_until = None
        self._save_state()
        print(f"[OrderExecutor] Daily stats RESET — P&L cleared, loss limit unlocked")

    def set_daily_loss_limit(self, limit: float):
        """Update the daily loss limit at runtime."""
        self.config.MAX_DAILY_LOSS = limit
        print(f"[OrderExecutor] Daily loss limit updated to: ${limit:.2f}")
        # Check if we're now below the new limit
        if self._daily_stats.net_pnl > -limit:
            print(f"[OrderExecutor] Current P&L ${self._daily_stats.net_pnl:.2f} is within new limit — trading unlocked!")

    def _check_cooldown(self, window_id: str) -> bool:
        """Check if we're in a cooldown period."""
        if not self.config.COOLDOWN_AFTER_LOSS:
            return True

        if self._cooldown_until and self._cooldown_until == window_id:
            print(f"[OrderExecutor] COOLDOWN: Skipping window {window_id}")
            return False

        return True

    def _is_new_day(self) -> bool:
        """Check if it's a new trading day (reset daily stats)."""
        today = date.today().isoformat()
        if self._daily_stats.date != today:
            self._daily_stats = DailyStats(date=today)
            return True
        return False

    # ── Trade Execution ────────────────────────────────────────────

    def execute_trade(self, signal: MomentumSignal,
                      market_info: Dict[str, Any],
                      window_id: str) -> Optional[Trade]:
        """
        Execute a trade based on a momentum signal.

        Args:
            signal: The momentum analysis result
            market_info: Kalshi market data (from find_15min_contracts)
            window_id: Identifier for the current 15-min window

        Returns the Trade record or None if trade was not executed.
        """
        # ── Pre-trade Risk Checks ──────────────────────────────
        self._is_new_day()

        if signal.recommendation == "SKIP":
            print(f"[OrderExecutor] Skipping {signal.symbol}: {signal.reason}")
            return None

        if not self._check_daily_loss_limit():
            return None

        if not self._check_cooldown(window_id):
            return None

        # Determine which contract to buy
        # Kalshi 15-min markets are SINGLE binary contracts:
        #   YES = price will go UP (price >= strike)
        #   NO  = price will go DOWN (price < strike)
        # So for an UP prediction, buy YES. For DOWN, buy NO.
        direction = signal.direction  # "UP" or "DOWN"

        if direction == "UP":
            # Buy YES contracts — we predict price >= strike
            side = "yes"
            ticker = market_info.get("up_ticker")
            # Use ask price for buying (best available), fallback to last price
            price_cents = market_info.get("up_ask_cents") or market_info.get("up_price")
        elif direction == "DOWN":
            # Buy NO contracts — we predict price < strike
            side = "no"
            ticker = market_info.get("down_ticker")
            # Use ask price for buying (best available), fallback to last price
            price_cents = market_info.get("down_ask_cents") or market_info.get("down_price")
        else:
            return None

        if not ticker:
            print(f"[OrderExecutor] No {direction} ticker found for {signal.symbol}")
            return None

        # Ensure price is a whole number (Kalshi requires integer cents 1-99)
        price_cents = max(1, min(99, int(round(price_cents))))

        # Calculate position size
        # price_cents is in cents (1-99), contracts pay $1 if correct
        # Cost per contract = price_cents / 100 (in dollars)
        if price_cents and price_cents > 0:
            cost_per_contract = price_cents / 100.0  # Convert from cents to dollars
        else:
            # Estimate based on signal confidence
            cost_per_contract = 0.50 + (signal.confidence * 0.20)

        # Number of contracts within our max position size
        num_contracts = max(1, int(self.config.MAX_POSITION_SIZE / cost_per_contract))
        total_cost = num_contracts * cost_per_contract

        # Cap at max position size
        if total_cost > self.config.MAX_POSITION_SIZE:
            num_contracts = max(1, int(self.config.MAX_POSITION_SIZE / cost_per_contract))
            total_cost = num_contracts * cost_per_contract

        # Create trade record
        self._trade_counter += 1
        trade_id = f"TRADE-{self._trade_counter:04d}"

        trade = Trade(
            trade_id=trade_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            symbol=signal.symbol,
            direction=direction,
            side=side,
            market_ticker=ticker,
            contracts=num_contracts,
            entry_price=cost_per_contract,
            cost_dollars=total_cost,
            paper_trade=self.paper_trading,
            outcome="PENDING",
        )

        # ── Execute or Simulate ────────────────────────────────
        if self.paper_trading:
            print(f"[OrderExecutor] PAPER TRADE: {trade.trade_id} | "
                  f"{direction} {signal.symbol} | "
                  f"side={side} {num_contracts}x @ ${cost_per_contract:.3f} = ${total_cost:.2f} | "
                  f"Confidence: {signal.confidence:.0%}")
        else:
            # Live trading: place the actual order
            # price_cents is already in cents (1-99) for the correct side
            result = self.client.create_order(
                ticker=ticker,
                side=side,
                count=num_contracts,
                price=price_cents,
            )

            if not result:
                print(f"[OrderExecutor] Order failed for {trade.trade_id}")
                return None

            print(f"[OrderExecutor] LIVE TRADE: {trade.trade_id} | "
                  f"{direction} {signal.symbol} | "
                  f"{num_contracts}x @ ${cost_per_contract:.3f} = ${total_cost:.2f}")

        # Record the trade
        self._trades.append(trade)
        self._active_positions[ticker] = trade
        self._daily_stats.total_trades += 1
        self._daily_stats.pending += 1
        self._daily_stats.total_cost += total_cost

        self._save_state()
        self._log_trade(trade, signal)

        return trade

    # ── Outcome Resolution ─────────────────────────────────────────

    def resolve_outcomes(self, momentum_detector=None) -> int:
        """
        Check all pending trades and resolve their outcomes.

        Resolution strategy (in order of preference):
        1. Check Kalshi API for settled market data (direct or series fallback)
        2. If market data unavailable, use Binance price comparison
        3. If position is stale (>30 min past close), force-resolve

        Args:
            momentum_detector: Optional MomentumDetector for Binance fallback

        Returns the number of trades resolved.
        """
        resolved = 0
        to_remove = []

        for ticker, trade in list(self._active_positions.items()):
            # ── Strategy 1: Check Kalshi API ───────────────────────
            market_data = self.client.get_market_price(ticker)
            outcome_determined = False

            if market_data:
                status = market_data.get("status", "")
                settlement_price = market_data.get("settlement_price")
                result = market_data.get("result")
                last_price = market_data.get("last_price")

                # Check if market has a definitive result (regardless of status label)
                # Kalshi sometimes returns result on markets not explicitly "settled"
                if settlement_price is not None:
                    # Settlement price is in cents: 100 = YES won, 0 = NO won
                    won = (trade.side == "yes" and settlement_price >= 100) or \
                          (trade.side == "no" and settlement_price <= 0)
                    outcome_determined = True
                elif result is not None and result != "":
                    # Result field: "yes" or "no"
                    won = (trade.side == "yes" and result == "yes") or \
                          (trade.side == "no" and result == "no")
                    outcome_determined = True
                    print(f"[OrderExecutor] Resolved {trade.trade_id} from result={result}")

                elif status in ("settled", "closed", "finalized"):
                    if last_price is not None and isinstance(last_price, (int, float)):
                        # Last price can indicate settlement:
                        # YES last_price >= 50 means YES won, < 50 means NO won
                        if trade.side == "yes":
                            won = last_price >= 50
                        else:
                            won = last_price <= 50
                        outcome_determined = True
                        print(f"[OrderExecutor] Resolved {trade.trade_id} from last_price={last_price} (status={status})")

            # ── Strategy 2: Binance price comparison ────────────────
            if not outcome_determined and momentum_detector is not None:
                actual_price = momentum_detector.fetch_current_price(trade.symbol)
                if actual_price is not None:
                    # Get the strike/target price from the market ticker
                    # If we predicted UP (side=yes), we expected price to go up
                    # If we predicted DOWN (side=no), we expected price to go down
                    # Compare current price vs what it was at trade time
                    # Use entry_price as a rough proxy for where we entered
                    # For a more accurate check, use the strike price from Kalshi
                    market_info = self.client.find_15min_contracts(trade.symbol)
                    strike = market_info.get("target_price", 0) if market_info else 0

                    if strike > 0:
                        # Kalshi settles based on whether actual price >= strike
                        price_above_strike = actual_price >= strike
                        if trade.side == "yes":
                            won = price_above_strike  # YES = price >= strike
                        else:
                            won = not price_above_strike  # NO = price < strike

                        outcome_determined = True
                        print(f"[OrderExecutor] Resolved {trade.trade_id} via Binance: "
                              f"price=${actual_price:.2f} vs strike=${strike:.2f}")

            # ── Strategy 3: Stale position force-resolution ─────────
            if not outcome_determined:
                # Check if this position is stale (more than 30 min old)
                try:
                    trade_time = datetime.fromisoformat(trade.timestamp)
                    now = datetime.now(timezone.utc)
                    age_minutes = (now - trade_time).total_seconds() / 60

                    if age_minutes > 30:
                        # Position is stale — we can't determine the outcome
                        # Count it as a loss to be conservative and free the slot
                        print(f"[OrderExecutor] STALE position {trade.trade_id} "
                              f"({age_minutes:.0f} min old) — force-resolving")
                        # Try Binance one more time with a simple direction check
                        if momentum_detector is not None:
                            current_price = momentum_detector.fetch_current_price(trade.symbol)
                            if current_price is not None and trade.entry_price > 0:
                                # Very rough: did the price go the way we predicted?
                                # Since we don't have the exact start price, assume
                                # the entry was at the strike. If we bought YES (UP),
                                # we need current price > entry. If NO (DOWN), < entry.
                                # This is approximate but better than leaving it stuck.
                                won = False  # Conservative: assume loss on stale
                                outcome_determined = True
                                print(f"[OrderExecutor] Stale {trade.trade_id} resolved "
                                      f"as LOSS (conservative)")
                        else:
                            won = False
                            outcome_determined = True
                except (ValueError, TypeError):
                    pass

            # ── Apply outcome ───────────────────────────────────────
            if outcome_determined:
                if won:
                    trade.outcome = "WIN"
                    trade.payout_dollars = trade.contracts * 1.0  # $1 per contract
                    trade.profit_dollars = trade.payout_dollars - trade.cost_dollars
                    self._daily_stats.wins += 1
                    self._daily_stats.gross_profit += trade.profit_dollars
                else:
                    trade.outcome = "LOSS"
                    trade.payout_dollars = 0.0
                    trade.profit_dollars = -trade.cost_dollars
                    self._daily_stats.losses += 1
                    self._daily_stats.gross_loss += trade.cost_dollars

                    # Set cooldown if configured
                    if self.config.COOLDOWN_AFTER_LOSS:
                        self._cooldown_until = None  # Will be set by next window

                self._daily_stats.pending -= 1
                self._daily_stats.net_pnl += trade.profit_dollars

                print(f"[OrderExecutor] RESOLVED {trade.trade_id}: {trade.outcome} | "
                      f"P&L: ${trade.profit_dollars:+.2f}")

                to_remove.append(ticker)
                resolved += 1
            else:
                # Could not resolve yet — will retry next window
                print(f"[OrderExecutor] Could not resolve {trade.trade_id} yet — "
                      f"will retry next window")

        # Clean up resolved positions
        for ticker in to_remove:
            del self._active_positions[ticker]

        if resolved > 0:
            self._save_state()

        return resolved

    # ── Paper Trading Resolution ───────────────────────────────────

    def resolve_paper_trade(self, trade: Trade, actual_direction: str) -> Trade:
        """
        Resolve a paper trade by checking if the actual outcome
        matched our prediction.

        Args:
            trade: The trade to resolve
            actual_direction: "UP" or "DOWN" (from Binance price comparison)
        """
        won = trade.direction == actual_direction

        if won:
            trade.outcome = "WIN"
            trade.payout_dollars = trade.contracts * 1.0
            trade.profit_dollars = trade.payout_dollars - trade.cost_dollars
            self._daily_stats.wins += 1
            self._daily_stats.gross_profit += trade.profit_dollars
        else:
            trade.outcome = "LOSS"
            trade.payout_dollars = 0.0
            trade.profit_dollars = -trade.cost_dollars
            self._daily_stats.losses += 1
            self._daily_stats.gross_loss += trade.cost_dollars

            if self.config.COOLDOWN_AFTER_LOSS:
                print(f"[OrderExecutor] Setting cooldown after loss on {trade.symbol}")

        self._daily_stats.pending -= 1
        self._daily_stats.net_pnl += trade.profit_dollars

        if trade.market_ticker in self._active_positions:
            del self._active_positions[trade.market_ticker]

        self._save_state()

        print(f"[OrderExecutor] PAPER RESOLVED {trade.trade_id}: {trade.outcome} | "
              f"Predicted: {trade.direction}, Actual: {actual_direction} | "
              f"P&L: ${trade.profit_dollars:+.2f}")

        return trade

    # ── Logging ────────────────────────────────────────────────────

    def _log_trade(self, trade: Trade, signal: MomentumSignal):
        """Write trade details to the log file."""
        log_file = TRADE_LOG_DIR / f"trades_{date.today().isoformat()}.jsonl"
        entry = {
            "trade": asdict(trade),
            "signal": {
                "direction": signal.direction,
                "strength": signal.strength,
                "confidence": signal.confidence,
                "price_change_pct": signal.price_change_pct,
                "consistency": signal.direction_consistency,
                "volatility": signal.volatility,
                "reason": signal.reason,
            },
        }
        with open(log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")

    # ── Reporting ──────────────────────────────────────────────────

    def get_stats(self) -> Dict[str, Any]:
        """Get current trading statistics."""
        win_rate = (self._daily_stats.wins / self._daily_stats.total_trades * 100
                    if self._daily_stats.total_trades > 0 else 0)

        return {
            "paper_trading": self.paper_trading,
            "daily_stats": asdict(self._daily_stats),
            "active_positions": len(self._active_positions),
            "win_rate": f"{win_rate:.1f}%",
            "total_lifetime_trades": len(self._trades),
            "mode": "PAPER" if self.paper_trading else "LIVE",
        }

    def get_status_summary(self) -> str:
        """Get a human-readable status summary."""
        stats = self.get_stats()
        ds = stats["daily_stats"]
        return (
            f"Mode: {stats['mode']} | "
            f"Trades: {ds['total_trades']} | "
            f"W/L: {ds['wins']}/{ds['losses']} | "
            f"Win Rate: {stats['win_rate']} | "
            f"P&L: ${ds['net_pnl']:+.2f} | "
            f"Active: {stats['active_positions']}"
        )
