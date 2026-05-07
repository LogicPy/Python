"""
Market Scanner for Kalshi — discovers and categorizes event markets.

Flow:
  1. Fetch events via /events (gives category + event_ticker)
  2. For each event, fetch markets via /markets?event_ticker=...
  3. Parse into MarketInfo objects
  4. Filter for active, priced markets
"""

from __future__ import annotations
import logging
import time
from dataclasses import dataclass, field
from typing import List, Optional, Dict

import requests

logger = logging.getLogger("Scanner")

# ------------------------------------------------------------------ #
#  Kalshi v2 API category → our internal category mapping            #
# ------------------------------------------------------------------ #
CATEGORY_MAP: Dict[str, str] = {
    "Climate and Weather":      "weather",
    "Elections":                 "politics",
    "Politics":                  "politics",
    "Economics":                "economics",
    "Financials":                "economics",
    "Sports":                   "sports",
    "World":                    "world",
    "Science and Technology":   "science",
    "Health":                   "health",
    "Entertainment":            "entertainment",
    "Social":                   "social",
    "Companies":                "companies",
}

# Reverse map (internal → API category name for filtering)
REVERSE_CATEGORY_MAP: Dict[str, str] = {}
for api_cat, internal_cat in CATEGORY_MAP.items():
    REVERSE_CATEGORY_MAP.setdefault(internal_cat, []).append(api_cat)


# ------------------------------------------------------------------ #
#  MarketInfo dataclass                                              #
# ------------------------------------------------------------------ #
@dataclass
class MarketInfo:
    ticker: str
    title: str
    category: str = "uncategorized"
    yes_price: float = 0.0
    no_price: float = 1.0
    volume_24h: float = 0.0
    open_interest: float = 0.0
    status: str = "unknown"
    event_ticker: str = ""
    subtitle: str = ""
    close_time: str = ""
    expiry_time: str = ""


# ------------------------------------------------------------------ #
#  MarketScanner                                                     #
# ------------------------------------------------------------------ #
class MarketScanner:
    """Discover and categorize Kalshi markets via the v2 API."""

    BASE_URL = "https://api.elections.kalshi.com/trade-api/v2"

    def __init__(self, kalshi_config):
        self.config = kalshi_config
        self.api_key = kalshi_config.API_KEY
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
        })
        self._cache: List[MarketInfo] = []
        self._cache_time: float = 0.0
        self._cache_ttl: int = 120  # seconds
        logger.info("MarketScanner initialized")

    # ------------------------------------------------------------------ #
    #  API helpers                                                        #
    # ------------------------------------------------------------------ #
    def _get(self, endpoint: str, params: Optional[dict] = None) -> Optional[dict]:
        """GET request to Kalshi API."""
        url = f"{self.BASE_URL}/{endpoint}"
        try:
            r = self.session.get(url, params=params or {}, timeout=15)
            if r.status_code == 200:
                return r.json()
            logger.warning(f"API {endpoint} returned {r.status_code}: {r.text[:200]}")
            return None
        except Exception as e:
            logger.error(f"API {endpoint} error: {e}")
            return None

    def _fetch_events(self, limit: int = 80) -> List[dict]:
        """Fetch events via /events endpoint (gives category info)."""
        events = []
        cursor = None
        while len(events) < limit:
            params = {"limit": min(100, limit - len(events))}
            if cursor:
                params["cursor"] = cursor
            data = self._get("events", params)
            if not data:
                break
            batch = data.get("events", [])
            events.extend(batch)
            cursor = data.get("cursor")
            if not cursor or not batch:
                break
        return events

    def _fetch_markets_for_event(self, event_ticker: str, limit: int = 20) -> List[dict]:
        """Fetch all markets under an event."""
        data = self._get("markets", {"event_ticker": event_ticker, "limit": limit})
        if data:
            return data.get("markets", [])
        return []

    # ------------------------------------------------------------------ #
    #  Parsing                                                            #
    # ------------------------------------------------------------------ #
    @staticmethod
    def _parse_price(val) -> float:
        """Convert Kalshi price string to float. '0.4500' -> 0.45"""
        if val is None:
            return 0.0
        try:
            return float(val)
        except (ValueError, TypeError):
            return 0.0

    @classmethod
    def _parse_market(cls, raw: dict, category: str = "uncategorized") -> Optional[MarketInfo]:
        """Convert raw Kalshi API market dict → MarketInfo."""
        status = raw.get("status", "unknown")
        # Accept both 'active' and 'open' statuses
        # Kalshi uses different status values across API versions
        if status not in ("active", "open"):
            return None

        last_price = cls._parse_price(raw.get("last_price_dollars"))
        # Skip zero-price markets (no one is trading them)
        if last_price <= 0.0:
            return None

        ticker = raw.get("ticker", "")
        title = raw.get("title", "")
        subtitle = raw.get("yes_sub_title") or raw.get("no_sub_title") or ""

        return MarketInfo(
            ticker=ticker,
            title=title,
            category=category,
            yes_price=last_price,
            no_price=round(1.0 - last_price, 4),
            volume_24h=cls._parse_price(raw.get("volume_24h_fp")),
            open_interest=cls._parse_price(raw.get("open_interest_fp")),
            status=status,
            event_ticker=raw.get("event_ticker", ""),
            subtitle=subtitle,
            close_time=raw.get("close_time", ""),
            expiry_time=raw.get("expiry_time", ""),
        )

    # ------------------------------------------------------------------ #
    #  Scan methods                                                       #
    # ------------------------------------------------------------------ #
    def scan(self, limit: int = 50, category_filter: Optional[str] = None) -> List[MarketInfo]:
        """
        Discover Kalshi markets.
        
        Args:
            limit: Max markets to return
            category_filter: Internal category name (e.g. 'weather', 'politics')
        
        Returns:
            List of MarketInfo objects
        """
        # Check cache
        if self._cache and (time.time() - self._cache_time) < self._cache_ttl:
            markets = self._cache
        else:
            logger.info(f"Scanning up to {limit} Kalshi markets...")
            markets = self._full_scan(max_events=limit)
            self._cache = markets
            self._cache_time = time.time()

        # Apply category filter
        if category_filter:
            api_cats = REVERSE_CATEGORY_MAP.get(category_filter, [])
            markets = [m for m in markets if m.category in api_cats or m.category == category_filter]

        # Sort by volume (most active first) and limit
        markets.sort(key=lambda m: m.volume_24h, reverse=True)
        markets = markets[:limit]

        logger.info(f"Found {len(markets)} markets"
                     + (f" in category '{category_filter}'" if category_filter else ""))
        return markets

    def _full_scan(self, max_events: int = 100) -> List[MarketInfo]:
        """Full scan: fetch events, then markets per event."""
        markets: List[MarketInfo] = []
        events = self._fetch_events(limit=max_events)
        logger.info(f"Found {len(events)} events, fetching markets...")

        for i, ev in enumerate(events):
            if len(markets) >= max_events * 3:  # Cap total markets
                break

            event_ticker = ev.get("event_ticker", "")
            api_category = ev.get("category", "uncategorized")
            internal_category = CATEGORY_MAP.get(api_category, "uncategorized")

            raw_markets = self._fetch_markets_for_event(event_ticker)
            for rm in raw_markets:
                mi = self._parse_market(rm, category=internal_category)
                if mi:
                    markets.append(mi)

            # Rate limit: delay between event fetches to avoid 429s
            time.sleep(0.15)

        return markets

    def get_by_category(self, category: str, limit: int = 20) -> List[MarketInfo]:
        """Shortcut: scan with a category filter."""
        return self.scan(limit=limit, category_filter=category)

    # ------------------------------------------------------------------ #
    #  Convenience                                                        #
    # ------------------------------------------------------------------ #
    def list_categories(self) -> Dict[str, int]:
        """Return dict of internal_category → market count."""
        if not self._cache:
            self.scan(limit=100)
        counts: Dict[str, int] = {}
        for m in self._cache:
            counts[m.category] = counts.get(m.category, 0) + 1
        return dict(sorted(counts.items(), key=lambda x: -x[1]))

    def search_ticker(self, ticker: str) -> Optional[MarketInfo]:
        """Find a specific market by ticker prefix."""
        if not self._cache:
            self.scan(limit=100)
        for m in self._cache:
            if m.ticker.startswith(ticker.upper()):
                return m
        return None

    def clear_cache(self):
        """Force a fresh scan on next call."""
        self._cache = []
        self._cache_time = 0.0