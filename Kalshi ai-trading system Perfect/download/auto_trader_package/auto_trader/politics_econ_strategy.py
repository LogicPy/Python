"""
Kalshi Politics & Economics Sentiment Strategy

Identifies +EV opportunities in political and economic event markets
by analyzing sentiment from GDELT news data and LLM reasoning.

Key Edge Sources:
- Market overreaction to news events (sentiment lag)
- Scheduled data releases (CPI, jobs, etc.) where consensus > market
- Policy outcomes where legislative math is clear but market isn't

Uses GDELT API for real-time news sentiment scanning, and optional
FRED API for economic data benchmarks.
"""

import re
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

import requests

from .market_scanner import MarketScanner, MarketInfo
from .ev_analyzer import EVAnalyzer, TradeRecommendation
from .ai_analyzer import AIAnalyzer
from .rate_limiter import RateLimiter


# ── GDELT News Client ──────────────────────────────────────────────────

GDELT_API_BASE = "https://api.gdeltproject.org/api/v2"


class GDELTClient:
    """
    Client for the GDELT Project news API.
    Free, no API key needed (rate limited to ~300 req/day).

    Includes rate limiting to prevent 429 errors:
    - Min 3s between requests (GDELT is strict on rate limits)
    - Exponential backoff on 429 responses
    - Auto-reset on successful responses
    """

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "KalshiResearch/1.0",
            "Accept": "application/json",
        })
        # Rate limiter: GDELT allows ~300 req/day but is strict on burst rate
        # Min 5s between requests prevents 429 errors (increased from 3s)
        self._rate_limiter = RateLimiter(
            min_interval=5.0,      # 5s between GDELT requests (was 3s, too aggressive)
            max_backoff=300.0,     # Max 5 min backoff (was 120s)
            initial_backoff=10.0,  # Start with 10s backoff on 429 (was 5s)
            backoff_factor=2.0,    # Double each time: 10, 20, 40, 80...
            jitter_range=1.0,      # Add 0-1s jitter
        )

    def _request_with_retry(self, url: str, params: dict, max_retries: int = 3) -> Optional[requests.Response]:
        """
        Make a GDELT API request with automatic retry on 429 errors.

        Uses the RateLimiter's exponential backoff to wait before
        retrying. After max_retries failures, returns None.
        """
        for attempt in range(max_retries):
            # Rate limit before request
            self._rate_limiter.wait("api.gdeltproject.org")

            try:
                resp = self.session.get(url, params=params, timeout=15)

                if resp.status_code == 429:
                    self._rate_limiter.backoff("api.gdeltproject.org")
                    if attempt < max_retries - 1:
                        print(f"[GDELT] Rate limited (429) — attempt {attempt+1}/{max_retries}, retrying after backoff...")
                        continue
                    else:
                        print(f"[GDELT] Rate limited (429) — max retries ({max_retries}) reached, giving up")
                        return None

                if resp.status_code != 200:
                    print(f"[GDELT] API error: {resp.status_code}")
                    return None

                # Success — reset backoff
                self._rate_limiter.reset("api.gdeltproject.org")
                return resp

            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    print(f"[GDELT] Request error (attempt {attempt+1}/{max_retries}): {e}")
                    continue
                else:
                    print(f"[GDELT] Request failed after {max_retries} attempts: {e}")
                    return None

        return None

    def search_articles(
        self,
        query: str,
        max_records: int = 50,
        timespan: str = "7d",
    ) -> Optional[List[Dict]]:
        """
        Search GDELT for recent articles matching a query.

        Args:
            query: Search terms (e.g., "inflation CPI" or "election Senate")
            max_records: Max number of articles to return
            timespan: Time window (1d, 7d, 30d)

        Returns:
            List of article dicts with title, url, date, source, sentiment
        """
        try:
            # GDELT doc API for article search
            url = f"{GDELT_API_BASE}/doc/doc"
            params = {
                "query": query,
                "mode": "ArtList",
                "maxRecords": max_records,
                "timespan": timespan,
                "format": "json",
                "sort": "DateDesc",
            }

            resp = self._request_with_retry(url, params)
            if not resp:
                return None

            data = resp.json()
            articles = data.get("articles", [])

            return [
                {
                    "title": a.get("title", ""),
                    "url": a.get("url", ""),
                    "date": a.get("seendate", ""),
                    "source": a.get("source", ""),
                    "language": a.get("language", ""),
                }
                for a in articles
            ]

        except Exception as e:
            print(f"[GDELT] Error searching '{query}': {e}")
            return None

    def get_sentiment_tone(
        self,
        query: str,
        timespan: str = "7d",
    ) -> Optional[Dict]:
        """
        Get GDELT tone/sentiment data for a query over time.
        Returns aggregate tone scores (positive/negative/neutral percentages).

        Includes retry logic for 429 errors with exponential backoff.
        """
        try:
            url = f"{GDELT_API_BASE}/tone/tone"
            params = {
                "query": query,
                "timespan": timespan,
                "format": "json",
            }

            resp = self._request_with_retry(url, params)
            if not resp:
                return None

            data = resp.json()
            tone_data = data.get("tone", {})

            # GDELT tone: ranges from -100 to +100
            # Positive = favorable coverage, Negative = unfavorable
            avg_tone = tone_data.get("avg", 0)
            article_count = tone_data.get("count", 0)

            # Normalize tone to 0-1 probability scale
            # Tone > 0 → sentiment leans positive; < 0 → negative
            normalized = (avg_tone + 100) / 200  # Map [-100, 100] → [0, 1]

            return {
                "avg_tone": avg_tone,
                "article_count": article_count,
                "normalized_sentiment": normalized,
                "query": query,
            }

        except Exception as e:
            print(f"[GDELT] Error getting tone for '{query}': {e}")
            return None

    def get_trending_themes(self) -> Optional[List[str]]:
        """Get currently trending themes from GDELT."""
        try:
            url = f"{GDELT_API_BASE}/doc/doc"
            params = {
                "query": "politics economics policy",
                "mode": "ArtList",
                "maxRecords": 25,
                "timespan": "1d",
                "format": "json",
                "sort": "DateDesc",
            }

            resp = self._request_with_retry(url, params)
            if not resp:
                return None

            data = resp.json()
            articles = data.get("articles", [])
            return [a.get("title", "") for a in articles[:10]]

        except Exception as e:
            print(f"[GDELT] Error getting trending themes: {e}")
            return None


# ── Economic Data Fetcher ──────────────────────────────────────────────

FRED_API_BASE = "https://fred.stlouisfed.org"


class EconomicDataFetcher:
    """
    Fetches economic data for comparing market expectations to reality.
    Uses FRED API (requires free API key) and economic calendar.
    """

    def __init__(self, fred_api_key: Optional[str] = None):
        self.fred_api_key = fred_api_key
        self.session = requests.Session()

    # ── Key Economic Indicators ────────────────────────────────────────

    # Mapped as: indicator_name → FRED series ID
    FRED_SERIES = {
        "cpi": "CPIAUCSL",
        "cpi_yoy": "CPIAUCSL",      # Year-over-year
        "unemployment": "UNRATE",
        "gdp": "GDP",
        "fed_funds": "FEDFUNDS",
        "treasury_10y": "DGS10",
        "treasury_2y": "DGS2",
        "retail_sales": "RSAFS",
        "payroll": "PAYEMS",
        "pce": "PCEPI",
    }

    def get_latest_value(self, series_id: str) -> Optional[Dict]:
        """
        Get the latest value for a FRED series.
        Requires FRED_API_KEY to be set.
        """
        if not self.fred_api_key:
            return None

        try:
            url = f"{FRED_API_BASE}/api/fred/series/observations"
            params = {
                "series_id": series_id,
                "api_key": self.fred_api_key,
                "file_type": "json",
                "sort_order": "desc",
                "limit": 1,
            }

            resp = self.session.get(url, params=params, timeout=10)
            if resp.status_code != 200:
                return None

            data = resp.json()
            observations = data.get("observations", [])
            if not observations:
                return None

            obs = observations[0]
            return {
                "date": obs.get("date", ""),
                "value": float(obs.get("value", 0)),
                "series": series_id,
            }

        except Exception as e:
            print(f"[EconData] Error fetching {series_id}: {e}")
            return None

    # ── Economic Calendar ───────────────────────────────────────────────

    # Scheduled US economic data releases (approximate dates)
    # These create predictable +EV opportunities when market doesn't
    # yet reflect the incoming data
    ECONOMIC_CALENDAR = {
        "cpi": {"day": 13, "frequency": "monthly", "description": "Consumer Price Index"},
        "ppi": {"day": 14, "frequency": "monthly", "description": "Producer Price Index"},
        "payroll": {"day": 3, "frequency": "monthly", "description": "Non-Farm Payrolls"},
        "unemployment": {"day": 3, "frequency": "monthly", "description": "Unemployment Rate"},
        "gdp": {"day": 27, "frequency": "quarterly", "description": "GDP (Advance)"},
        "fed": {"day": 15, "frequency": "6weeks", "description": "FOMC Rate Decision"},
    }

    def get_upcoming_releases(self, within_days: int = 7) -> List[Dict]:
        """
        Get upcoming economic data releases within a window.
        These are key opportunities: market often hasn't priced in
        the actual data yet.
        """
        now = datetime.now(timezone.utc)
        upcoming = []

        for name, info in self.ECONOMIC_CALENDAR.items():
            # Simplified: check if release day is within window
            release_day = info["day"]
            day_of_month = now.day

            days_until = release_day - day_of_month
            if days_until < 0:
                days_until += 30  # Next month

            if days_until <= within_days:
                upcoming.append({
                    "name": name,
                    **info,
                    "days_until": days_until,
                })

        return upcoming


# ── Market Text Parser ──────────────────────────────────────────────────

def extract_search_terms(title: str) -> List[str]:
    """
    Extract relevant search terms from a Kalshi market title.
    Removes filler words and focuses on key entities.
    """
    # Remove common filler
    filler = {"will", "the", "a", "an", "in", "on", "at", "be", "this",
              "that", "is", "are", "was", "were", "of", "for", "to", "by",
              "how", "many", "much", "what", "which", "who", "during"}

    words = title.lower().replace("?", "").replace(".", "").split()
    terms = [w for w in words if w not in filler and len(w) > 2]

    # Also extract quoted entities
    entities = re.findall(r'"([^"]+)"', title)
    terms.extend(entities)

    return terms


def extract_economic_indicator(title: str) -> Optional[str]:
    """Check if a market relates to a known economic indicator."""
    title_lower = title.lower()

    indicators = {
        "cpi": ["cpi", "consumer price", "inflation rate"],
        "unemployment": ["unemployment", "jobs report", "employment rate", "nonfarm"],
        "gdp": ["gdp", "gross domestic"],
        "fed_rate": ["fed", "interest rate", "fomc", "federal funds"],
        "treasury": ["treasury", "yield", "bond"],
        "payroll": ["payroll", "jobs added", "non-farm"],
    }

    for indicator, keywords in indicators.items():
        if any(kw in title_lower for kw in keywords):
            return indicator

    return None


# ── Politics/Economics Strategy ─────────────────────────────────────────

class PoliticsEconStrategy:
    """
    Identifies +EV opportunities in politics and economics markets.

    Uses:
    1. GDELT news sentiment to gauge public narrative
    2. LLM reasoning to calculate fair probability
    3. Economic data (FRED) for scheduled releases
    4. Structured analysis framework from EV analyzer

    Workflow:
    1. Scanner finds politics/economics markets
    2. Extract search terms and indicators
    3. Fetch GDELT sentiment data
    4. Check for upcoming economic releases
    5. Feed all context to LLM for probability estimation
    6. EV Analyzer compares to market price
    """

    def __init__(
        self,
        ev_analyzer: Optional[EVAnalyzer] = None,
        ai_analyzer: Optional[AIAnalyzer] = None,
        fred_api_key: Optional[str] = None,
    ):
        self.ev_analyzer = ev_analyzer or EVAnalyzer()
        self.ai_analyzer = ai_analyzer or AIAnalyzer()
        self.gdelt = GDELTClient()
        self.econ_fetcher = EconomicDataFetcher(fred_api_key)

    def scan_and_analyze(
        self,
        scanner: MarketScanner,
    ) -> List[TradeRecommendation]:
        """
        Scan all politics/economics markets and find +EV opportunities.
        """
        markets = (
            scanner.get_by_category("politics") +
            scanner.get_by_category("economics")
        )
        print(f"[PoliticsEcon] Found {len(markets)} politics/economics markets")

        recommendations = []
        for market in markets:
            try:
                rec = self.analyze_market(market)
                if rec and rec.suggested_size > 0:
                    recommendations.append(rec)
            except Exception as e:
                print(f"[PoliticsEcon] Error analyzing {market.ticker}: {e}")

        recommendations.sort(key=lambda r: abs(r.ev_cents), reverse=True)
        print(f"[PoliticsEcon] Found {len(recommendations)} +EV opportunities")
        return recommendations

    def analyze_market(self, market: MarketInfo) -> Optional[TradeRecommendation]:
        """
        Analyze a single politics/economics market.
        """
        # Step 1: Extract search terms
        search_terms = extract_search_terms(market.title)
        if not search_terms:
            return None

        query = " ".join(search_terms[:5])

        # Step 2: Fetch sentiment data
        sentiment = self.gdelt.get_sentiment_tone(query, timespan="7d")

        # Step 3: Check for economic indicator
        indicator = extract_economic_indicator(market.title)
        econ_data = None
        upcoming = self.econ_fetcher.get_upcoming_releases(within_days=5)

        if indicator and self.econ_fetcher.fred_api_key:
            series_id = EconomicDataFetcher.FRED_SERIES.get(indicator)
            if series_id:
                econ_data = self.econ_fetcher.get_latest_value(series_id)

        # Step 4: Fetch recent articles for context
        articles = self.gdelt.search_articles(query, max_records=10)
        article_summaries = []
        if articles:
            article_summaries = [
                f"- {a['title']} ({a['date'][:10]})"
                for a in articles[:5]
            ]

        # Step 5: Use LLM to estimate fair probability
        fair_prob, confidence, reasoning = self._llm_estimate(
            market_title=market.title,
            market_subtitle=market.subtitle,
            market_price=market.implied_prob,
            sentiment=sentiment,
            article_summaries=article_summaries,
            econ_data=econ_data,
            upcoming_releases=upcoming,
        )

        if fair_prob is None:
            return None

        # Step 6: Run through EV analyzer
        data_sources = ["gdelt"]
        if econ_data:
            data_sources.append("fred")
        if upcoming:
            data_sources.append("economic_calendar")

        return self.ev_analyzer.analyze(
            ticker=market.ticker,
            fair_probability=fair_prob,
            market_price=market.implied_prob,
            confidence=confidence,
            reasoning=reasoning,
            strategy="politics_econ",
            data_sources=data_sources,
        )

    def _llm_estimate(
        self,
        market_title: str,
        market_subtitle: str,
        market_price: float,
        sentiment: Optional[Dict],
        article_summaries: List[str],
        econ_data: Optional[Dict],
        upcoming_releases: List[Dict],
    ) -> Tuple[Optional[float], float, str]:
        """
        Use LLM to estimate fair probability based on all gathered context.
        """
        # Build context block
        context_parts = [
            f"Market: {market_title}",
            f"Current Kalshi YES price: {market_price:.0%}",
        ]

        if market_subtitle:
            context_parts.append(f"Details: {market_subtitle}")

        if sentiment:
            context_parts.append(
                f"GDELT sentiment: tone={sentiment['avg_tone']:.1f}, "
                f"articles={sentiment['article_count']}"
            )

        if article_summaries:
            context_parts.append("Recent headlines:\n" + "\n".join(article_summaries))

        if econ_data:
            context_parts.append(
                f"Latest {econ_data['series']} data: "
                f"{econ_data['value']} (as of {econ_data['date']})"
            )

        if upcoming_releases:
            releases_str = ", ".join(
                f"{r['name']} in {r['days_until']}d" for r in upcoming_releases[:3]
            )
            context_parts.append(f"Upcoming releases: {releases_str}")

        context = "\n\n".join(context_parts)

        # LLM prompt
        prompt = f"""You are an expert quantitative trader analyzing a Kalshi event contract.

{context}

Based on the evidence above:
1. What is your estimated PROBABILITY (0-100%) that this event will occur?
2. How CONFIDENT are you in this estimate (0-100%)?
3. Briefly explain your reasoning.

Respond EXACTLY in this JSON format:
{{"probability": <number 0-100>, "confidence": <number 0-100>, "reasoning": "<brief explanation>"}}"""

        try:
            # Use chat() instead of analyze_signal() — this is a generic
            # LLM call, not a crypto momentum analysis.
            # analyze_signal() requires (symbol, momentum_data, kalshi_data)
            # which are not available here.
            response = self.ai_analyzer.chat(
                prompt,
                system_prompt="You are an expert quantitative trader. Respond with valid JSON only.",
                temperature=0.3,
                max_tokens=200,
            )

            if not response:
                return self._sentiment_fallback(market_price, sentiment)

            # Parse JSON response
            json_match = re.search(r'\{[^}]+\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                prob = float(data.get("probability", 50)) / 100
                conf = float(data.get("confidence", 30)) / 100
                reason = data.get("reasoning", "LLM analysis")

                # Clamp values
                prob = max(0.01, min(0.99, prob))
                conf = max(0.1, min(1.0, conf))

                return (prob, conf, reason)
            else:
                # Fallback: use sentiment data alone
                return self._sentiment_fallback(market_price, sentiment)

        except Exception as e:
            print(f"[PoliticsEcon] LLM error: {e}")
            return self._sentiment_fallback(market_price, sentiment)

    def _sentiment_fallback(
        self,
        market_price: float,
        sentiment: Optional[Dict],
    ) -> Tuple[Optional[float], float, str]:
        """
        Fallback when LLM is unavailable: use raw sentiment data.
        Low confidence since sentiment → probability mapping is crude.
        """
        if not sentiment:
            return (None, 0.0, "No sentiment data available")

        # Very rough heuristic: if sentiment is extreme, adjust price
        tone = sentiment.get("avg_tone", 0)
        normalized = sentiment.get("normalized_sentiment", 0.5)

        # Slight adjustment from market price based on sentiment
        adjustment = (normalized - 0.5) * 0.1  # ±5% adjustment
        fair_prob = max(0.01, min(0.99, market_price + adjustment))

        reasoning = (
            f"Sentiment fallback: tone={tone:.1f}, "
            f"normalized={normalized:.2f}"
        )

        return (fair_prob, 0.3, reasoning)  # Low confidence for raw sentiment