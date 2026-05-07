"""
Kalshi Weather Trading Bot — AI-Enhanced Auto-Trading System.

A dedicated trading bot for Kalshi weather/climate markets that mirrors
the CryptoScalperBot pattern but is adapted for weather tickers:

Key Differences from Crypto Bot:
  - No 15-minute windows (weather markets span days/weeks)
  - Uses NWS/Open-Meteo forecasts instead of Binance price data
  - EV-based entry decisions instead of momentum-based
  - AI-enhanced analysis for probability estimation
  - Different scheduler (periodic scan, not window-aligned)

Strategy:
  1. Scan Kalshi climate/weather category for active markets
  2. Fetch weather forecast data (NWS + Open-Meteo)
  3. Calculate fair probability from forecasts + historical data
  4. Use AI (OpenRouter) to refine probability estimates
  5. Execute trades where EV edge exceeds minimum threshold
  6. Monitor and resolve positions as markets settle
"""

import json
import time
import threading
from datetime import datetime, timezone, date
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
from kalshi_python import KalshiClient as SDKClient, MarketsApi

from .config import (
    KalshiConfig, TradingConfig, WeatherTradingConfig,
    StrategyConfig, OpenRouterConfig, QuantitativeProbabilityConfig,
    POSITION_FILE, TRADE_LOG_DIR
)
from .kalshi_client import KalshiClient
from .market_scanner import MarketScanner, MarketInfo
from .weather_strategy import WeatherStrategy, is_actual_weather_market
from .ev_analyzer import EVAnalyzer, TradeRecommendation
from .ai_analyzer import AIAnalyzer
from .rate_limiter import get_kalshi_limiter, get_weather_limiter


@dataclass
class WeatherTrade:
    """Record of a weather market trade."""
    trade_id: str
    timestamp: str
    ticker: str
    title: str
    direction: str        # "yes" or "no"
    side: str             # "yes" or "no"
    contracts: int
    entry_price: float    # Price per contract in dollars
    cost_dollars: float
    paper_trade: bool
    fair_probability: float
    market_price: float
    ev_cents: float
    confidence: float
    reasoning: str
    strategy: str = "weather"
    outcome: Optional[str] = None  # "WIN", "LOSS", "PENDING"
    payout_dollars: Optional[float] = None
    profit_dollars: Optional[float] = None


class WeatherTradingBot:
    """
    AI-Enhanced Weather Trading Bot for Kalshi climate markets.

    Operates on a periodic scan cycle:
    - Every N minutes, scan all weather markets
    - Analyze each with weather data + AI
    - Execute trades with +EV edge above threshold
    - Resolve settled positions
    """

    def __init__(self, paper_mode: Optional[bool] = None, trading_mode: Optional[str] = None):
        # Configuration
        self.kalshi_config = KalshiConfig()
        self.trading_config = TradingConfig()
        self.weather_config = WeatherTradingConfig()
        self.strategy_config = StrategyConfig()
        self.ai_config = OpenRouterConfig()
        self.quant_config = QuantitativeProbabilityConfig()

        # Override paper mode if specified
        if paper_mode is not None:
            self.trading_config.PAPER_TRADING = paper_mode

        # Override trading mode if specified (fixes CLI mode toggle)
        if trading_mode is not None:
            self.trading_config.TRADING_MODE = trading_mode.lower()

        # Components
        self.client = KalshiClient(self.kalshi_config)
        self.scanner = MarketScanner(self.kalshi_config)
        self.weather_strategy = WeatherStrategy()
        self.ev_analyzer = EVAnalyzer(self.strategy_config)
        self.ai = AIAnalyzer(self.ai_config)

        # Quant Probability strategy (loaded when TRADING_MODE=quant_probability)
        self._quant_strategy = None
        self._init_quant_strategy()

        # State
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._trades: List[WeatherTrade] = []
        self._active_positions: Dict[str, WeatherTrade] = {}
        self._trade_counter = 0
        self._last_scan_results: List[TradeRecommendation] = []
        self._scan_count = 0
        self._category_status: Dict[str, Any] = {}

        # Load existing state
        self._load_state()

    def _init_quant_strategy(self):
        """Initialize or re-initialize the quant strategy based on current TRADING_MODE."""
        if self.trading_config.TRADING_MODE == "quant_probability" and self.quant_config.QUANT_MODE_ENABLED:
            from .quant_strategy import QuantitativeProbabilityStrategy
            self._quant_strategy = QuantitativeProbabilityStrategy(self.quant_config)
            print(f"[WeatherBot] QUANTITATIVE PROBABILITY MODE active — >60% prob, +15c EV, Safe-Bet chains")
        else:
            self._quant_strategy = None

    def set_trading_mode(self, mode: str):
        """Change trading mode at runtime and reinitialize quant strategy."""
        mode = mode.lower()
        self.trading_config.TRADING_MODE = mode
        self._init_quant_strategy()
        strategy_name = "QUANTITATIVE PROBABILITY" if self._quant_strategy else "SCALPER"
        print(f"[WeatherBot] Trading mode changed to: {strategy_name}")

    # ── State Management ──────────────────────────────────────────

    def _load_state(self):
        """Load saved trading state from disk."""
        state_file = POSITION_FILE
        if state_file.exists():
            try:
                data = json.loads(state_file.read_text())
                self._trade_counter = data.get("weather_trade_counter", 0)
                for t_data in data.get("weather_trades", []):
                    trade = WeatherTrade(**t_data)
                    self._trades.append(trade)
                    if trade.outcome == "PENDING":
                        self._active_positions[trade.ticker] = trade
                print(f"[WeatherBot] Loaded {len(self._trades)} weather trades, "
                      f"{len(self._active_positions)} active")
            except (json.JSONDecodeError, TypeError) as e:
                print(f"[WeatherBot] Failed to load state: {e}")

    def _save_state(self):
        """Persist trading state to disk."""
        state_file = POSITION_FILE
        try:
            data = {}
            if state_file.exists():
                data = json.loads(state_file.read_text())
            data["weather_trade_counter"] = self._trade_counter
            data["weather_trades"] = [asdict(t) for t in self._trades]
            state_file.write_text(json.dumps(data, indent=2))
        except Exception as e:
            print(f"[WeatherBot] Failed to save state: {e}")

    # ── Main Trading Cycle ────────────────────────────────────────

    def scan_and_trade(self):
        """
        Main trading cycle: scan -> analyze -> trade.

        This is the weather equivalent of the crypto bot's _on_entry().
        """
        scan_time = datetime.now(timezone.utc)
        self._scan_count += 1

        mode_label = "QUANT PROBABILITY" if self._quant_strategy else "SCALPER"
        print(f"\n{'='*60}")
        print(f"[WeatherBot] SCAN #{self._scan_count} — {scan_time.isoformat()[:19]}")
        print(f"  Mode: {'PAPER' if self.trading_config.PAPER_TRADING else 'LIVE'} | Strategy: {mode_label}")
        print(f"  Active positions: {len(self._active_positions)}/{self.weather_config.MAX_WEATHER_POSITIONS}")
        print(f"{'='*60}")

        # Step 1: Resolve any settled positions
        self._resolve_positions()

        # Step 2: Check if we have capacity for new trades
        if len(self._active_positions) >= self.weather_config.MAX_WEATHER_POSITIONS:
            print(f"[WeatherBot] Max positions reached ({self.weather_config.MAX_WEATHER_POSITIONS}) — skipping scan")
            return

        # Step 3: Scan weather markets
        print(f"[WeatherBot] Scanning weather markets...")

        # ══════════════════════════════════════════════════════════════════
        # PRIMARY SCAN: Direct ticker-based search for known weather tickers.
        #
        # Kalshi's "Climate and Weather" category is FULL of junk — sports,
        # cross-category, multi-event bundles, etc. (50+ markets, ~90% junk).
        # Instead of scanning the category and filtering, we directly search
        # for known weather ticker prefixes (KXHIGHNY, KXHIGHLAX, etc.).
        #
        # This is the whitelist approach: only search for tickers we KNOW
        # are weather, instead of trying to filter out non-weather junk.
        # ══════════════════════════════════════════════════════════════════
        weather_markets = self._scan_by_known_tickers()

        # SECONDARY: Category scan as fallback (to discover new weather tickers)
        # Only used if ticker scan finds very few markets
        if len(weather_markets) < 3:
            print(f"[WeatherBot] Ticker scan found only {len(weather_markets)} markets, "
                  f"trying category scan as fallback...")
            category_markets = self.scanner.get_by_category(
                "weather",
                limit=50
            )
            # Merge, avoiding duplicates
            existing_tickers = {m.ticker for m in weather_markets}
            for m in category_markets:
                if m.ticker not in existing_tickers:
                    weather_markets.append(m)
                    existing_tickers.add(m.ticker)

        if not weather_markets:
            print(f"[WeatherBot] No weather markets found")
            self._category_status["weather"] = {
                "last_scan": scan_time.isoformat(),
                "markets_found": 0,
                "opportunities": 0,
            }
            return

        print(f"[WeatherBot] Found {len(weather_markets)} weather markets")

        # Step 4: Analyze each market
        opportunities: List[Dict[str, Any]] = []
        filtered_count = 0
        weather_count = 0
        filter_reasons: Dict[str, int] = {}  # Track why markets are filtered
        weather_tickers: List[str] = []  # Track which tickers pass the filter

        for market in weather_markets:
            # Skip if already in a position for this ticker
            if market.ticker in self._active_positions:
                continue

            # Skip non-weather markets (sports, cross-category, etc.)
            # This prevents wasting API calls on false positives from Kalshi's category
            if not is_actual_weather_market(market):
                filtered_count += 1
                # Categorize why it was filtered (by ticker prefix)
                ticker_upper = market.ticker.upper()
                if ticker_upper.startswith("KXMVESPORTS"):
                    reason = "sports_multi_game"
                elif ticker_upper.startswith("KXMVECROSS"):
                    reason = "cross_category"
                elif ticker_upper.startswith("KXMVE"):
                    reason = "multi_event"
                elif ticker_upper.startswith(("KXNBA", "KXNFL", "KXMLB", "KXNHL")):
                    reason = "sports_league"
                else:
                    reason = f"other({ticker_upper[:15]})"
                filter_reasons[reason] = filter_reasons.get(reason, 0) + 1
                continue

            weather_count += 1
            weather_tickers.append(market.ticker)

            try:
                # Route to quant strategy if in quant_probability mode
                if self._quant_strategy:
                    rec = self._quant_strategy.analyze_market(market)
                else:
                    rec = self.weather_strategy.analyze_market(market)
                if rec and rec.suggested_size > 0:
                    # Apply AI enhancement if enabled
                    if self.weather_config.WEATHER_AI_ENHANCED and self.ai.api_key:
                        rec = self._ai_enhance_analysis(market, rec)

                    if rec and rec.suggested_size > 0:
                        opportunities.append({
                            "market": market,
                            "recommendation": rec,
                        })
            except Exception as e:
                print(f"[WeatherBot] Error analyzing {market.ticker}: {e}")
                continue

        # Sort by edge (best first)
        opportunities.sort(
            key=lambda x: abs(x["recommendation"].ev_cents),
            reverse=True
        )

        self._last_scan_results = [o["recommendation"] for o in opportunities]

        if filtered_count > 0:
            reasons_str = ", ".join(f"{k}={v}" for k, v in sorted(filter_reasons.items(), key=lambda x: -x[1]))
            print(f"[WeatherBot] Filtered out {filtered_count} non-weather markets: {reasons_str}")

        if weather_tickers:
            # Show which tickers passed the filter (first 10)
            sample = weather_tickers[:10]
            suffix = f" +{len(weather_tickers)-10} more" if len(weather_tickers) > 10 else ""
            print(f"[WeatherBot] Weather tickers: {', '.join(sample)}{suffix}")
        elif filtered_count > 0 and weather_count == 0:
            print(f"[WeatherBot] WARNING: All {len(weather_markets)} markets were non-weather!")
            print(f"[WeatherBot] This is unusual — the ticker-based scan should find weather markets.")

        print(f"[WeatherBot] Found {len(opportunities)} +EV opportunities ({weather_count} weather markets analyzed)")

        if not opportunities:
            self._category_status["weather"] = {
                "last_scan": scan_time.isoformat(),
                "markets_found": len(weather_markets),
                "opportunities": 0,
            }
            return

        # Step 5: Print opportunities
        for i, opp in enumerate(opportunities[:10]):
            rec = opp["recommendation"]
            m = opp["market"]
            print(f"  {i+1}. {m.ticker} | {rec.direction.upper()} | "
                  f"fair={rec.fair_probability:.0%} mkt={rec.market_price:.0%} | "
                  f"EV={rec.ev_cents:+.1f}¢ | conf={rec.confidence:.0%} | "
                  f"risk={rec.risk_level}")

        # Step 6: Execute trades
        if self.weather_config.WEATHER_AUTO_TRADE:
            remaining_slots = self.weather_config.MAX_WEATHER_POSITIONS - len(self._active_positions)
            for opp in opportunities[:remaining_slots]:
                self._execute_weather_trade(opp["market"], opp["recommendation"])
        else:
            print(f"[WeatherBot] Auto-trade disabled — opportunities logged but not executed")
            print(f"  Enable with: WEATHER_AUTO_TRADE=true in .env")

        # Update category status
        self._category_status["weather"] = {
            "last_scan": scan_time.isoformat(),
            "markets_found": len(weather_markets),
            "weather_markets": weather_count,
            "filtered_non_weather": filtered_count,
            "opportunities": len(opportunities),
            "best_edge": opportunities[0]["recommendation"].ev_cents if opportunities else 0,
        }

        self._save_state()

    # ── Ticker-Based Scan ─────────────────────────────────────────

    def _scan_by_known_tickers(self) -> List[MarketInfo]:
        """
        PRIMARY scan: Search for weather markets using known series tickers.

        This is the whitelist approach — instead of scanning Kalshi's
        "Climate and Weather" category (which is ~90% sports/cross-category
        junk), we directly query by series ticker for weather we KNOW exists:

          KXHIGHNY   — NYC high temperature series
          KXHIGHLAX  — LA high temperature series
          KXHIGHTBOS — Boston high temperature (with T prefix)
          KXRAINNY   — NYC rain series
          KXSNOWDEN  — Denver snow series
          KXHURR     — Hurricane markets series
          etc.

        CRITICAL FIX: We use the `series_ticker` API parameter (NOT
        `ticker_prefix` which does NOT exist in Kalshi's V2 API).
        The `series_ticker` parameter returns ALL markets in a series,
        which is exactly what we need.

        Reference: suislanchez/polymarket-kalshi-weather-bot uses this
        exact approach successfully:
          params = {"series_ticker": "KXHIGHNY", "limit": 200}

        The Kalshi API also supports the official kalshi_python SDK:
          MarketsApi.get_markets(series_ticker="KXHIGHNY")

        Strategy (3 methods, tried in order):
          1. kalshi_python SDK (if available) — most robust
          2. Direct API with series_ticker param — reliable
          3. Category scan fallback (already exists in caller)
        """
        markets: List[MarketInfo] = []
        found_tickers = set()
        patterns = self.weather_config.WEATHER_TICKER_PATTERNS

        print(f"[WeatherBot] Ticker scan: searching {len(patterns)} known weather series...")

        # ══════════════════════════════════════════════════════════════════
        # METHOD 1: Try kalshi_python SDK (most robust, proper auth)
        # ══════════════════════════════════════════════════════════════════
        sdk_markets = self._scan_with_kalshi_sdk(patterns)
        if sdk_markets:
            for mi in sdk_markets:
                if mi.ticker not in found_tickers:
                    markets.append(mi)
                    found_tickers.add(mi.ticker)
            print(f"[WeatherBot] SDK scan found {len(sdk_markets)} weather markets")

        # ══════════════════════════════════════════════════════════════════
        # METHOD 2: Direct API with series_ticker parameter
        # ══════════════════════════════════════════════════════════════════
        # If SDK didn't find enough, or as supplemental scan
        if len(markets) < 3:
            api_markets = self._scan_with_series_ticker_api(patterns)
            for mi in api_markets:
                if mi.ticker not in found_tickers:
                    markets.append(mi)
                    found_tickers.add(mi.ticker)

        if markets:
            # Show sample of found tickers
            sample_tickers = [m.ticker for m in markets[:5]]
            print(f"[WeatherBot] Ticker scan found {len(markets)} weather markets")
            print(f"[WeatherBot] Sample tickers: {', '.join(sample_tickers)}"
                  + (f" +{len(markets)-5} more" if len(markets) > 5 else ""))
        else:
            print(f"[WeatherBot] Ticker scan found 0 markets — "
                  f"no active markets matching known weather series")

        return markets

    # ── SDK-Based Scanner ─────────────────────────────────────────

    def _scan_with_kalshi_sdk(self, patterns: list) -> List[MarketInfo]:
        """
        Scan weather markets using the official kalshi_python SDK.

        The SDK provides MarketsApi.get_markets(series_ticker=...)
        which is the correct way to find all markets in a series.

        Returns list of MarketInfo objects.
        """
        markets: List[MarketInfo] = []

        try:
            from kalshi_python import KalshiClient, MarketsApi, Configuration
        except ImportError:
            print(f"[WeatherBot] kalshi_python SDK not available, skipping SDK scan")
            return markets

        try:
            # Configure SDK client with our API credentials
            config = Configuration()
            # Use the correct base URL
            if self.kalshi_config.ENV == "prod":
                api_url = "https://api.elections.kalshi.com/trade-api/v2"
            else:
                api_url = "https://demo-api.kalshi.co/trade-api/v2"

            client = SDKClient(
                key_id=self.kalshi_config.API_KEY,       # NOT 'api_key_id'!
                private_key=self.kalshi_config.get_private_key(),  # NOT 'private_key_pem'!
                url=api_url,                              # NOT Configuration object!
            )

            # Must call login() to establish authenticated session
            try:
                client.login()
            except Exception as auth_err:
                print(f"[WeatherBot] SDK auth failed: {auth_err} — falling back to direct API")
                return markets

            markets_api = MarketsApi(client)

            # Query each series ticker
            for series_ticker in patterns:
                try:
                    response = markets_api.get_markets(
                        series_ticker=series_ticker,
                        limit=100,
                    )

                    if not response or not response.markets:
                        continue

                    for raw_market in response.markets:
                        mi = self._parse_sdk_market(raw_market, series_ticker)
                        if mi:
                            # Defense in depth: reject known non-weather tickers
                            ticker_upper = mi.ticker.upper()
                            if any(ticker_upper.startswith(p) for p in [
                                "KXMVESPORTS", "KXMVECROSSCATEGORY", "KXMVE",
                                "KXNBA", "KXNFL", "KXMLB", "KXNHL"
                            ]):
                                continue
                            markets.append(mi)

                except Exception as e:
                    # Individual series failures are normal (some series may not exist)
                    continue

        except Exception as e:
            print(f"[WeatherBot] SDK scan error: {e}")

        return markets

    def _parse_sdk_market(self, raw_market, series_ticker: str) -> Optional[MarketInfo]:
        """
        Parse a kalshi_python SDK market object into our MarketInfo.

        The SDK returns objects with attributes like:
          ticker, title, status, last_price, yes_ask, no_ask, etc.
        """
        try:
            # Extract attributes from SDK object (could be dict or object)
            if isinstance(raw_market, dict):
                ticker = raw_market.get("ticker", "")
                title = raw_market.get("title", "")
                status = raw_market.get("status", "unknown")
                last_price = raw_market.get("last_price")
                yes_ask = raw_market.get("yes_ask")
                no_ask = raw_market.get("no_ask")
                volume = raw_market.get("volume") or raw_market.get("volume_fp")
                open_interest = raw_market.get("open_interest") or raw_market.get("open_interest_fp")
                subtitle = raw_market.get("yes_sub_title") or raw_market.get("subtitle", "")
                event_ticker = raw_market.get("event_ticker", "")
                close_time = raw_market.get("close_time", "")
            else:
                # SDK object with attributes
                ticker = getattr(raw_market, 'ticker', '')
                title = getattr(raw_market, 'title', '')
                status = getattr(raw_market, 'status', 'unknown')
                last_price = getattr(raw_market, 'last_price', None)
                yes_ask = getattr(raw_market, 'yes_ask', None)
                no_ask = getattr(raw_market, 'no_ask', None)
                volume = getattr(raw_market, 'volume', None) or getattr(raw_market, 'volume_fp', None)
                open_interest = getattr(raw_market, 'open_interest', None) or getattr(raw_market, 'open_interest_fp', None)
                subtitle = getattr(raw_market, 'yes_sub_title', '') or getattr(raw_market, 'subtitle', '')
                event_ticker = getattr(raw_market, 'event_ticker', '')
                close_time = getattr(raw_market, 'close_time', '')

            if not ticker:
                return None

            # Accept both 'active' and 'open' statuses
            # (Kalshi uses different status values across API versions)
            if status not in ("active", "open"):
                return None

            # Parse price — SDK may return price as percentage (0-100) or decimal (0-1)
            if last_price is not None:
                try:
                    price = float(last_price)
                    # If price > 1, it's in cents (0-100 scale) → convert to 0-1
                    if price > 1:
                        price = price / 100.0
                except (ValueError, TypeError):
                    price = 0.0
            else:
                price = 0.0

            # Skip zero-price markets (no one trading them)
            if price <= 0.0:
                return None

            # Parse volume
            try:
                vol = float(volume) if volume else 0.0
            except (ValueError, TypeError):
                vol = 0.0

            # Parse open interest
            try:
                oi = float(open_interest) if open_interest else 0.0
            except (ValueError, TypeError):
                oi = 0.0

            return MarketInfo(
                ticker=ticker,
                title=title or ticker,
                category="weather",
                yes_price=price,
                no_price=round(1.0 - price, 4),
                volume_24h=vol,
                open_interest=oi,
                status=status,
                event_ticker=event_ticker,
                subtitle=str(subtitle) if subtitle else "",
                close_time=str(close_time) if close_time else "",
            )
        except Exception:
            return None

    # ── Direct API Scanner ────────────────────────────────────────

    def _scan_with_series_ticker_api(self, patterns: list) -> List[MarketInfo]:
        """
        Scan weather markets using direct API calls with series_ticker param.

        This is the fallback if the SDK is unavailable. Uses the
        KalshiClient (which has proper RSA-PSS auth) to query:
          GET /markets?series_ticker=KXHIGHNY&limit=100

        CRITICAL: Uses `series_ticker` (valid API param), NOT
        `ticker_prefix` (which doesn't exist in the API and was the
        root cause of the "0 weather markets found" bug).
        """
        markets: List[MarketInfo] = []
        found_tickers = set()

        print(f"[WeatherBot] Direct API scan: querying {len(patterns)} series...")

        for series_ticker in patterns:
            try:
                # Use KalshiClient.get_active_markets() which supports
                # series_ticker properly with auth + fallback status filters
                # KEY FIX: This uses 'series_ticker' NOT 'ticker_prefix'
                raw_markets = self.client.get_active_markets(series_ticker)

                if not raw_markets:
                    continue

                for raw in raw_markets:
                    mi = self._parse_api_market(raw, series_ticker)
                    if mi and mi.ticker not in found_tickers:
                        # Defense in depth: reject known non-weather tickers
                        ticker_upper = mi.ticker.upper()
                        if any(ticker_upper.startswith(p) for p in [
                            "KXMVESPORTS", "KXMVECROSSCATEGORY", "KXMVE",
                            "KXNBA", "KXNFL", "KXMLB", "KXNHL"
                        ]):
                            continue
                        markets.append(mi)
                        found_tickers.add(mi.ticker)

            except Exception:
                continue

        return markets

    def _parse_api_market(self, raw: dict, series_ticker: str) -> Optional[MarketInfo]:
        """
        Parse a raw Kalshi API market dict into MarketInfo.

        Handles both V1 and V2 API response formats, with
        relaxed status filtering (accepts 'active' and 'open').
        """
        try:
            status = raw.get("status", "unknown")

            # Accept both 'active' and 'open' statuses
            # Kalshi uses different status values across API versions
            if status not in ("active", "open"):
                return None

            # Parse price — V2 uses last_price (0-100 scale), V1 uses last_price_dollars (0-1)
            last_price_dollars = raw.get("last_price_dollars")
            last_price = raw.get("last_price")

            if last_price_dollars is not None:
                try:
                    price = float(last_price_dollars)
                except (ValueError, TypeError):
                    price = 0.0
            elif last_price is not None:
                try:
                    price = float(last_price)
                    if price > 1:
                        price = price / 100.0
                except (ValueError, TypeError):
                    price = 0.0
            else:
                price = 0.0

            # Skip zero-price markets
            if price <= 0.0:
                return None

            ticker = raw.get("ticker", "")
            title = raw.get("title", "")
            subtitle = raw.get("yes_sub_title") or raw.get("no_sub_title") or raw.get("subtitle", "")

            # Parse volume
            volume = raw.get("volume_24h_fp") or raw.get("volume_fp") or raw.get("volume")
            try:
                vol = float(volume) if volume else 0.0
            except (ValueError, TypeError):
                vol = 0.0

            # Parse open interest
            oi = raw.get("open_interest_fp") or raw.get("open_interest")
            try:
                open_interest = float(oi) if oi else 0.0
            except (ValueError, TypeError):
                open_interest = 0.0

            return MarketInfo(
                ticker=ticker,
                title=title or ticker,
                category="weather",
                yes_price=price,
                no_price=round(1.0 - price, 4),
                volume_24h=vol,
                open_interest=open_interest,
                status=status,
                event_ticker=raw.get("event_ticker", ""),
                subtitle=str(subtitle) if subtitle else "",
                close_time=raw.get("close_time", ""),
            )
        except Exception:
            return None

    # ── AI Enhancement ────────────────────────────────────────────

    def _ai_enhance_analysis(
        self,
        market: MarketInfo,
        rec: TradeRecommendation,
    ) -> Optional[TradeRecommendation]:
        """
        Use AI (OpenRouter) to enhance weather trade analysis.

        The AI gets context about the market, our forecast data,
        and the EV estimate, then provides a confidence modifier.
        """
        if not self.ai.api_key:
            return rec

        prompt = f"""You are an expert weather derivatives trader analyzing a Kalshi climate contract.

MARKET: {market.title}
TICKER: {market.ticker}
SUBTITLE: {market.subtitle}
CURRENT YES PRICE: {rec.market_price:.0%} (market-implied probability)
OUR FAIR VALUE: {rec.fair_probability:.0%}
OUR EV EDGE: {rec.ev_cents:+.1f} cents
OUR DIRECTION: {rec.direction.upper()}
OUR CONFIDENCE: {rec.confidence:.0%}
REASONING: {rec.reasoning}

Our analysis uses: NWS forecasts, Open-Meteo forecasts, and Meteostat station-based
historical observations (real weather station data, not model reanalysis).

Based on your knowledge of weather forecasting accuracy, NWS/Meteostat reliability,
historical weather patterns, and market microstructure on Kalshi:

1. Do you AGREE or DISAGREE with the direction?
2. What confidence MODIFIER would you apply? (-0.20 to +0.15)
3. Any RISK WARNING?

Respond as JSON only:
{{"ai_direction": "yes" or "no" or "neutral", "confidence_modifier": -0.20 to +0.15, "risk_warning": "description or null", "reasoning": "1-2 sentence explanation"}}"""

        try:
            import requests as req
            resp = req.post(
                self.ai.api_url,
                headers={
                    "Authorization": f"Bearer {self.ai.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://kalshi-weather-bot.local",
                },
                json={
                    "model": self.ai.model,
                    "messages": [
                        {"role": "system", "content": "You are a concise weather derivatives analyst. Respond with valid JSON only."},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.3,
                    "max_tokens": 200,
                },
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()

            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")

            # Parse JSON
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]

            result = json.loads(content.strip())

            modifier = float(result.get("confidence_modifier", 0))
            modifier = max(-0.20, min(0.15, modifier))
            ai_direction = result.get("ai_direction", "neutral")

            # If AI disagrees, reduce confidence significantly
            if ai_direction != "neutral" and ai_direction != rec.direction:
                print(f"  AI DISAGREES: AI says {ai_direction}, we say {rec.direction}")
                modifier = min(modifier, -0.15)

            # Apply modifier to confidence
            new_confidence = max(0.0, min(1.0, rec.confidence + modifier))

            # If confidence dropped below minimum, skip this trade
            if new_confidence < self.weather_config.WEATHER_MIN_CONFIDENCE:
                print(f"  AI reduced confidence below minimum ({new_confidence:.0%} < {self.weather_config.WEATHER_MIN_CONFIDENCE:.0%})")
                return None

            # Create updated recommendation
            risk_warning = result.get("risk_warning")
            if risk_warning:
                rec.reasoning += f" | AI Warning: {risk_warning}"

            rec.confidence = new_confidence
            print(f"  AI: {ai_direction} | mod={modifier:+.2f} | conf={new_confidence:.0%} | "
                  f"{result.get('reasoning', '')[:80]}")

            return rec

        except Exception as e:
            print(f"  AI enhancement failed: {e}")
            return rec  # Return original recommendation on AI failure

    # ── Trade Execution ───────────────────────────────────────────

    def _execute_weather_trade(
        self,
        market: MarketInfo,
        rec: TradeRecommendation,
    ) -> Optional[WeatherTrade]:
        """Execute a weather market trade based on a recommendation."""
        # Determine side
        if rec.direction == "yes":
            side = "yes"
        else:
            side = "no"

        # Calculate position size
        price_cents = int(round(market.yes_price * 100)) if rec.direction == "yes" else int(round(market.no_price * 100))
        price_cents = max(1, min(99, price_cents))
        cost_per_contract = price_cents / 100.0

        # Size within max position dollars
        num_contracts = max(1, int(self.weather_config.MAX_WEATHER_POSITION_DOLLARS / cost_per_contract))
        total_cost = num_contracts * cost_per_contract

        # Cap at max position size
        if total_cost > self.weather_config.MAX_WEATHER_POSITION_DOLLARS:
            num_contracts = max(1, int(self.weather_config.MAX_WEATHER_POSITION_DOLLARS / cost_per_contract))
            total_cost = num_contracts * cost_per_contract

        # Create trade record
        self._trade_counter += 1
        trade_id = f"WX-{self._trade_counter:04d}"

        trade = WeatherTrade(
            trade_id=trade_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            ticker=market.ticker,
            title=market.title,
            direction=rec.direction,
            side=side,
            contracts=num_contracts,
            entry_price=cost_per_contract,
            cost_dollars=total_cost,
            paper_trade=self.trading_config.PAPER_TRADING,
            fair_probability=rec.fair_probability,
            market_price=rec.market_price,
            ev_cents=rec.ev_cents,
            confidence=rec.confidence,
            reasoning=rec.reasoning,
        )

        # Execute or simulate
        if self.trading_config.PAPER_TRADING:
            print(f"[WeatherBot] PAPER TRADE: {trade_id} | "
                  f"{rec.direction.upper()} {market.ticker} | "
                  f"side={side} {num_contracts}x @ ${cost_per_contract:.3f} = ${total_cost:.2f} | "
                  f"EV={rec.ev_cents:+.1f}¢ | conf={rec.confidence:.0%}")
        else:
            # Live trading: place the actual order
            result = self.client.create_order(
                ticker=market.ticker,
                side=side,
                count=num_contracts,
                price=price_cents,
            )

            if not result:
                print(f"[WeatherBot] Order failed for {trade_id}")
                return None

            print(f"[WeatherBot] LIVE TRADE: {trade_id} | "
                  f"{rec.direction.upper()} {market.ticker} | "
                  f"{num_contracts}x @ ${cost_per_contract:.3f} = ${total_cost:.2f}")

        # Record the trade
        self._trades.append(trade)
        self._active_positions[market.ticker] = trade

        # Log to trade log
        self._log_trade(trade, rec)

        return trade

    # ── Position Resolution ───────────────────────────────────────

    def _resolve_positions(self):
        """Check all active positions and resolve settled ones."""
        to_remove = []

        for ticker, trade in list(self._active_positions.items()):
            # Check Kalshi for settlement
            market_data = self.client.get_market_price(ticker)

            if market_data:
                status = market_data.get("status", "")
                result = market_data.get("result")
                settlement_price = market_data.get("settlement_price")
                last_price = market_data.get("last_price")

                won = None

                if settlement_price is not None:
                    won = (trade.side == "yes" and settlement_price >= 100) or \
                          (trade.side == "no" and settlement_price <= 0)
                elif result is not None and result != "":
                    won = (trade.side == "yes" and result == "yes") or \
                          (trade.side == "no" and result == "no")
                elif status in ("settled", "closed", "finalized"):
                    if last_price is not None and isinstance(last_price, (int, float)):
                        won = (trade.side == "yes" and last_price >= 50) or \
                              (trade.side == "no" and last_price <= 50)

                if won is not None:
                    if won:
                        trade.outcome = "WIN"
                        trade.payout_dollars = trade.contracts * 1.0
                        trade.profit_dollars = trade.payout_dollars - trade.cost_dollars
                    else:
                        trade.outcome = "LOSS"
                        trade.payout_dollars = 0.0
                        trade.profit_dollars = -trade.cost_dollars

                    print(f"[WeatherBot] RESOLVED {trade.trade_id}: {trade.outcome} | "
                          f"P&L: ${trade.profit_dollars:+.2f}")
                    to_remove.append(ticker)

        for ticker in to_remove:
            del self._active_positions[ticker]

        if to_remove:
            self._save_state()

    # ── Logging ───────────────────────────────────────────────────

    def _log_trade(self, trade: WeatherTrade, rec: TradeRecommendation):
        """Write trade details to the log file."""
        log_file = TRADE_LOG_DIR / f"trades_{date.today().isoformat()}.jsonl"
        entry = {
            "trade": asdict(trade),
            "recommendation": rec.to_dict() if hasattr(rec, 'to_dict') else str(rec),
            "strategy": "weather",
        }
        with open(log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")

    # ── Bot Control ───────────────────────────────────────────────

    def start(self):
        """Start the weather trading bot in a background thread."""
        if self._running:
            print("[WeatherBot] Already running")
            return

        print(f"\n{'='*60}")
        strategy_name = "QUANTITATIVE PROBABILITY" if self._quant_strategy else "SCALPER"
        print(f"  KALSHI WEATHER TRADING BOT")
        print(f"  {strategy_name} Strategy | AI-Enhanced Auto-Trading System")
        print(f"{'='*60}")
        print(f"  Mode: {'PAPER TRADING' if self.trading_config.PAPER_TRADING else 'LIVE TRADING!'}")
        print(f"  Strategy: {strategy_name}")
        print(f"  Auto-Trade: {self.weather_config.WEATHER_AUTO_TRADE}")
        print(f"  AI Enhanced: {self.weather_config.WEATHER_AI_ENHANCED}")
        print(f"  Scan Interval: {self.weather_config.SCAN_INTERVAL_MINUTES} min")
        print(f"  Max Positions: {self.weather_config.MAX_WEATHER_POSITIONS}")
        print(f"  Max Position Size: ${self.weather_config.MAX_WEATHER_POSITION_DOLLARS:.2f}")
        print(f"  Min EV Edge: {self.weather_config.WEATHER_MIN_EV_CENTS:.0f}¢")
        print(f"  Min Confidence: {self.weather_config.WEATHER_MIN_CONFIDENCE:.0%}")
        print(f"{'='*60}")

        # Authenticate with Kalshi
        print("[WeatherBot] Authenticating with Kalshi...")
        if not self.client.login():
            print("[WeatherBot] Auth FAILED — continuing in observation-only mode")

        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        print("[WeatherBot] Started — scanning weather markets")

    def stop(self):
        """Stop the weather trading bot."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        self._save_state()
        print("[WeatherBot] Stopped")

    def _run_loop(self):
        """Main bot loop: scan on interval, resolve positions."""
        while self._running:
            try:
                self.scan_and_trade()

                # Wait for next scan interval
                interval = self.weather_config.SCAN_INTERVAL_MINUTES * 60
                wait_until = time.time() + interval

                while self._running and time.time() < wait_until:
                    time.sleep(5)  # Check every 5s for stop signal

            except Exception as e:
                print(f"[WeatherBot] Error in loop: {e}")
                time.sleep(30)  # Wait before retrying

    # ── Status API ────────────────────────────────────────────────

    def get_status(self) -> Dict[str, Any]:
        """Get complete bot status for the dashboard."""
        total = len(self._trades)
        wins = sum(1 for t in self._trades if t.outcome == "WIN")
        losses = sum(1 for t in self._trades if t.outcome == "LOSS")
        pending = sum(1 for t in self._trades if t.outcome == "PENDING")
        net_pnl = sum(
            t.profit_dollars for t in self._trades
            if t.profit_dollars is not None
        )

        return {
            "running": self._running,
            "mode": "PAPER" if self.trading_config.PAPER_TRADING else "LIVE",
            "auto_trade": self.weather_config.WEATHER_AUTO_TRADE,
            "ai_enhanced": self.weather_config.WEATHER_AI_ENHANCED,
            "scan_count": self._scan_count,
            "total_trades": total,
            "wins": wins,
            "losses": losses,
            "pending": pending,
            "win_rate": f"{wins / (wins + losses) * 100:.1f}%" if (wins + losses) > 0 else "0%",
            "net_pnl": f"${net_pnl:+.2f}",
            "active_positions": len(self._active_positions),
            "max_positions": self.weather_config.MAX_WEATHER_POSITIONS,
            "trading_mode": self.trading_config.TRADING_MODE,
            "quant_enabled": bool(self._quant_strategy),
            "category_status": self._category_status,
            "last_scan_results": [
                {
                    "ticker": r.ticker,
                    "direction": r.direction,
                    "ev_cents": r.ev_cents,
                    "confidence": r.confidence,
                    "strategy": r.strategy,
                }
                for r in self._last_scan_results[:10]
            ] if self._last_scan_results else None,
        }
