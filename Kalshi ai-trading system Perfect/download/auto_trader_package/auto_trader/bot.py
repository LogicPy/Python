"""
Kalshi Crypto Scalper — Main Bot Orchestrator.

The bot runs a continuous loop:
1. Scheduler waits for T-8 min before each 15-min window closes
2. Momentum detector analyzes Binance price data for ALL symbols
3. AI analyzer provides additional signal (optional)
4. Order executor places trades on ALL directional signals (aggressive mode)
5. When window closes, outcomes are resolved
6. Repeat

AGGRESSION MODES:
  "conservative" — Only best STRONG/MODERATE signal per window
  "aggressive"   — Trade ALL WEAK+ directional signals (recommended)
  "hyper"        — Trade ANY directional signal, maximum frequency
"""

import json
import time
import signal
import sys
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

from .config import (
    KalshiConfig, TradingConfig, BinanceConfig, StrategyConfig,
    WeatherTradingConfig, DynamicCategoryConfig, QuantitativeProbabilityConfig,
    SYMBOL_MAP, POSITION_FILE
)
from .kalshi_client import KalshiClient
from .momentum_detector import MomentumDetector, MomentumSignal
from .order_executor import OrderExecutor, Trade
from .scheduler import TradingWindowScheduler
from .ai_analyzer import AIAnalyzer
from .weather_bot import WeatherTradingBot
from .category_manager import DynamicCategoryManager


class CryptoScalperBot:
    """
    Late-Game Momentum Scalping Bot for Kalshi 15-minute crypto markets.

    Strategy:
    - Wait until 8 minutes before a 15-min window closes
    - Check Binance price momentum for ALL active symbols
    - Trade every symbol with a directional signal (aggressive mode)
    - Small consistent wins compound over many windows

    Safety Features:
    - Paper trading mode (default) — validates strategy with zero risk
    - Daily loss limit — stops trading if hit
    - Cooldown after losses — prevents tilt trading
    - Max position size per trade — caps risk on any single trade
    - Minimum confidence threshold — filters out truly random noise
    """

    def __init__(self, paper_mode: Optional[bool] = None, trading_mode: Optional[str] = None):
        # Configuration
        self.kalshi_config = KalshiConfig()
        self.trading_config = TradingConfig()
        self.binance_config = BinanceConfig()
        self.strategy_config = StrategyConfig()
        self.weather_config = WeatherTradingConfig()
        self.dynamic_config = DynamicCategoryConfig()

        # Override paper mode if specified
        if paper_mode is not None:
            self.trading_config.PAPER_TRADING = paper_mode

        # Override trading mode if specified (fixes CLI mode toggle)
        if trading_mode is not None:
            self.trading_config.TRADING_MODE = trading_mode.lower()

        # Quant mode config
        self.quant_config = QuantitativeProbabilityConfig()

        # Components - Crypto
        self.client = KalshiClient(self.kalshi_config)
        self.detector = MomentumDetector(self.trading_config, self.binance_config)
        self.executor = OrderExecutor(self.client, self.trading_config)
        self.scheduler = TradingWindowScheduler(self.trading_config)
        self.ai = AIAnalyzer()

        # Quant Probability strategy (loaded when TRADING_MODE=quant_probability)
        self._quant_strategy = None
        self._init_quant_strategy()

        # Components - Weather
        self.weather_bot = WeatherTradingBot(paper_mode=paper_mode, trading_mode=trading_mode)

        # Components - Category Management
        self.category_manager = DynamicCategoryManager(
            strategy_config=self.strategy_config,
            dynamic_config=self.dynamic_config,
        )

        # State
        self._running = False
        self._last_signals: List[MomentumSignal] = []
        self._last_trades: List[Trade] = []

        # Register scheduler callbacks
        self.scheduler.on_entry(self._on_entry)
        self.scheduler.on_resolve(self._on_resolve)

    def _init_quant_strategy(self):
        """Initialize or re-initialize the quant strategy based on current TRADING_MODE."""
        if self.trading_config.TRADING_MODE == "quant_probability" and self.quant_config.QUANT_MODE_ENABLED:
            from .quant_strategy import QuantitativeProbabilityStrategy
            self._quant_strategy = QuantitativeProbabilityStrategy(self.quant_config)
            print(f"[Bot] QUANTITATIVE PROBABILITY MODE active — >60% prob, +15c EV, Safe-Bet chains")
        else:
            self._quant_strategy = None

    def set_trading_mode(self, mode: str):
        """Change trading mode at runtime and reinitialize quant strategy."""
        mode = mode.lower()
        self.trading_config.TRADING_MODE = mode
        self._init_quant_strategy()
        # Propagate to weather bot
        if hasattr(self, 'weather_bot') and self.weather_bot:
            self.weather_bot.set_trading_mode(mode)

    # ── Trading Cycle ──────────────────────────────────────────────

    def _on_entry(self, window_id: str):
        """
        Called at T-8 minutes before window close.
        This is where we analyze ALL symbols and trade every opportunity.
        """
        print(f"\n{'='*60}")
        print(f"[Bot] ENTRY WINDOW: {window_id}")
        mode_label = "QUANT PROBABILITY" if self._quant_strategy else self.trading_config.AGGRESSION.upper()
        print(f"[Bot] Mode: {'PAPER' if self.trading_config.PAPER_TRADING else 'LIVE'} | "
              f"Strategy: {mode_label}")
        print(f"{'='*60}")

        # Step 1: Scan ALL symbols for momentum signals
        active_symbols = self.trading_config.ACTIVE_SYMBOLS
        print(f"[Bot] Scanning {len(active_symbols)} symbols: {', '.join(active_symbols)}")

        # Print ALL momentum readings (even SKIP ones — so you can see what's happening)
        all_signals = self.detector.get_multi_symbol_analysis(active_symbols)

        print(f"\n[Bot] Momentum Readings:")
        for symbol, sig in all_signals.items():
            marker = ">>>" if sig.recommendation != "SKIP" else "   "
            print(f"  {marker} {symbol}: {sig.direction} {sig.strength} | "
                  f"{sig.price_change_pct:+.3f}% | "
                  f"conf={sig.confidence:.0%} | "
                  f"consist={sig.direction_consistency:.0%} | "
                  f"{sig.recommendation}")

        # Step 2: Find all tradeable opportunities
        if self.trading_config.TRADE_ALL_SIGNALS:
            opportunities = self.detector.find_all_opportunities(active_symbols)
        else:
            # Legacy: just the best one
            best = self.detector.find_best_opportunity(active_symbols)
            opportunities = [best] if best else []

        if not opportunities:
            print(f"[Bot] No trading opportunities this window")
            return

        print(f"\n[Bot] {len(opportunities)} trading opportunities found!")

        # Step 3: Trade each opportunity
        self._last_signals = []
        self._last_trades = []

        for symbol, signal in opportunities:
            self._last_signals.append(signal)

            print(f"\n[Bot] --- {symbol} ---")
            print(f"  Direction: {signal.direction} | Strength: {signal.strength}")
            print(f"  Confidence: {signal.confidence:.0%} | Change: {signal.price_change_pct:+.3f}%")
            print(f"  Consistency: {signal.direction_consistency:.0%} | Vol: {signal.volatility:.4f}%")
            print(f"  Reason: {signal.reason}")

            # Get Kalshi market data
            market_info = self.client.find_15min_contracts(symbol)

            if not market_info or not market_info.get("market_ticker"):
                print(f"  No active Kalshi market for {symbol} — skipping")
                continue

            print(f"  Kalshi: {market_info.get('market_ticker')} | "
                  f"YES=${market_info.get('yes_price_dollars', 0):.2f} | "
                  f"NO=${market_info.get('no_price_dollars', 0):.2f}")

            # AI analysis (optional confidence modifier)
            if self.ai.api_key:
                ai_result = self.ai.analyze_signal(
                    symbol,
                    {
                        "direction": signal.direction,
                        "strength": signal.strength,
                        "confidence": signal.confidence,
                        "price_change_pct": signal.price_change_pct,
                        "direction_consistency": signal.direction_consistency,
                        "volatility": signal.volatility,
                        "current_price": signal.current_price,
                    },
                    market_info,
                )

                if ai_result:
                    print(f"  AI: {ai_result.get('ai_direction')} | "
                          f"mod={ai_result.get('confidence_modifier', 0):+.2f} | "
                          f"{ai_result.get('risk_warning', 'OK')}")

                    # Apply AI modifier
                    modifier = ai_result.get("confidence_modifier", 0)

                    # If AI disagrees, reduce confidence
                    if ai_result.get("ai_direction") != signal.direction and \
                       ai_result.get("ai_direction") != "NEUTRAL":
                        print(f"  AI DISAGREES — reducing confidence")
                        modifier = min(modifier, -0.10)

                    signal.confidence = max(0.0, min(1.0, signal.confidence + modifier))

                    # Skip if confidence dropped below minimum
                    if signal.confidence < self.trading_config.MIN_CONFIDENCE:
                        print(f"  Confidence too low ({signal.confidence:.0%}) — skipping")
                        continue

            # Execute the trade
            trade = self.executor.execute_trade(signal, market_info, window_id)

            if trade:
                self._last_trades.append(trade)
                print(f"  TRADE: {trade.trade_id} | "
                      f"{trade.direction} {trade.symbol} "
                      f"({trade.contracts}x @ ${trade.entry_price:.3f})")

        # Print summary
        if self._last_trades:
            print(f"\n[Bot] {len(self._last_trades)} trade(s) placed this window!")
        else:
            print(f"\n[Bot] No trades executed this window")

        print(f"[Bot] {self.executor.get_status_summary()}")

    def _on_resolve(self, window_id: str):
        """
        Called when a 15-min window closes.
        Resolve outcomes for all pending trades.

        For LIVE trades, we use a 3-tier resolution:
        1. Check Kalshi API (direct + series fallback)
        2. Compare Binance spot price vs strike price
        3. Force-resolve stale positions (>30 min old)

        For PAPER trades, we use Binance price comparison.
        """
        print(f"\n[Bot] RESOLVING WINDOW: {window_id}")

        if self.trading_config.PAPER_TRADING:
            self._resolve_paper_trades(window_id)
        else:
            # Pass the momentum detector for Binance fallback resolution
            resolved = self.executor.resolve_outcomes(momentum_detector=self.detector)
            print(f"[Bot] Resolved {resolved} trades")

        print(f"[Bot] {self.executor.get_status_summary()}")

    def _resolve_paper_trades(self, window_id: str):
        """
        Resolve paper trades by checking actual price movement.
        """
        stats = self.executor.get_stats()
        active = stats.get("active_positions", 0)

        if active == 0:
            return

        # Check each pending trade
        for ticker, trade in list(self.executor._active_positions.items()):
            current_price = self.detector.fetch_current_price(trade.symbol)

            if current_price is None:
                continue

            # Find the matching signal for this trade
            matching_signal = None
            for sig in self._last_signals:
                if sig.symbol == trade.symbol:
                    matching_signal = sig
                    break

            if matching_signal:
                start_price = matching_signal.start_price
                actual_direction = "UP" if current_price > start_price else "DOWN"
            else:
                actual_direction = "UP" if current_price > trade.entry_price else "DOWN"

            self.executor.resolve_paper_trade(trade, actual_direction)

    # ── Bot Control ────────────────────────────────────────────────

    def start(self):
        """Start the trading bot."""
        if self._running:
            print("[Bot] Already running")
            return

        print("\n" + "=" * 60)
        strategy_name = "QUANTITATIVE PROBABILITY" if self._quant_strategy else "SCALPER"
        print("  KALSHI CRYPTO " + strategy_name + " BOT")
        if self._quant_strategy:
            print("  >60% Probability | +EV Focus | Safe-Bet Chains")
        else:
            print("  Late-Game Momentum Scalping Bot")
        print("=" * 60)
        print(f"  Mode: {'PAPER TRADING (Safe)' if self.trading_config.PAPER_TRADING else 'LIVE TRADING (Real Money!)'}")
        print(f"  Strategy: {strategy_name}")
        if not self._quant_strategy:
            print(f"  Aggression: {self.trading_config.AGGRESSION.upper()}")
        print(f"  Trade All Signals: {self.trading_config.TRADE_ALL_SIGNALS}")
        print(f"  Symbols: {', '.join(self.trading_config.ACTIVE_SYMBOLS)}")
        print(f"  Max Position: ${self.trading_config.MAX_POSITION_SIZE:.2f}")
        print(f"  Daily Loss Limit: ${self.trading_config.MAX_DAILY_LOSS:.2f}")
        print(f"  Min Momentum: {self.trading_config.MIN_MOMENTUM_PCT:.3f}%")
        print(f"  Min Confidence: {self.trading_config.MIN_CONFIDENCE:.0%}")
        print(f"  Entry Window: T-{self.trading_config.ENTRY_WINDOW_MINUTES} min")
        print(f"  Cooldown After Loss: {self.trading_config.COOLDOWN_AFTER_LOSS}")
        if self._quant_strategy:
            print("  --- Quant Probability Mode ---")
            print(f"  Quant Min Win Prob: {self.quant_config.MIN_WIN_PROBABILITY:.0%}")
            print(f"  Quant Min EV Edge: {self.quant_config.MIN_EV_EDGE_CENTS:.0f}c")
            print(f"  Quant Min Confidence: {self.quant_config.MIN_CONFIDENCE:.0%}")
            print(f"  Compound Threshold: {self.quant_config.COMPOUND_THRESHOLD:.2f}")
            print(f"  Max Safe-Bet Chains: {self.quant_config.MAX_SAFE_BET_CHAINS}")
        print("=" * 60)

        if not self.trading_config.PAPER_TRADING:
            print("\n  LIVE TRADING MODE — Real money at risk!")
            print("  Press Ctrl+C to stop at any time\n")
        else:
            print("\n  PAPER MODE — No real money, just simulation\n")

        # Authenticate with Kalshi
        print("[Bot] Authenticating with Kalshi...")
        if not self.client.login():
            print("[Bot] Authentication FAILED — check your API keys")
            print("[Bot] Bot will continue in paper mode (market data may be limited)")
        elif not self.trading_config.PAPER_TRADING:
            # In live mode, also test POST authentication
            print("[Bot] Testing POST authentication for order placement...")
            if not self.client.test_post_auth():
                print("[Bot] WARNING: POST auth failed — orders will fail!")
                print("[Bot] Falling back to PAPER MODE for safety")
                self.trading_config.PAPER_TRADING = True
                self.executor.paper_trading = True

        # Start the crypto scheduler
        self._running = True
        self.scheduler.start()

        # Start weather bot if enabled
        if self.strategy_config.ENABLE_WEATHER:
            print("[Bot] Starting weather trading bot...")
            self.weather_bot.start()
        else:
            print("[Bot] Weather trading disabled (ENABLE_WEATHER=false)")

        # Print next entry time
        next_entry = self.scheduler.get_next_entry_time()
        print(f"[Bot] Next crypto entry time: {next_entry.isoformat()[:19]}")

        # Print active categories
        active_cats = self.category_manager.get_active_categories()
        print(f"[Bot] Active categories: {', '.join(active_cats)}")

        # Keep main thread alive
        try:
            while self._running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[Bot] Shutting down...")
            self.stop()

    def stop(self):
        """Stop the trading bot."""
        self._running = False
        self.scheduler.stop()
        self.weather_bot.stop()

        # Print final stats
        print(f"\n[Bot] Final Stats: {self.executor.get_status_summary()}")
        print(f"[Bot] Weather Stats: {self.weather_bot.get_status()}")
        print("[Bot] Bot stopped.")

    # ── Status API ─────────────────────────────────────────────────

    def get_status(self) -> Dict[str, Any]:
        """Get complete bot status for the dashboard."""
        return {
            "running": self._running,
            "mode": "PAPER" if self.trading_config.PAPER_TRADING else "LIVE",
            "trading_mode": self.trading_config.TRADING_MODE,
            "aggression": self.trading_config.AGGRESSION,
            "scheduler": self.scheduler.status,
            "trading": self.executor.get_stats(),
            "weather": self.weather_bot.get_status(),
            "categories": self.category_manager.get_status(),
            "last_signals": [
                {
                    "symbol": s.symbol,
                    "direction": s.direction,
                    "strength": s.strength,
                    "confidence": s.confidence,
                    "recommendation": s.recommendation,
                    "reason": s.reason,
                }
                for s in self._last_signals
            ] if self._last_signals else None,
            "active_symbols": self.trading_config.ACTIVE_SYMBOLS,
            "config": {
                "max_position": self.trading_config.MAX_POSITION_SIZE,
                "daily_loss_limit": self.trading_config.MAX_DAILY_LOSS,
                "min_momentum_pct": self.trading_config.MIN_MOMENTUM_PCT,
                "min_confidence": self.trading_config.MIN_CONFIDENCE,
                "entry_window_min": self.trading_config.ENTRY_WINDOW_MINUTES,
                "aggression": self.trading_config.AGGRESSION,
                "trade_all_signals": self.trading_config.TRADE_ALL_SIGNALS,
                "weather_auto_trade": self.weather_config.WEATHER_AUTO_TRADE,
                "weather_ai_enhanced": self.weather_config.WEATHER_AI_ENHANCED,
                "quant_mode_enabled": self.quant_config.QUANT_MODE_ENABLED,
            },
        }


# ── CLI Entry Point ────────────────────────────────────────────────

def main():
    """Run the bot from the command line."""
    import argparse

    parser = argparse.ArgumentParser(description="Kalshi Crypto Scalper")
    parser.add_argument("--live", action="store_true",
                       help="Enable live trading (default: paper mode)")
    parser.add_argument("--symbols", type=str, default=None,
                       help="Comma-separated symbols (e.g., BTC,ETH,XRP)")
    parser.add_argument("--max-position", type=float, default=None,
                       help="Max position size in dollars")
    parser.add_argument("--daily-limit", type=float, default=None,
                       help="Daily loss limit in dollars")
    parser.add_argument("--aggression", type=str, default=None,
                       choices=["conservative", "aggressive", "hyper"],
                       help="Trading aggression level")
    parser.add_argument("--mode", type=str, default=None,
                       choices=["scalper", "quant_probability"],
                       help="Trading strategy mode")
    parser.add_argument("--status", action="store_true",
                       help="Print current status and exit")

    args = parser.parse_args()

    # Create bot
    paper_mode = not args.live
    bot = CryptoScalperBot(paper_mode=paper_mode)

    # Apply overrides
    if args.symbols:
        bot.trading_config.ACTIVE_SYMBOLS = [s.strip().upper() for s in args.symbols.split(",")]
    if args.max_position:
        bot.trading_config.MAX_POSITION_SIZE = args.max_position
    if args.daily_limit:
        bot.trading_config.MAX_DAILY_LOSS = args.daily_limit
    if args.aggression:
        bot.trading_config.AGGRESSION = args.aggression
    if args.mode:
        bot.trading_config.TRADING_MODE = args.mode

    # Status check
    if args.status:
        print(json.dumps(bot.get_status(), indent=2, default=str))
        return

    # Start the bot
    bot.start()


if __name__ == "__main__":
    main()
