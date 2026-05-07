"""
Momentum Detection Engine for Late-Game Scalping.

Analyzes Binance price data to detect directional momentum
in the final minutes of a Kalshi 15-minute window.

Strategy: "Late-Game Momentum Scalping"
- At T-8 minutes, check if price is trending in one direction
- Even slight directional edges (0.03%+) are tradeable in 15-min markets
- Small consistent wins compound over many 15-minute windows

AGGRESSION LEVELS:
  "conservative" — Only trade STRONG/MODERATE signals (rare, high confidence)
  "aggressive"   — Trade WEAK+ signals (recommended scalping mode)
  "hyper"        — Trade ANY directional signal (maximum frequency)

IMPORTANT: US users MUST use api.binance.us (not api.binance.com).
"""

import time
import hmac
import hashlib
import statistics
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
from urllib.parse import urlencode

import requests

from .config import BinanceConfig, TradingConfig, SYMBOL_MAP


@dataclass
class MomentumSignal:
    """Result of a momentum analysis."""
    symbol: str
    direction: str  # "UP", "DOWN", or "FLAT"
    strength: str   # "STRONG", "MODERATE", "WEAK", "SLIGHT", "NONE"
    confidence: float  # 0.0 to 1.0
    price_change_pct: float
    direction_consistency: float  # What fraction of intervals agree with trend
    current_price: float
    start_price: float
    timeframe_seconds: int
    volatility: float
    recommendation: str  # "BUY_UP", "BUY_DOWN", "SKIP"
    reason: str


class MomentumDetector:
    """
    Detects price momentum from Binance data for scalping decisions.

    Uses multiple confirmation signals:
    1. Overall price change percentage over the analysis window
    2. Direction consistency (% of intervals moving same direction)
    3. Recent acceleration (is the trend speeding up?)
    4. Volatility check (too much volatility = unreliable)
    5. Volume confirmation (if available)
    6. Recent micro-trend (last 3 minutes vs overall)
    """

    def __init__(self, config: Optional[TradingConfig] = None,
                 binance_config: Optional[BinanceConfig] = None):
        self.config = config or TradingConfig()
        self.binance_config = binance_config or BinanceConfig()
        self.base_url = self.binance_config.BASE_URL
        self.api_key = self.binance_config.API_KEY
        self.api_secret = self.binance_config.API_SECRET
        self.aggression = self.config.AGGRESSION
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})

        # Add API key header if available (higher rate limits)
        if self.api_key:
            self.session.headers.update({
                "X-MBX-APIKEY": self.api_key,
            })
            print(f"[MomentumDetector] Using Binance API key for rate limits ({self.base_url})")
        else:
            print(f"[MomentumDetector] No Binance API key — using public endpoints ({self.base_url})")

        print(f"[MomentumDetector] Aggression: {self.aggression.upper()}")
        print(f"[MomentumDetector] Min momentum: {self.config.MIN_MOMENTUM_PCT:.3f}%")

        # Price history cache per symbol
        self._price_cache: Dict[str, List[Dict]] = {}
        self._cache_time: Dict[str, float] = {}
        self._cache_ttl = 5  # seconds

    def _sign_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sign a Binance US API request with HMAC-SHA256.
        Only needed for authenticated endpoints (not klines/ticker).
        """
        if not self.api_secret:
            return params

        params["timestamp"] = int(time.time() * 1000)
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        params["signature"] = signature
        return params

    def _get_binance_pair(self, symbol: str) -> str:
        """Get the Binance trading pair for a symbol."""
        info = SYMBOL_MAP.get(symbol)
        if info:
            return info["binance_pair"]
        return f"{symbol}USDT"

    def fetch_klines(self, symbol: str, interval: str = "1m",
                     limit: int = 15) -> List[Dict[str, Any]]:
        """Fetch kline (candlestick) data from Binance."""
        pair = self._get_binance_pair(symbol)

        try:
            params = {
                "symbol": pair,
                "interval": interval,
                "limit": limit,
            }

            resp = self.session.get(
                f"{self.base_url}/api/v3/klines",
                params=params,
                timeout=10,
            )
            resp.raise_for_status()
            raw_klines = resp.json()

            klines = []
            for k in raw_klines:
                klines.append({
                    "open_time": k[0],
                    "open": float(k[1]),
                    "high": float(k[2]),
                    "low": float(k[3]),
                    "close": float(k[4]),
                    "volume": float(k[5]),
                    "close_time": k[6],
                    "quote_volume": float(k[7]),
                })

            return klines

        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            if "451" in error_msg:
                print(f"[MomentumDetector] HTTP 451 — Binance.com blocks US users!")
                print(f"[MomentumDetector] Fix: Set BINANCE_BASE_URL=https://api.binance.us in .env")
            else:
                print(f"[MomentumDetector] Failed to fetch klines for {symbol}: {e}")
            return []

    def fetch_current_price(self, symbol: str) -> Optional[float]:
        """Get the current spot price from Binance."""
        pair = self._get_binance_pair(symbol)

        try:
            resp = self.session.get(
                f"{self.base_url}/api/v3/ticker/price",
                params={"symbol": pair},
                timeout=5,
            )
            resp.raise_for_status()
            data = resp.json()
            return float(data["price"])

        except requests.exceptions.RequestException as e:
            print(f"[MomentumDetector] Failed to fetch price for {symbol}: {e}")
            return None

    def analyze_momentum(self, symbol: str,
                         window_minutes: int = 10) -> MomentumSignal:
        """
        Analyze price momentum for a given symbol.

        This is the core strategy function. It fetches recent price data
        and determines if there's a directional edge to justify a trade.

        The key insight for SCALPING: We don't need STRONG momentum.
        We need ANY consistent directional bias. Even 0.03% with 60%
        consistency means the market is leaning one way — and that's
        enough to be profitable over many 15-minute windows.

        Args:
            symbol: Crypto symbol to analyze
            window_minutes: How many minutes of data to analyze

        Returns a MomentumSignal with direction, strength, and recommendation.
        """
        # Fetch 1-minute klines for the analysis window
        klines = self.fetch_klines(symbol, interval="1m", limit=window_minutes)

        if len(klines) < 5:
            return MomentumSignal(
                symbol=symbol,
                direction="FLAT",
                strength="NONE",
                confidence=0.0,
                price_change_pct=0.0,
                direction_consistency=0.0,
                current_price=0.0,
                start_price=0.0,
                timeframe_seconds=window_minutes * 60,
                volatility=0.0,
                recommendation="SKIP",
                reason="Insufficient price data",
            )

        # ── Calculate Core Metrics ─────────────────────────────

        start_price = klines[0]["open"]
        current_price = klines[-1]["close"]

        # Overall price change percentage
        price_change_pct = ((current_price - start_price) / start_price) * 100

        overall_direction = "UP" if price_change_pct > 0 else "DOWN" if price_change_pct < 0 else "FLAT"

        # ── Interval-to-interval returns ───────────────────────
        # This is the CORRECT way to measure direction consistency.
        # We compare each candle's CLOSE to the PREVIOUS candle's CLOSE
        # (not open-to-close within a single candle, which is misleading).
        #
        # Example: BTC opens at 80000, closes at 80105 (+0.131%)
        # But individual candles might be: red, red, green, red, green, green...
        # Using close[i] vs close[i-1] captures the ACTUAL tick-by-tick direction.
        interval_returns = []
        interval_directions = []
        for i in range(1, len(klines)):
            ret = ((klines[i]["close"] - klines[i-1]["close"]) / klines[i-1]["close"]) * 100
            interval_returns.append(ret)
            interval_directions.append("UP" if ret > 0 else "DOWN" if ret < 0 else "FLAT")

        # Direction consistency: what fraction of interval moves
        # agreed with the overall trend direction?
        if overall_direction != "FLAT" and len(interval_directions) > 0:
            consistent_count = sum(
                1 for d in interval_directions if d == overall_direction
            )
            direction_consistency = consistent_count / len(interval_directions)
        else:
            direction_consistency = 0.5

        volatility = statistics.stdev(interval_returns) if len(interval_returns) > 1 else 0.0

        # Recent acceleration: compare last 3 intervals vs first 3 intervals
        if len(interval_returns) >= 6:
            early_avg = statistics.mean(interval_returns[:3])
            recent_avg = statistics.mean(interval_returns[-3:])
            acceleration = recent_avg - early_avg
        else:
            acceleration = 0.0

        # Volume trend: is volume increasing in the trend direction?
        volumes = [k["quote_volume"] for k in klines]
        avg_volume = statistics.mean(volumes)
        recent_volumes = volumes[-3:]
        recent_avg_volume = statistics.mean(recent_volumes)
        volume_increasing = recent_avg_volume > avg_volume * 1.1

        # ── Micro-Trend (last 3 minutes) ───────────────────────
        # Is the recent price action confirming or reversing the trend?
        if len(klines) >= 3:
            recent_start = klines[-3]["open"]
            recent_change_pct = ((current_price - recent_start) / recent_start) * 100
            micro_trend = "UP" if recent_change_pct > 0 else "DOWN" if recent_change_pct < 0 else "FLAT"
            micro_confirms = micro_trend == overall_direction
        else:
            micro_confirms = True

        # ── Determine Signal Strength ──────────────────────────

        abs_change = abs(price_change_pct)
        min_momentum = self.config.MIN_MOMENTUM_PCT

        # NEW approach: Price change IS the signal.
        # Consistency modifies confidence, it doesn't block trades.
        #
        # In 15-min crypto markets, even a 0.03% directional move
        # is a real edge. The question isn't "is it consistent enough?"
        # but "is there enough of a directional bias to be tradeable?"
        #
        # Strength is based primarily on magnitude:
        if abs_change >= min_momentum * 5:
            strength = "STRONG"
        elif abs_change >= min_momentum * 2.5:
            strength = "MODERATE"
        elif abs_change >= min_momentum:
            strength = "WEAK"
        elif abs_change >= min_momentum * 0.5:
            strength = "SLIGHT"
        else:
            strength = "NONE"

        # ── Confidence Score ───────────────────────────────────
        # Scalping-optimized scoring: ANY directional move gets base confidence.
        # Consistency and other factors MODIFY the score up or down.
        confidence = 0.0

        # Base confidence from price change magnitude (0-30%)
        # Even 0.03% gets some confidence — it's a real directional bias
        confidence += min(abs_change / min_momentum * 0.15, 0.30)

        # Direction consistency modifier (can add or subtract)
        # 50% consistency = neutral (half the intervals agree)
        # Above 50% = confidence boost, below 50% = confidence penalty
        consistency_bonus = (direction_consistency - 0.40) * 0.30
        confidence += max(-0.10, min(consistency_bonus, 0.20))

        # Micro-trend confirmation (0-15%) — recent price action agrees
        confidence += (0.15 if micro_confirms else -0.05)

        # Acceleration bonus (0-10%)
        confidence += (0.10 if acceleration > 0 else 0.0)

        # Volume confirmation (0-10%)
        confidence += (0.10 if volume_increasing else 0.0)

        # Low volatility bonus (0-10%) — less noise = more reliable
        confidence += max(0, 0.10 - volatility * 1.5)

        confidence = max(0.0, min(confidence, 1.0))

        # Direction
        direction = overall_direction if strength != "NONE" else "FLAT"

        # ── Recommendation (Aggression-Aware) ──────────────────
        recommendation = "SKIP"
        reason = ""

        if direction in ("UP", "DOWN"):
            if strength == "STRONG":
                recommendation = f"BUY_{direction}"
                reason = (
                    f"STRONG {direction}: {abs_change:.3f}% move, "
                    f"{direction_consistency:.0%} consistent, "
                    f"micro={'confirming' if micro_confirms else 'diverging'}, "
                    f"accel={'yes' if acceleration > 0 else 'no'}, "
                    f"vol={volatility:.4f}%"
                )
            elif strength == "MODERATE":
                recommendation = f"BUY_{direction}"
                reason = (
                    f"MODERATE {direction}: {abs_change:.3f}% move, "
                    f"{direction_consistency:.0%} consistent"
                )
            elif strength == "WEAK":
                # WEAK signals: trade in aggressive+ modes
                if self.aggression in ("aggressive", "hyper"):
                    recommendation = f"BUY_{direction}"
                    reason = (
                        f"WEAK {direction} [AGGRESSIVE]: {abs_change:.3f}% move, "
                        f"{direction_consistency:.0%} consistent"
                    )
                else:
                    reason = (
                        f"WEAK {direction}: {abs_change:.3f}% move — "
                        f"skipped (need AGGRESSION=aggressive)"
                    )
            elif strength == "SLIGHT":
                # SLIGHT signals: only in hyper mode
                if self.aggression == "hyper":
                    recommendation = f"BUY_{direction}"
                    reason = (
                        f"SLIGHT {direction} [HYPER]: {abs_change:.3f}% move, "
                        f"{direction_consistency:.0%} consistent"
                    )
                else:
                    reason = (
                        f"SLIGHT {direction}: {abs_change:.3f}% move — "
                        f"skipped (need AGGRESSION=hyper)"
                    )
        else:
            reason = f"FLAT: {abs_change:.3f}% move, no directional edge"

        if recommendation == "SKIP" and strength != "NONE":
            reason += f" | need {min_momentum:.3f}%+ momentum"

        return MomentumSignal(
            symbol=symbol,
            direction=direction,
            strength=strength,
            confidence=confidence,
            price_change_pct=price_change_pct,
            direction_consistency=direction_consistency,
            current_price=current_price,
            start_price=start_price,
            timeframe_seconds=window_minutes * 60,
            volatility=volatility,
            recommendation=recommendation,
            reason=reason,
        )

    def get_multi_symbol_analysis(self, symbols: List[str]) -> Dict[str, MomentumSignal]:
        """Analyze momentum across multiple symbols."""
        results = {}
        for symbol in symbols:
            signal = self.analyze_momentum(symbol)
            results[symbol] = signal
        return results

    def find_best_opportunity(self, symbols: List[str]) -> Optional[Tuple[str, MomentumSignal]]:
        """
        Find the single best trading opportunity across all symbols.
        Returns (symbol, signal) tuple or None if no good opportunity.
        """
        results = self.get_multi_symbol_analysis(symbols)

        best = None
        best_confidence = 0.0

        for symbol, signal in results.items():
            if signal.recommendation != "SKIP" and signal.confidence > best_confidence:
                best = (symbol, signal)
                best_confidence = signal.confidence

        return best

    def find_all_opportunities(self, symbols: List[str]) -> List[Tuple[str, MomentumSignal]]:
        """
        Find ALL trading opportunities across all symbols.
        Returns list of (symbol, signal) tuples, sorted by confidence (best first).

        This is the key change for aggressive scalping — we don't just
        trade the single best opportunity, we trade ALL symbols with
        directional signals. More trades = more compounding.
        """
        results = self.get_multi_symbol_analysis(symbols)

        opportunities = []
        for symbol, signal in results.items():
            if signal.recommendation != "SKIP":
                if signal.confidence >= self.config.MIN_CONFIDENCE:
                    opportunities.append((symbol, signal))

        # Sort by confidence (best first)
        opportunities.sort(key=lambda x: x[1].confidence, reverse=True)

        return opportunities
