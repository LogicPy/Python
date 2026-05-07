"""
Kalshi EV Analyzer — The core intelligence module.

Calculates "fair value" probabilities and identifies +EV (Expected Value)
opportunities by comparing fair value to current market prices.

This is the brain that powers ALL strategies — they feed it data,
and it returns actionable trade recommendations.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

from .config import TradingConfig


# ── Data Structures ────────────────────────────────────────────────────

@dataclass
class FairValueEstimate:
    """An AI/analysis-driven estimate of a market's true probability."""
    ticker: str
    fair_probability: float        # 0.0 - 1.0 (our estimate)
    market_price: float            # 0.0 - 1.0 (Kalshi YES price)
    confidence: float              # 0.0 - 1.0 (how confident we are)
    reasoning: str                 # Why we think this
    data_sources: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def ev_pct(self) -> float:
        """Expected value as a percentage (positive = +EV)."""
        return (self.fair_probability - self.market_price) * 100

    @property
    def is_plus_ev(self) -> bool:
        """Whether this is a +EV opportunity."""
        return self.ev_pct > 0

    @property
    def is_strong_signal(self) -> bool:
        """Whether the EV exceeds the confidence-adjusted threshold."""
        min_ev_threshold = 10.0  # 10 cents minimum edge
        return self.is_plus_ev and self.ev_pct >= min_ev_threshold

    @property
    def direction(self) -> str:
        """Trade direction: 'yes' if undervalued, 'no' if overvalued."""
        return "yes" if self.fair_probability > self.market_price else "no"

    @property
    def edge_cents(self) -> float:
        """Edge in cents (same as ev_pct since market prices are in cents)."""
        return self.ev_pct

    def __repr__(self):
        arrow = "↑YES" if self.direction == "yes" else "↓NO"
        return (
            f"FairValue({self.ticker} | fair={self.fair_probability:.1%} "
            f"market={self.market_price:.1%} | EV={self.ev_pct:+.1f}¢ {arrow} "
            f"| conf={self.confidence:.0%})"
        )


@dataclass
class TradeRecommendation:
    """A validated trade recommendation from the EV analyzer."""
    ticker: str
    direction: str                 # "yes" or "no"
    fair_probability: float
    market_price: float
    ev_cents: float                # Expected edge in cents
    confidence: float              # 0-1
    strategy: str                  # Which strategy found this
    reasoning: str
    suggested_size: int            # Number of contracts
    risk_level: str = "medium"     # "low", "medium", "high"

    def to_dict(self) -> dict:
        return {
            "ticker": self.ticker,
            "direction": self.direction,
            "fair_probability": f"{self.fair_probability:.1%}",
            "market_price": f"{self.market_price:.1%}",
            "ev_cents": f"{self.ev_cents:+.1f}",
            "confidence": f"{self.confidence:.0%}",
            "strategy": self.strategy,
            "reasoning": self.reasoning,
            "suggested_size": self.suggested_size,
            "risk_level": self.risk_level,
        }


# ── Analyzer ──────────────────────────────────────────────────────────

class EVAnalyzer:
    """
    Expected Value Analyzer for Kalshi event contracts.

    Takes a fair value estimate (from any strategy — weather data,
    sentiment analysis, etc.) and compares it to the market price.

    If the gap (edge) exceeds the minimum threshold AND the confidence
    is high enough, it produces a TradeRecommendation.
    """

    def __init__(self, config=None):
        # Import here to avoid circular imports
        from .config import StrategyConfig
        self.config = config or StrategyConfig()
        self._history: List[FairValueEstimate] = []

    # ── Core Analysis ─────────────────────────────────────────────────

    def analyze(
        self,
        ticker: str,
        fair_probability: float,
        market_price: float,
        confidence: float,
        reasoning: str,
        strategy: str = "unknown",
        data_sources: Optional[List[str]] = None,
    ) -> TradeRecommendation:
        """
        Analyze a single market for +EV opportunity.

        Args:
            ticker: Kalshi market ticker
            fair_probability: Our estimated true probability (0.0-1.0)
            market_price: Current Kalshi YES price (0.0-1.0)
            confidence: How confident in our estimate (0.0-1.0)
            reasoning: Why we believe this fair value
            strategy: Name of the strategy that found this
            data_sources: List of data sources used

        Returns:
            TradeRecommendation (may have size=0 if no edge found)
        """
        estimate = FairValueEstimate(
            ticker=ticker,
            fair_probability=fair_probability,
            market_price=market_price,
            confidence=confidence,
            reasoning=reasoning,
            data_sources=data_sources or [],
        )

        self._history.append(estimate)

        # Calculate position size based on edge and confidence
        ev_cents = estimate.ev_pct
        direction = estimate.direction

        # Sizing: Kelly-inspired fractional sizing
        suggested_size = self._calculate_size(
            edge_pct=abs(ev_cents),
            confidence=confidence,
            direction=direction,
        )

        # Risk level
        risk_level = self._assess_risk(ev_cents, confidence, market_price)

        rec = TradeRecommendation(
            ticker=ticker,
            direction=direction,
            fair_probability=fair_probability,
            market_price=market_price,
            ev_cents=ev_cents,
            confidence=confidence,
            strategy=strategy,
            reasoning=reasoning,
            suggested_size=suggested_size,
            risk_level=risk_level,
        )

        # Log it
        if suggested_size > 0:
            print(f"[EV] +EV FOUND: {ticker} | {direction.upper()} @ {market_price:.0%} "
                  f"| fair={fair_probability:.0%} | edge={ev_cents:+.1f}¢ | "
                  f"conf={confidence:.0%} | size={suggested_size} | risk={risk_level}")
        else:
            print(f"[EV] No edge: {ticker} | fair={fair_probability:.0%} "
                  f"market={market_price:.0%} | edge={ev_cents:+.1f}¢")

        return rec

    def analyze_batch(
        self,
        estimates: List[Tuple[str, float, float, float, str, str]],
    ) -> List[TradeRecommendation]:
        """
        Analyze multiple markets at once.

        Args:
            estimates: List of (ticker, fair_prob, market_price, confidence,
                       reasoning, strategy) tuples

        Returns:
            List of TradeRecommendations, sorted by edge (best first)
        """
        recs = []
        for ticker, fair_prob, market_price, conf, reasoning, strategy in estimates:
            rec = self.analyze(
                ticker=ticker,
                fair_probability=fair_prob,
                market_price=market_price,
                confidence=conf,
                reasoning=reasoning,
                strategy=strategy,
            )
            recs.append(rec)

        # Sort by edge (best opportunities first)
        recs.sort(key=lambda r: abs(r.ev_cents), reverse=True)
        return recs

    # ── Position Sizing ────────────────────────────────────────────────

    def _calculate_size(
        self,
        edge_pct: float,
        confidence: float,
        direction: str,
    ) -> int:
        """
        Kelly-inspired position sizing.

        Size = confidence * edge * base_multiplier, capped by max_position.

        A confident analyst with a big edge should bet more.
        """
        min_ev_threshold = getattr(self.config, 'MIN_EV_THRESHOLD_CENTS', 10.0)  # e.g. 10¢

        # No edge = no trade
        if edge_pct < min_ev_threshold:
            return 0

        # Kelly fraction: edge / odds
        # For binary events: f* = (bp - q) / b
        # Simplified: we use confidence * edge as our sizing heuristic
        kelly_fraction = (edge_pct / 100) * confidence

        # Scale to contract count
        base_size = getattr(self.config, 'BASE_POSITION_SIZE', 5)  # e.g. 5 contracts
        max_size = getattr(self.config, 'MAX_POSITION_SIZE', 25)  # e.g. 25 contracts

        size = max(1, int(kelly_fraction * base_size * 10))
        size = min(size, max_size)

        return size

    def _assess_risk(
        self,
        ev_cents: float,
        confidence: float,
        market_price: float,
    ) -> str:
        """Assess risk level for a trade recommendation."""
        # Low risk: high confidence, large edge, not at extremes
        if confidence > 0.8 and abs(ev_cents) > 15 and 0.2 < market_price < 0.8:
            return "low"
        # High risk: low confidence, small edge, or extreme prices
        elif confidence < 0.5 or abs(ev_cents) < 12 or market_price < 0.1 or market_price > 0.9:
            return "high"
        else:
            return "medium"

    # ── History & Stats ────────────────────────────────────────────────

    def get_history(self, ticker: Optional[str] = None) -> List[FairValueEstimate]:
        """Get analysis history, optionally filtered by ticker."""
        if ticker:
            return [e for e in self._history if e.ticker == ticker]
        return self._history

    def get_stats(self) -> Dict[str, any]:
        """Get analysis statistics."""
        if not self._history:
            return {"total_analyses": 0}

        plus_ev = [e for e in self._history if e.is_plus_ev]
        strong = [e for e in self._history if e.is_strong_signal]

        return {
            "total_analyses": len(self._history),
            "plus_ev_count": len(plus_ev),
            "strong_signal_count": len(strong),
            "avg_edge_cents": sum(e.ev_pct for e in self._history) / len(self._history),
            "avg_confidence": sum(e.confidence for e in self._history) / len(self._history),
            "best_edge": max((e.ev_pct for e in self._history), default=0),
        }

    def clear_history(self):
        """Clear analysis history."""
        self._history.clear()

    def analyze_market(self, market) -> Optional[TradeRecommendation]:
        """Fallback analysis for markets without a dedicated strategy.

        Uses a simple mean-reversion heuristic: if the market price is
        far from 50¢, we assume slight reversion toward 50 and calculate
        a conservative fair value. Only flags opportunities with meaningful edge.
        """
        ticker = market.ticker
        market_price = market.yes_price or 0.50

        # Simple mean-reversion heuristic: fair value = midpoint between 0.50 and market price
        # This is intentionally conservative — dedicated strategies will always beat this
        distance_from_50 = market_price - 0.50
        fair_value = 0.50 + (distance_from_50 * 0.70)  # Pull 30% toward 0.50

        edge = abs(fair_value - market_price)

        # Only recommend if edge exceeds threshold
        min_ev_threshold = getattr(self.config, 'MIN_EV_THRESHOLD_CENTS', 10.0)
        if edge * 100 < min_ev_threshold:
            return None

        confidence = min(0.55, 0.40 + edge)  # Low confidence for heuristic
        direction = "YES" if fair_value > market_price else "NO"
        strategy = "heuristic_mean_reversion"

        return self.analyze(
            ticker=ticker,
            fair_probability=fair_value * 100,
            market_price=market_price,
            confidence=confidence,
            reasoning=f"Heuristic: market price {market_price:.2f} appears "
                      f"{'overbought' if direction == 'NO' else 'oversold'} — "
                      f"fair value estimated at {fair_value:.2f}",
            strategy=strategy,
        )