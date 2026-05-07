"""
Quantitative Probability Mode Strategy — The STATISTICAL DOMINANCE engine.

This is the highest-conviction trading strategy in the auto-trader suite.
It implements "QUANTITATIVE PROBABILITY MODE" — a philosophy of discovering
profitable instances using cold logical percentage calculation and identifying
the HIGHEST chance of success for duplicating funds at scale.

═══════════════════════════════════════════════════════════════════════════
QUANT PROBABILITY MODE vs SCALPER MODE — Key Differences
═══════════════════════════════════════════════════════════════════════════

SCALPER MODE (TradingConfig + momentum_detector):
  - Trades on ANY detectable momentum, even weak signals
  - Minimum confidence: 0.20 (trades WEAK+ signals)
  - Minimum EV edge: 10¢ (small edges are acceptable)
  - No minimum win probability gate
  - Philosophy: frequent small wins compound over time
  - Risk profile: many trades, small edge per trade, high volume

QUANT PROBABILITY MODE (this module):
  - ONLY trades where statistical edge is DOMINANT
  - Minimum confidence: 0.60 (trades STRONG signals only)
  - Minimum EV edge: 15¢ (ignores low-confidence noise)
  - Minimum win probability: >60% (statistical dominance required)
  - Compound threshold: edge * confidence > 0.10 (Safe-Bet filter)
  - Philosophy: systematic fund duplication via "Safe-Bet" chains
  - Risk profile: few trades, large edge per trade, high conviction

═══════════════════════════════════════════════════════════════════════════
Strategy Data Sources
═══════════════════════════════════════════════════════════════════════════

1. 15-minute BTC delta — For crypto markets, uses short-term price
   momentum with strict direction consistency filtering (>70% of
   indicators must agree).

2. Meteostat weather baselines — For weather markets, uses professional-
   grade station observations to find "mispriced" contracts where the
   market's emotional pricing lags behind the logical reality of data.

3. EVAnalyzer — The core EV calculation engine shared across all
   strategies, but with STRICTER thresholds applied here.

═══════════════════════════════════════════════════════════════════════════
Safe-Bet Chain Philosophy
═══════════════════════════════════════════════════════════════════════════

The goal is not just winning individual trades, but identifying sequences
of "Safe-Bet" opportunities that allow for systematic fund duplication
over long-term execution. Each trade in the chain must:

  1. Have >60% probability of success (statistical dominance)
  2. Represent a positive mathematical edge (>15¢ EV)
  3. Pass the compound threshold (edge * confidence > 0.10)
  4. Not be classified as "high" risk

This compound multiplication approach means we skip many trades that
the scalper would take, but the ones we DO take have a much higher
probability of success — enabling systematic fund growth rather than
grinding for small edges.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional

from .config import QuantitativeProbabilityConfig
from .ev_analyzer import EVAnalyzer, TradeRecommendation, FairValueEstimate
from .market_scanner import MarketInfo

logger = logging.getLogger("QuantProbability")


class QuantitativeProbabilityStrategy:
    """
    Quantitative Probability Mode Strategy for Kalshi auto-trading.

    Discovers profitable instances using cold logical percentage calculation
    and identifies the HIGHEST chance of success for duplicating funds at
    scale. Only recommends trades where:

      - Fair probability > 60% (MIN_WIN_PROBABILITY)
      - EV edge > 15¢ (MIN_EV_EDGE_CENTS — higher than scalper's 10¢)
      - Confidence >= 0.60 (MIN_CONFIDENCE — much higher than scalper's 0.20)
      - Edge * confidence > 0.10 (COMPOUND_THRESHOLD — Safe-Bet filter)

    This strategy is the ANTITHESIS of the scalper: fewer trades, higher
    conviction, systematic fund duplication via "Safe-Bet" chains.

    Usage:
        config = QuantitativeProbabilityConfig()
        strategy = QuantitativeProbabilityStrategy(config)

        # For weather/economics markets
        recommendation = strategy.analyze_market(market_info)

        # For crypto markets with 15-min BTC delta
        recommendation = strategy.analyze_crypto_signal(
            symbol="BTC",
            signal_data=momentum_data,
            market_info=kalshi_data,
        )

        # Filter a batch of recommendations into Safe-Bet chains
        safe_bets = strategy.filter_safe_bet_chain(all_recommendations)
    """

    # ── System Prompt ────────────────────────────────────────────────────
    # This is the full trading philosophy that guides all decisions in
    # this strategy module. It can be used as a system prompt for LLM-
    # enhanced analysis or as a reference for understanding the strategy's
    # decision-making framework.

    SYSTEM_PROMPT: str = (
        "TRADING STRATEGY: QUANTITATIVE PROBABILITY MODE\n"
        "\n"
        "Objective: Discover profitable instances using cold logical percentage "
        "calculation and identify the HIGHEST chance of success for duplicating "
        "funds at scale.\n"
        "\n"
        "Key Philosophy:\n"
        "1. Statistical Dominance: Prioritize trades where the calculated "
        "probability of success is >60%, moving beyond \"any detectable momentum.\"\n"
        "2. Expected Value (EV) Focus: Every trade must represent a positive "
        "mathematical edge. Ignore \"low-confidence\" noise to protect capital "
        "for high-conviction windows.\n"
        "3. Scalable Replication: Use 15-minute BTC delta and Meteostat weather "
        "baselines to find \"mispriced\" contracts where the market's emotional "
        "pricing lags behind the logical reality of the data.\n"
        "4. Compound Multiplication: The goal is not just winning, but identifying "
        "\"Safe-Bet\" chains that allow for systematic fund duplication over "
        "long-term execution."
    )

    # ── Initialization ──────────────────────────────────────────────────

    def __init__(self, config: Optional[QuantitativeProbabilityConfig] = None) -> None:
        """
        Initialize the Quantitative Probability Mode strategy.

        Args:
            config: Strategy configuration. If None, uses defaults from
                    QuantitativeProbabilityConfig (all thresholds at their
                    strictest recommended values).

        The EVAnalyzer is created internally and shared across all analysis
        methods. The Quant Prob strategy applies STRICTER thresholds on top
        of the base EVAnalyzer — the analyzer does the math, and this
        strategy filters the results through the quant probability lens.
        """
        self.config = config or QuantitativeProbabilityConfig()
        self.ev_analyzer = EVAnalyzer()
        self._active_since: datetime = datetime.now(timezone.utc)
        self._total_analyzed: int = 0
        self._total_recommended: int = 0
        self._total_filtered: int = 0

        logger.info(
            "[QuantProb] Strategy initialized | "
            "min_win_prob=%.0f%% | min_ev_edge=%.0f¢ | "
            "min_confidence=%.0f%% | compound_threshold=%.2f | "
            "max_safe_bets=%d | mispricing_threshold=%.2f | "
            "direction_consistency_min=%.0f%%",
            self.config.MIN_WIN_PROBABILITY * 100,
            self.config.MIN_EV_EDGE_CENTS,
            self.config.MIN_CONFIDENCE * 100,
            self.config.COMPOUND_THRESHOLD,
            self.config.MAX_SAFE_BET_CHAINS,
            self.config.MISPRICING_THRESHOLD,
            self.config.DIRECTION_CONSISTENCY_MIN * 100,
        )

    # ── Main Analysis: Weather / Economics Markets ──────────────────────

    def analyze_market(self, market: MarketInfo) -> Optional[TradeRecommendation]:
        """
        Analyze a single market for Quantitative Probability Mode opportunities.

        This is the main entry point for weather, economics, and other
        non-crypto markets. It uses the existing EVAnalyzer.analyze() but
        applies STRICTER thresholds that are the hallmark of Quant Prob mode.

        The filtering pipeline:
          1. Run EVAnalyzer to get base fair value estimate and recommendation
          2. Filter: fair_probability must exceed MIN_WIN_PROBABILITY (60%)
          3. Filter: EV edge must exceed MIN_EV_EDGE_CENTS (15¢)
          4. Filter: confidence must meet MIN_CONFIDENCE (0.60)
          5. Filter: edge * confidence must exceed COMPOUND_THRESHOLD (0.10)
          6. Tag the recommendation with strategy="quant_probability"

        Args:
            market: MarketInfo object from the market scanner, containing
                    ticker, title, yes_price, category, and other metadata.

        Returns:
            TradeRecommendation if all quant probability filters pass,
            None if the opportunity doesn't meet the strict thresholds.

        Example:
            >>> from .market_scanner import MarketInfo
            >>> market = MarketInfo(
            ...     ticker="KXHIGHNY-26MAR15",
            ...     title="NYC high temp above 55°F on Mar 15",
            ...     category="weather",
            ...     yes_price=0.35,
            ... )
            >>> rec = strategy.analyze_market(market)
            >>> if rec:
            ...     print(f"QUANT TRADE: {rec.ticker} {rec.direction} "
            ...           f"edge={rec.ev_cents:+.1f}¢ conf={rec.confidence:.0%}")
        """
        self._total_analyzed += 1

        try:
            # ── Step 1: Run base EV analysis ──────────────────────────
            # The EVAnalyzer.analyze_market() method uses a mean-reversion
            # heuristic for markets without a dedicated strategy. For
            # weather markets, the WeatherStrategy should have already
            # computed a fair value — this method applies the QUANT
            # PROBABILITY filters on top.
            base_rec = self.ev_analyzer.analyze_market(market)

            if base_rec is None:
                logger.debug(
                    "[QuantProb] No base recommendation for %s — "
                    "EVAnalyzer found no edge",
                    market.ticker,
                )
                return None

            # ── Step 2: Apply Quant Probability strict filters ─────────
            # These filters are what separate Quant Prob from Scalper mode.
            # Scalper would take the base_rec as-is if it has any positive
            # edge. Quant Prob requires DOMINANT statistical edge.

            # Filter 2a: Fair probability must exceed MIN_WIN_PROBABILITY
            if base_rec.fair_probability < self.config.MIN_WIN_PROBABILITY:
                logger.info(
                    "[QuantProb] FILTERED %s — fair_prob %.1f%% < "
                    "min_win_prob %.1f%% | (scalper would trade this)",
                    market.ticker,
                    base_rec.fair_probability * 100,
                    self.config.MIN_WIN_PROBABILITY * 100,
                )
                self._total_filtered += 1
                return None

            # Filter 2b: EV edge must exceed MIN_EV_EDGE_CENTS
            if abs(base_rec.ev_cents) < self.config.MIN_EV_EDGE_CENTS:
                logger.info(
                    "[QuantProb] FILTERED %s — ev_edge %.1f¢ < "
                    "min_ev_edge %.1f¢ | (scalper would trade this with "
                    "10¢ threshold)",
                    market.ticker,
                    abs(base_rec.ev_cents),
                    self.config.MIN_EV_EDGE_CENTS,
                )
                self._total_filtered += 1
                return None

            # Filter 2c: Confidence must meet MIN_CONFIDENCE
            if base_rec.confidence < self.config.MIN_CONFIDENCE:
                logger.info(
                    "[QuantProb] FILTERED %s — confidence %.0f%% < "
                    "min_confidence %.0f%% | (scalper would trade this "
                    "with 20%% threshold)",
                    market.ticker,
                    base_rec.confidence * 100,
                    self.config.MIN_CONFIDENCE * 100,
                )
                self._total_filtered += 1
                return None

            # Filter 2d: Compound threshold — edge * confidence > threshold
            # This is the "Safe-Bet Chain" gate: it ensures that only
            # trades with BOTH high edge AND high confidence pass.
            # A trade with 20¢ edge but 30% confidence would fail here
            # (0.20 * 0.30 = 0.06 < 0.10), while a trade with 15¢ edge
            # and 80% confidence would pass (0.15 * 0.80 = 0.12 > 0.10).
            edge_fraction = abs(base_rec.ev_cents) / 100.0
            compound_score = edge_fraction * base_rec.confidence

            if compound_score < self.config.COMPOUND_THRESHOLD:
                logger.info(
                    "[QuantProb] FILTERED %s — compound_score %.3f < "
                    "threshold %.3f (edge=%.1f¢ × conf=%.0f%%) | "
                    "fails Safe-Bet chain gate",
                    market.ticker,
                    compound_score,
                    self.config.COMPOUND_THRESHOLD,
                    abs(base_rec.ev_cents),
                    base_rec.confidence * 100,
                )
                self._total_filtered += 1
                return None

            # ── Step 3: Tag and return ────────────────────────────────
            # Override the strategy tag to identify this as a Quant
            # Probability recommendation (not the base strategy's tag).
            base_rec.strategy = "quant_probability"

            self._total_recommended += 1

            logger.info(
                "[QuantProb] ✓ RECOMMENDED %s | %s | "
                "fair=%.1f%% market=%.1f%% edge=%+.1f¢ | "
                "conf=%.0f%% compound=%.3f | risk=%s | size=%d",
                base_rec.ticker,
                base_rec.direction.upper(),
                base_rec.fair_probability * 100,
                base_rec.market_price * 100,
                base_rec.ev_cents,
                base_rec.confidence * 100,
                compound_score,
                base_rec.risk_level,
                base_rec.suggested_size,
            )

            return base_rec

        except Exception as e:
            logger.error(
                "[QuantProb] Error analyzing market %s: %s",
                market.ticker,
                e,
                exc_info=True,
            )
            return None

    # ── Crypto Signal Analysis ──────────────────────────────────────────

    def analyze_crypto_signal(
        self,
        symbol: str,
        signal_data: dict,
        market_info: dict,
    ) -> Optional[TradeRecommendation]:
        """
        Analyze a crypto market signal using Quantitative Probability Mode.

        Specifically designed for 15-minute BTC (and other crypto) delta
        markets on Kalshi. Applies the quantitative filter to momentum
        signals and identifies "mispriced" contracts where the market's
        emotional pricing lags behind the logical reality of the data.

        Filtering Pipeline:
          1. Validate direction consistency > DIRECTION_CONSISTENCY_MIN (0.70)
          2. Validate price change > 0.05% (minimum meaningful move)
          3. Calculate mispricing score = abs(fair_prob - market_price) × confidence
          4. Filter: mispricing_score must exceed MISPRICING_THRESHOLD (0.08)
          5. Scale position size UP for high-conviction trades:
             - confidence >= 0.75: 1.5x base size
             - confidence >= 0.85: 2.0x base size
          6. Tag with strategy="quant_probability"

        Args:
            symbol: Crypto symbol (e.g., "BTC", "ETH", "SOL").
            signal_data: Dict from the momentum detector containing:
                - "direction": "up" or "down"
                - "direction_consistency": float 0-1 (% of indicators agreeing)
                - "price_change_pct": float (% price change in window)
                - "confidence": float 0-1 (signal strength)
                - "momentum_score": float (composite momentum reading)
                - "reasoning": str (why the signal fired)
            market_info: Dict containing Kalshi market data:
                - "ticker": str (Kalshi market ticker)
                - "yes_price": float (current YES price 0.0-1.0)
                - "fair_probability": float (our estimated true probability)
                - "confidence": float 0-1 (confidence in fair value estimate)

        Returns:
            TradeRecommendation if all quant probability filters pass,
            None if the opportunity doesn't meet the strict thresholds.

        Example:
            >>> signal = {
            ...     "direction": "up",
            ...     "direction_consistency": 0.85,
            ...     "price_change_pct": 0.12,
            ...     "confidence": 0.78,
            ...     "momentum_score": 0.65,
            ...     "reasoning": "Strong 15min uptrend with 85% indicator agreement",
            ... }
            >>> market = {
            ...     "ticker": "KXBTC15M-26MAR151400",
            ...     "yes_price": 0.40,
            ...     "fair_probability": 0.68,
            ...     "confidence": 0.75,
            ... }
            >>> rec = strategy.analyze_crypto_signal("BTC", signal, market)
        """
        self._total_analyzed += 1

        try:
            # ── Validate inputs ───────────────────────────────────────
            direction_consistency = signal_data.get("direction_consistency", 0.0)
            price_change_pct = signal_data.get("price_change_pct", 0.0)
            signal_confidence = signal_data.get("confidence", 0.0)
            direction = signal_data.get("direction", "neutral")

            ticker = market_info.get("ticker", f"{symbol}_UNKNOWN")
            yes_price = market_info.get("yes_price", 0.5)
            fair_probability = market_info.get("fair_probability", 0.5)
            market_confidence = market_info.get("confidence", 0.5)

            # Use the LOWER of signal confidence and market confidence
            # as the overall confidence — both must be strong.
            overall_confidence = min(signal_confidence, market_confidence)

            # ── Filter 1: Direction consistency ───────────────────────
            # The quant probability mode requires that the majority of
            # indicators agree on the direction. This filters out "noisy"
            # signals where indicators are split.
            if direction_consistency < self.config.DIRECTION_CONSISTENCY_MIN:
                logger.info(
                    "[QuantProb] FILTERED %s — direction_consistency %.0f%% < "
                    "min %.0f%% | signal too noisy for Quant Prob mode",
                    ticker,
                    direction_consistency * 100,
                    self.config.DIRECTION_CONSISTENCY_MIN * 100,
                )
                self._total_filtered += 1
                return None

            # ── Filter 2: Minimum price change ────────────────────────
            # A price change < 0.05% is too small to create a meaningful
            # mispricing. Scalper might trade it, but Quant Prob skips it.
            if abs(price_change_pct) < 0.05:
                logger.info(
                    "[QuantProb] FILTERED %s — price_change %.3f%% < "
                    "min 0.05%% | move too small for Quant Prob mode",
                    ticker,
                    price_change_pct,
                )
                self._total_filtered += 1
                return None

            # ── Filter 3: Win probability gate ────────────────────────
            # The fair probability must indicate a >60% chance of winning.
            if fair_probability < self.config.MIN_WIN_PROBABILITY:
                logger.info(
                    "[QuantProb] FILTERED %s — fair_prob %.1f%% < "
                    "min_win_prob %.1f%%",
                    ticker,
                    fair_probability * 100,
                    self.config.MIN_WIN_PROBABILITY * 100,
                )
                self._total_filtered += 1
                return None

            # ── Filter 4: Confidence gate ─────────────────────────────
            if overall_confidence < self.config.MIN_CONFIDENCE:
                logger.info(
                    "[QuantProb] FILTERED %s — overall_confidence %.0f%% < "
                    "min %.0f%% (signal_conf=%.0f%%, market_conf=%.0f%%)",
                    ticker,
                    overall_confidence * 100,
                    self.config.MIN_CONFIDENCE * 100,
                    signal_confidence * 100,
                    market_confidence * 100,
                )
                self._total_filtered += 1
                return None

            # ── Filter 5: Mispricing score ────────────────────────────
            # The mispricing score quantifies how "wrong" the market is,
            # weighted by our confidence in that assessment.
            # High mispricing + high confidence = strong Quant Prob trade.
            mispricing_score = abs(fair_probability - yes_price) * overall_confidence

            if mispricing_score < self.config.MISPRICING_THRESHOLD:
                logger.info(
                    "[QuantProb] FILTERED %s — mispricing_score %.3f < "
                    "threshold %.3f (|fair=%.1f%% - market=%.1f%%| × "
                    "conf=%.0f%%)",
                    ticker,
                    mispricing_score,
                    self.config.MISPRICING_THRESHOLD,
                    fair_probability * 100,
                    yes_price * 100,
                    overall_confidence * 100,
                )
                self._total_filtered += 1
                return None

            # ── Filter 6: Compound threshold (Safe-Bet gate) ──────────
            ev_edge_cents = (fair_probability - yes_price) * 100
            edge_fraction = abs(ev_edge_cents) / 100.0
            compound_score = edge_fraction * overall_confidence

            if compound_score < self.config.COMPOUND_THRESHOLD:
                logger.info(
                    "[QuantProb] FILTERED %s — compound_score %.3f < "
                    "threshold %.3f | fails Safe-Bet chain gate",
                    ticker,
                    compound_score,
                    self.config.COMPOUND_THRESHOLD,
                )
                self._total_filtered += 1
                return None

            # ── Calculate position size with conviction scaling ───────
            # Quant Prob mode SCALES UP position sizes for high-conviction
            # trades. This is the opposite of conservative sizing — when
            # we have dominant statistical edge, we press the advantage.
            base_size = self._get_base_position_size()
            position_scale = 1.0

            if overall_confidence >= self.config.VERY_HIGH_CONV_THRESHOLD:
                position_scale = self.config.POSITION_SCALE_VERY_HIGH_CONV
                scale_label = "2.0x (very high conv)"
            elif overall_confidence >= self.config.HIGH_CONV_THRESHOLD:
                position_scale = self.config.POSITION_SCALE_HIGH_CONV
                scale_label = "1.5x (high conv)"
            else:
                scale_label = "1.0x (base)"

            suggested_size = max(1, int(base_size * position_scale))

            # ── Determine trade direction ─────────────────────────────
            if fair_probability > yes_price:
                trade_direction = "yes"
            else:
                trade_direction = "no"

            # ── Build recommendation ──────────────────────────────────
            reasoning_parts = [
                f"Quant Prob Mode: {symbol} 15-min delta",
                f"Direction: {direction} (consistency={direction_consistency:.0%})",
                f"Price change: {price_change_pct:+.3f}%",
                f"Mispricing: {mispricing_score:.3f} (>{self.config.MISPRICING_THRESHOLD})",
                f"Compound score: {compound_score:.3f} (>{self.config.COMPOUND_THRESHOLD})",
                f"Position scale: {scale_label}",
                signal_data.get("reasoning", ""),
            ]
            reasoning = " | ".join(r for r in reasoning_parts if r)

            # Assess risk level based on quant probability criteria
            risk_level = self._assess_quant_risk(
                ev_cents=ev_edge_cents,
                confidence=overall_confidence,
                market_price=yes_price,
                direction_consistency=direction_consistency,
            )

            recommendation = TradeRecommendation(
                ticker=ticker,
                direction=trade_direction,
                fair_probability=fair_probability,
                market_price=yes_price,
                ev_cents=ev_edge_cents,
                confidence=overall_confidence,
                strategy="quant_probability",
                reasoning=reasoning,
                suggested_size=suggested_size,
                risk_level=risk_level,
            )

            self._total_recommended += 1

            logger.info(
                "[QuantProb] ✓ CRYPTO RECOMMENDED %s | %s | "
                "fair=%.1f%% market=%.1f%% edge=%+.1f¢ | "
                "conf=%.0f%% mispricing=%.3f compound=%.3f | "
                "risk=%s | size=%d (%s)",
                ticker,
                trade_direction.upper(),
                fair_probability * 100,
                yes_price * 100,
                ev_edge_cents,
                overall_confidence * 100,
                mispricing_score,
                compound_score,
                risk_level,
                suggested_size,
                scale_label,
            )

            return recommendation

        except Exception as e:
            logger.error(
                "[QuantProb] Error analyzing crypto signal %s: %s",
                symbol,
                e,
                exc_info=True,
            )
            return None

    # ── Safe-Bet Chain Filter ───────────────────────────────────────────

    def filter_safe_bet_chain(
        self,
        recommendations: List[TradeRecommendation],
    ) -> List[TradeRecommendation]:
        """
        Filter and rank trade recommendations into a "Safe-Bet Chain".

        The "Compound Multiplication" filter — this method takes a list of
        trade recommendations and identifies the SAFEST, highest-quality
        opportunities for systematic fund duplication.

        Filtering Pipeline:
          1. Remove all "high" risk recommendations (only low/medium pass)
          2. Calculate "compound_score" for each remaining recommendation:
             compound_score = ev_cents * confidence * (1 / risk_factor)
             where risk_factor = 3.0 for "high", 2.0 for "medium", 1.0 for "low"
          3. Rank by compound_score (descending)
          4. Return only the top N (MAX_SAFE_BET_CHAINS) opportunities

        The compound_score rewards trades that have:
          - Large EV edge (more cents of edge = higher score)
          - High confidence (more certain = higher score)
          - Low risk (safer = higher score via 1/risk_factor)

        This ensures that the Safe-Bet Chain consists of the absolute best
        opportunities — not just the highest edge, but the highest quality
        combination of edge, confidence, and safety.

        Args:
            recommendations: List of TradeRecommendation objects to filter.
                             These may come from analyze_market() or
                             analyze_crypto_signal().

        Returns:
            List of up to MAX_SAFE_BET_CHAINS TradeRecommendation objects,
            sorted by compound_score (best first). May be empty if no
            recommendations pass the filter.

        Example:
            >>> recs = [rec1, rec2, rec3, rec4, rec5]
            >>> safe_bets = strategy.filter_safe_bet_chain(recs)
            >>> for bet in safe_bets:
            ...     print(f"Safe-Bet: {bet.ticker} score={score:.3f}")
        """
        if not recommendations:
            logger.info("[QuantProb] No recommendations to filter for Safe-Bet chain")
            return []

        # Risk factor mapping: lower risk = higher multiplier
        risk_factors: Dict[str, float] = {
            "low": 1.0,
            "medium": 2.0,
            "high": 3.0,
        }

        safe_bets: List[TradeRecommendation] = []
        filtered_reasons: List[str] = []

        for rec in recommendations:
            # ── Filter: Remove high-risk trades ───────────────────────
            # Safe-Bet chains only include low/medium risk trades.
            # High risk trades, even with large edge, undermine the
            # "systematic fund duplication" goal.
            if rec.risk_level == "high":
                reason = (
                    f"{rec.ticker}: risk_level=high (ev={rec.ev_cents:+.1f}¢, "
                    f"conf={rec.confidence:.0%})"
                )
                filtered_reasons.append(reason)
                logger.info(
                    "[QuantProb] Safe-Bet FILTERED %s — risk_level=high | "
                    "ev=%+.1f¢ conf=%.0f%% | high risk excluded from chain",
                    rec.ticker,
                    rec.ev_cents,
                    rec.confidence * 100,
                )
                continue

            # ── Filter: Zero-size trades ──────────────────────────────
            if rec.suggested_size <= 0:
                reason = (
                    f"{rec.ticker}: suggested_size=0 (no position)"
                )
                filtered_reasons.append(reason)
                logger.debug(
                    "[QuantProb] Safe-Bet FILTERED %s — suggested_size=0",
                    rec.ticker,
                )
                continue

            safe_bets.append(rec)

        # ── Calculate compound scores and rank ────────────────────────
        def compound_score(rec: TradeRecommendation) -> float:
            """Calculate the compound quality score for a recommendation."""
            risk_factor = risk_factors.get(rec.risk_level, 2.0)
            return abs(rec.ev_cents) / 100.0 * rec.confidence * (1.0 / risk_factor)

        safe_bets.sort(key=compound_score, reverse=True)

        # ── Log the ranking ──────────────────────────────────────────
        if safe_bets:
            logger.info(
                "[QuantProb] Safe-Bet chain ranking (%d candidates):",
                len(safe_bets),
            )
            for i, rec in enumerate(safe_bets):
                score = compound_score(rec)
                logger.info(
                    "  #%d: %s | %s | ev=%+.1f¢ conf=%.0f%% "
                    "risk=%s compound_score=%.4f",
                    i + 1,
                    rec.ticker,
                    rec.direction.upper(),
                    rec.ev_cents,
                    rec.confidence * 100,
                    rec.risk_level,
                    score,
                )

        # ── Trim to MAX_SAFE_BET_CHAINS ──────────────────────────────
        max_chains = self.config.MAX_SAFE_BET_CHAINS
        if len(safe_bets) > max_chains:
            trimmed = safe_bets[max_chains:]
            for rec in trimmed:
                # Log trimmed items that didn't make the top N
                logger.info(
                    "[QuantProb] Safe-Bet TRIMMED %s — compound_score=%.4f "
                    "ranked #%d+ (max_chain=%d)",
                    rec.ticker,
                    compound_score(rec),
                    safe_bets.index(rec) + 1,
                    max_chains,
                )
            safe_bets = safe_bets[:max_chains]

        # ── Summary log ──────────────────────────────────────────────
        logger.info(
            "[QuantProb] Safe-Bet chain: %d input → %d filtered → %d output "
            "(max=%d)",
            len(recommendations),
            len(filtered_reasons),
            len(safe_bets),
            max_chains,
        )

        if filtered_reasons:
            logger.debug(
                "[QuantProb] Filtered reasons:\n  %s",
                "\n  ".join(filtered_reasons),
            )

        return safe_bets

    # ── Strategy Summary ────────────────────────────────────────────────

    def get_strategy_summary(self) -> dict:
        """
        Get a summary of the current Quantitative Probability Mode strategy state.

        Returns a dict containing:
          - mode: Strategy name
          - philosophy: Core trading philosophy
          - thresholds: All active threshold values
          - active_since: ISO timestamp of strategy initialization
          - stats: Analysis statistics (total analyzed, recommended, filtered)
          - difference_from_scalper: Key differences from scalper mode

        Returns:
            Dict with strategy summary information.

        Example:
            >>> summary = strategy.get_strategy_summary()
            >>> print(f"Mode: {summary['mode']}")
            >>> print(f"Active since: {summary['active_since']}")
            >>> print(f"Recommendations: {summary['stats']['total_recommended']}")
        """
        return {
            "mode": "quant_probability",
            "philosophy": self.SYSTEM_PROMPT,
            "thresholds": {
                "min_win_probability": self.config.MIN_WIN_PROBABILITY,
                "min_ev_edge_cents": self.config.MIN_EV_EDGE_CENTS,
                "min_confidence": self.config.MIN_CONFIDENCE,
                "compound_threshold": self.config.COMPOUND_THRESHOLD,
                "max_safe_bet_chains": self.config.MAX_SAFE_BET_CHAINS,
                "mispricing_threshold": self.config.MISPRICING_THRESHOLD,
                "direction_consistency_min": self.config.DIRECTION_CONSISTENCY_MIN,
                "position_scale_high_conv": self.config.POSITION_SCALE_HIGH_CONV,
                "position_scale_very_high_conv": self.config.POSITION_SCALE_VERY_HIGH_CONV,
                "high_conv_threshold": self.config.HIGH_CONV_THRESHOLD,
                "very_high_conv_threshold": self.config.VERY_HIGH_CONV_THRESHOLD,
            },
            "active_since": self._active_since.isoformat(),
            "stats": {
                "total_analyzed": self._total_analyzed,
                "total_recommended": self._total_recommended,
                "total_filtered": self._total_filtered,
                "recommendation_rate": (
                    self._total_recommended / max(1, self._total_analyzed)
                ),
                "filter_rate": (
                    self._total_filtered / max(1, self._total_analyzed)
                ),
            },
            "difference_from_scalper": {
                "min_confidence": "0.60 vs scalper's 0.20 (3x stricter)",
                "min_ev_edge_cents": "15¢ vs scalper's 10¢ (50% higher)",
                "min_win_probability": "0.60 vs scalper's none (new gate)",
                "compound_threshold": "0.10 (unique to Quant Prob — no scalper equivalent)",
                "position_sizing": "1.5x-2x scaling for high conviction vs scalper's fixed size",
                "risk_tolerance": "Only low/medium risk vs scalper's any risk",
                "philosophy": "Statistical dominance & fund duplication vs frequent small wins",
            },
        }

    # ── Private Helpers ─────────────────────────────────────────────────

    def _get_base_position_size(self) -> int:
        """
        Get the base position size from the EVAnalyzer's config.

        Falls back to 5 contracts if the config doesn't specify a base size.
        """
        try:
            return getattr(
                self.ev_analyzer.config,
                "BASE_POSITION_SIZE",
                5,
            )
        except AttributeError:
            return 5

    def _assess_quant_risk(
        self,
        ev_cents: float,
        confidence: float,
        market_price: float,
        direction_consistency: float,
    ) -> str:
        """
        Assess risk level using Quant Probability Mode criteria.

        This is STRICTER than the base EVAnalyzer's risk assessment:
          - "low": high confidence (>0.80), large edge (>15¢), strong
            direction consistency (>0.80), and market price not at extremes
          - "high": low confidence (<0.65), small edge (<12¢), weak
            direction consistency (<0.60), or extreme market prices
          - "medium": everything else

        Args:
            ev_cents: Expected value edge in cents.
            confidence: Overall confidence in the fair value estimate (0-1).
            market_price: Current market YES price (0-1).
            direction_consistency: Agreement level of directional indicators (0-1).

        Returns:
            Risk level string: "low", "medium", or "high".
        """
        # Low risk: dominant edge across all dimensions
        if (
            confidence > 0.80
            and abs(ev_cents) > 15
            and direction_consistency > 0.80
            and 0.2 < market_price < 0.8
        ):
            return "low"

        # High risk: any dimension is weak
        if (
            confidence < 0.65
            or abs(ev_cents) < 12
            or direction_consistency < 0.60
            or market_price < 0.10
            or market_price > 0.90
        ):
            return "high"

        return "medium"
