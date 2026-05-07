"""
Kalshi API Client with RSA-PSS authenticated requests.
Handles market data retrieval and order placement.

AUTHENTICATION: Kalshi V2 uses per-request signing — NO login endpoint.
Every authenticated request includes 3 headers:
  - KALSHI-ACCESS-KEY: Your API Key ID
  - KALSHI-ACCESS-TIMESTAMP: Current time in milliseconds
  - KALSHI-ACCESS-SIGNATURE: RSA-PSS signature of {timestamp}{method}{path}

Public endpoints (like market data) work without auth.
Private endpoints (like portfolio/orders) require auth headers.
"""

import json
import time
import base64
import hmac
import hashlib
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from pathlib import Path

import requests
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

from .config import KalshiConfig, SYMBOL_MAP


class KalshiClient:
    """
    Authenticated client for the Kalshi Trade API v2.

    Uses per-request RSA-PSS signing. No session/login endpoint needed.
    Each request is individually authenticated with signed headers.

    Auto-detects the correct API base URL by trying all known endpoints
    if the primary one fails.
    """

    def __init__(self, config: Optional[KalshiConfig] = None):
        self.config = config or KalshiConfig()
        self.api_key = self.config.API_KEY
        self.private_key_pem = self.config.get_private_key()
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
        })
        self._authenticated = False
        self._user_id: Optional[str] = None
        self._working_base_url: Optional[str] = None

        # Try to find a working base URL
        self.base_url = self._find_working_base_url()

    def _find_working_base_url(self) -> str:
        """
        Try all known Kalshi API URLs to find one that works.

        We test by hitting a public endpoint (market data) first,
        then if auth is available, verify auth works too.
        """
        primary_url = self.config.get_base_url()

        # If we already know the working URL, use it
        if self._working_base_url:
            return self._working_base_url

        urls_to_try = self.config.get_all_possible_urls()

        for url in urls_to_try:
            try:
                # Test with a lightweight public endpoint
                test_resp = self.session.get(
                    f"{url}/markets?limit=1",
                    timeout=8,
                )
                if test_resp.status_code in (200, 401):
                    # 200 = working, 401 = server is there but needs auth
                    print(f"[KalshiClient] Working API found: {url}")
                    self._working_base_url = url
                    return url
                elif test_resp.status_code == 404:
                    print(f"[KalshiClient] {url} — 404, trying next...")
                    continue
                else:
                    print(f"[KalshiClient] {url} — status {test_resp.status_code}, trying next...")
                    continue
            except requests.exceptions.RequestException as e:
                print(f"[KalshiClient] {url} — connection failed: {type(e).__name__}")
                continue

        # Fallback to primary even if it didn't respond
        print(f"[KalshiClient] WARNING: No responsive API found, using primary: {primary_url}")
        return primary_url

    # ── Authentication ─────────────────────────────────────────────

    # The API path prefix that must be included in the signing message.
    # Kalshi requires the FULL path (e.g., /trade-api/v2/portfolio/balance)
    # in the signature, NOT just the endpoint path (/portfolio/balance).
    API_PATH_PREFIX = "/trade-api/v2"

    def _sign_request(self, timestamp_ms: str, method: str, path: str) -> str:
        """
        Sign a request using RSA-PSS with SHA-256.

        The message to sign is: {timestamp_ms}{method}{path}

        IMPORTANT: The request body is NOT included in the signing message,
        even for POST/PUT requests. This is confirmed by the official Kalshi
        documentation at:
          https://docs.kalshi.com/getting_started/quick_start_authenticated_requests
        and the official SDK code (pykalshi, kalshi-js-sdk).

        The path MUST include the API prefix (/trade-api/v2/...).
        Query parameters should NOT be included in the signing path.

        RSA-PSS parameters must match Kalshi's expectations:
          - MGF1 with SHA-256
          - salt_length = PSS.DIGEST_LENGTH (32 bytes for SHA-256)
          Using MAX_LENGTH or AUTO will produce INVALID signatures.
        """
        # Strip query parameters from path before signing
        path_without_query = path.split("?")[0]

        # Prepend the API path prefix if not already present
        if not path_without_query.startswith(self.API_PATH_PREFIX):
            sign_path = f"{self.API_PATH_PREFIX}{path_without_query}"
        else:
            sign_path = path_without_query

        message = f"{timestamp_ms}{method}{sign_path}"

        # Load the private key
        try:
            private_key = serialization.load_pem_private_key(
                self.private_key_pem.encode(),
                password=None,
            )
        except (ValueError, TypeError) as e:
            print(f"[KalshiClient] Failed to load private key: {e}")
            print(f"[KalshiClient] Key starts with: {self.private_key_pem[:50]}...")
            raise

        # Sign with RSA-PSS (must use DIGEST_LENGTH, NOT MAX_LENGTH)
        signature = private_key.sign(
            message.encode("utf-8"),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.DIGEST_LENGTH,
            ),
            hashes.SHA256(),
        )

        return base64.b64encode(signature).decode("utf-8")

    def _get_auth_headers(self, method: str, path: str) -> Dict[str, str]:
        """Generate authenticated headers for a request.

        The signing format is: {timestamp_ms}{method}{path}
        The body is NOT included in the signature (confirmed by official docs).
        """
        timestamp_ms = str(int(time.time() * 1000))
        signature = self._sign_request(timestamp_ms, method, path)

        return {
            "KALSHI-ACCESS-KEY": self.api_key,
            "KALSHI-ACCESS-SIGNATURE": signature,
            "KALSHI-ACCESS-TIMESTAMP": timestamp_ms,
        }

    def login(self) -> bool:
        """
        Verify authentication works by making a test request.

        Kalshi V2 has NO /login endpoint. Instead, we verify auth
        by calling /portfolio/balance with signed headers.
        If it succeeds, we know our keys are valid.

        If auth fails on one URL, we try all known URLs to find
        one that accepts our credentials.
        """
        if not self.api_key:
            print("[KalshiClient] No API key configured — skipping auth")
            return False

        # Try each known base URL for authentication
        urls_to_try = self.config.get_all_possible_urls()

        for url in urls_to_try:
            result = self._try_auth_on_url(url)
            if result:
                self._working_base_url = url
                self.base_url = url
                return True

        print("[KalshiClient] Auth FAILED on all known API URLs")
        print("[KalshiClient] Possible causes:")
        print("  1. Your API key might be for a different environment (demo vs prod)")
        print("  2. Your private key might not match the API key")
        print("  3. Your API key might be expired or revoked")
        return False

    def _try_auth_on_url(self, base_url: str) -> bool:
        """Try to authenticate against a specific base URL."""
        # Try /portfolio/balance first
        auth_endpoints = [
            "/portfolio/balance",
            "/portfolio",
            "/user/self",
        ]

        for path in auth_endpoints:
            try:
                headers = self._get_auth_headers("GET", path)
                resp = self.session.get(
                    f"{base_url}{path}",
                    headers=headers,
                    timeout=10,
                )

                if resp.status_code == 200:
                    data = resp.json()
                    self._authenticated = True
                    balance = data.get("balance", "N/A")
                    print(f"[KalshiClient] Auth verified on {base_url}!")
                    if balance != "N/A":
                        print("[KalshiClient] Balance: $" + str(balance))
                    return True

                elif resp.status_code == 401:
                    # Auth failed — wrong key for this URL
                    resp_text = resp.text[:200]
                    print(f"[KalshiClient] Auth rejected on {base_url}{path}: {resp_text}")
                    # Don't try more endpoints on this URL if key is rejected
                    return False

                elif resp.status_code == 404:
                    # Endpoint doesn't exist but auth headers might be OK
                    print(f"[KalshiClient] 404 on {base_url}{path} — trying next endpoint")
                    continue

                else:
                    # Other status codes — might still be OK
                    resp_text = resp.text[:200]
                    print(f"[KalshiClient] Status {resp.status_code} on {base_url}{path}: {resp_text}")
                    # If it's not 401, auth headers were probably accepted
                    if resp.status_code != 401:
                        self._authenticated = True
                        print(f"[KalshiClient] Assuming auth OK (non-401 response)")
                        return True

            except requests.exceptions.RequestException as e:
                print(f"[KalshiClient] Connection failed to {base_url}: {type(e).__name__}")
                return False

        # Tried all endpoints on this URL — none worked
        return False

    def _ensure_auth(self) -> bool:
        """Ensure authentication has been verified."""
        if self._authenticated:
            return True
        return self.login()

    def test_post_auth(self) -> bool:
        """
        Test that POST request authentication works.

        GET requests to /portfolio/balance work fine, but POST
        requests to /portfolio/orders fail with 401. This method
        tests POST auth by trying to get positions (which is a GET
        but we explicitly test with the direct requests approach).

        Returns True if auth works for all methods.
        """
        print(f"[KalshiClient] Testing POST authentication...")

        # Test 1: Verify GET still works with direct requests
        path = "/portfolio/balance"
        auth_headers = self._get_auth_headers("GET", path)
        all_headers = {
            "Accept": "application/json",
            "KALSHI-ACCESS-KEY": auth_headers["KALSHI-ACCESS-KEY"],
            "KALSHI-ACCESS-SIGNATURE": auth_headers["KALSHI-ACCESS-SIGNATURE"],
            "KALSHI-ACCESS-TIMESTAMP": auth_headers["KALSHI-ACCESS-TIMESTAMP"],
        }
        try:
            resp = requests.get(
                f"{self.base_url}{path}",
                headers=all_headers,
                timeout=10,
            )
            if resp.status_code == 200:
                bal = resp.json().get('balance', 'N/A')
                print("[KalshiClient] GET auth: OK (balance: $" + str(bal) + ")")
            else:
                print(f"[KalshiClient] GET auth: FAILED ({resp.status_code}: {resp.text[:200]})")
                return False
        except Exception as e:
            print(f"[KalshiClient] GET auth: ERROR ({e})")
            return False

        # Test 2: Try a POST with a dummy order body
        # This should return 400 (bad ticker) if auth works, or 401 if auth fails
        path = "/portfolio/orders"
        body_dict = {
            "ticker": "TEST_AUTH_CHECK_12345",
            "action": "buy",
            "side": "yes",
            "count": 1,
            "type": "market",
        }
        result = self._send_authenticated_post(path, body_dict)

        if result is not None:
            print(f"[KalshiClient] POST auth: OK (order endpoint reachable)")
            return True

        # If the result is None but we got a 400, auth still works
        # (the test_post_auth returned None because of the 400 error)
        # Let's try again and check the actual response code
        body_json = json.dumps(body_dict, separators=(",", ":"))
        auth_headers = self._get_auth_headers("POST", path)
        all_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "KALSHI-ACCESS-KEY": auth_headers["KALSHI-ACCESS-KEY"],
            "KALSHI-ACCESS-SIGNATURE": auth_headers["KALSHI-ACCESS-SIGNATURE"],
            "KALSHI-ACCESS-TIMESTAMP": auth_headers["KALSHI-ACCESS-TIMESTAMP"],
        }
        try:
            resp = requests.post(
                f"{self.base_url}{path}",
                data=body_json,
                headers=all_headers,
                timeout=15,
            )
            # Any non-401 response means auth passed
            if resp.status_code != 401:
                print(f"[KalshiClient] POST auth: OK (got {resp.status_code}, auth passed)")
                print(f"  Response: {resp.text[:200]}")
                return True
            else:
                print(f"[KalshiClient] POST auth: FAILED (401 Unauthorized)")
                print(f"  Response: {resp.text[:200]}")
                return False
        except Exception as e:
            print(f"[KalshiClient] POST auth: ERROR ({e})")
            return False

    # ── Market Data (Public — no auth needed) ──────────────────────

    def get_active_markets(self, series_ticker: str) -> List[Dict[str, Any]]:
        """
        Get all active markets for a series (e.g., 'KXHIGHNY', 'KXBTC15M').

        This is a PUBLIC endpoint — works without authentication.
        Returns a list of market objects with tickers, strike prices,
        last prices (probabilities), and close times.

        Uses the `series_ticker` query parameter which returns ALL markets
        in a series (e.g., all temperature brackets for a city on a date).
        Supports cursor-based pagination to get all results.
        """
        all_markets: List[Dict[str, Any]] = []

        # Try multiple status filters — different Kalshi versions use different terms
        # "open" first since it's the most common current status
        for status_filter in ["open", "active", ""]:
            params: Dict[str, Any] = {
                "series_ticker": series_ticker,
                "limit": 200,
            }
            if status_filter:
                params["status"] = status_filter

            all_markets = []
            cursor = None

            while True:
                if cursor:
                    params["cursor"] = cursor

                try:
                    headers = {}
                    if self.api_key and self._authenticated:
                        # Sign the base path (without query params)
                        headers = self._get_auth_headers("GET", "/markets")

                    resp = self.session.get(
                        f"{self.base_url}/markets",
                        params=params,
                        headers=headers,
                        timeout=10,
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    batch = data.get("markets", [])
                    all_markets.extend(batch)

                    # Pagination
                    cursor = data.get("cursor")
                    if not cursor or not batch:
                        break

                except requests.exceptions.RequestException as e:
                    # If this status filter fails, try the next one
                    break

            if all_markets:
                print(f"[KalshiClient] Found {len(all_markets)} markets for {series_ticker} (status={status_filter or 'all'})")
                return all_markets

        print(f"[KalshiClient] No markets found for series {series_ticker}")
        return []

    def get_markets(
        self,
        limit: int = 200,
        cursor: Optional[int] = None,
        category: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Browse all Kalshi markets with optional filtering and pagination.

        This is a PUBLIC endpoint — works without authentication.
        Hits the /markets endpoint with query parameters.

        Args:
            limit: Maximum number of markets to return (default 200, max 200).
            cursor: Pagination cursor for fetching next page.
            category: Optional category filter (e.g., 'weather', 'politics').

        Returns:
            List of raw market dicts from the Kalshi API.
        """
        all_markets: List[Dict[str, Any]] = []
        params: Dict[str, Any] = {"limit": min(limit, 200)}
        if cursor is not None:
            params["cursor"] = cursor
        if category:
            params["group"] = category  # Kalshi uses 'group' for categories

        remaining = limit

        while remaining > 0:
            params["limit"] = min(remaining, 200)
            try:
                headers = {}
                if self.api_key and self._authenticated:
                    headers = self._get_auth_headers("GET", "/markets")

                resp = self.session.get(
                    f"{self.base_url}/markets",
                    params=params,
                    headers=headers,
                    timeout=10,
                )
                resp.raise_for_status()

                data = resp.json()
                batch = data.get("markets", [])
                all_markets.extend(batch)
                remaining -= len(batch)

                # Pagination — follow cursor if more results available
                next_cursor = data.get("cursor")
                if not next_cursor or len(batch) == 0:
                    break
                params["cursor"] = next_cursor

            except Exception as e:
                print(f"[KalshiClient] get_markets error: {e}")
                break

        return all_markets

    def get_market_orderbook(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Get the order book for a specific market ticker.
        Returns bid/ask data including prices and sizes.
        """
        path = f"/markets/{ticker}/orderbook"

        try:
            headers = {}
            if self.api_key and self._authenticated:
                headers = self._get_auth_headers("GET", path)

            resp = self.session.get(
                f"{self.base_url}{path}",
                headers=headers,
                timeout=10,
            )
            resp.raise_for_status()
            return resp.json()

        except requests.exceptions.RequestException as e:
            print(f"[KalshiClient] Failed to get orderbook for {ticker}: {e}")
            return None

    def get_market_price(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Get current price data for a specific market.
        Includes last_price, bid, ask volumes.

        For ACTIVE markets, uses /markets/{ticker}.
        For CLOSED/FINALIZED markets (which 404), falls back to
        searching the series endpoint.
        """
        path = f"/markets/{ticker}"

        try:
            headers = {}
            if self.api_key and self._authenticated:
                headers = self._get_auth_headers("GET", path)

            resp = self.session.get(
                f"{self.base_url}{path}",
                headers=headers,
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("market", data)

        except requests.exceptions.HTTPError as e:
            if e.response is not None and e.response.status_code == 404:
                # Market may be closed/finalized — try the series fallback
                result = self._get_settled_market(ticker)
                if result:
                    return result
            print(f"[KalshiClient] Failed to get price for {ticker}: {e}")
            return None

        except requests.exceptions.RequestException as e:
            print(f"[KalshiClient] Failed to get price for {ticker}: {e}")
            return None

    def _get_settled_market(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Look up a settled/finalized market by searching its series.

        When /markets/{ticker} returns 404, the market has likely been
        finalized and removed from the direct endpoint. We can still find
        it by querying the series endpoint, which includes past markets.

        Args:
            ticker: Full market ticker (e.g., 'KXBTC15M-26MAY041945-15')

        Returns:
            Market data dict or None if not found.
        """
        # Extract series ticker from the full ticker
        # Format: KXBTC15M-26MAY041945-15 → KXBTC15M
        parts = ticker.split("-")
        if len(parts) < 2:
            return None

        series_ticker = parts[0]

        # Query the series for ALL markets (including finalized)
        # Try multiple status filters to find the market
        for status_filter in ["", "closed", "finalized", "settled"]:
            path = f"/markets?series_ticker={series_ticker}&limit=100"
            if status_filter:
                path += f"&status={status_filter}"

            try:
                headers = {}
                if self.api_key and self._authenticated:
                    headers = self._get_auth_headers("GET", path)

                resp = self.session.get(
                    f"{self.base_url}{path}",
                    headers=headers,
                    timeout=10,
                )
                if resp.status_code != 200:
                    continue

                data = resp.json()
                markets = data.get("markets", [])

                for market in markets:
                    if market.get("ticker") == ticker:
                        print(f"[KalshiClient] Found settled market via series: {ticker}")
                        return market

            except requests.exceptions.RequestException:
                continue

        # Try the events endpoint as another fallback
        # Some Kalshi versions expose settled markets via /events
        try:
            path = f"/events?series_ticker={series_ticker}&limit=50"
            headers = {}
            if self.api_key and self._authenticated:
                headers = self._get_auth_headers("GET", path)

            resp = self.session.get(
                f"{self.base_url}{path}",
                headers=headers,
                timeout=10,
            )
            if resp.status_code == 200:
                events = resp.json().get("events", [])
                for event in events:
                    for market in event.get("markets", []):
                        if market.get("ticker") == ticker:
                            print(f"[KalshiClient] Found settled market via events: {ticker}")
                            return market
        except requests.exceptions.RequestException:
            pass

        print(f"[KalshiClient] Could not find settled market {ticker} via any fallback")
        return None

    # ── Order Management (Requires Auth) ───────────────────────────

    def _send_authenticated_post(self, path: str, body_dict: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Send an authenticated POST request.

        IMPORTANT DISCOVERY: Kalshi's API does NOT include the request body
        in the signing message. The signing format is:
            {timestamp}{method}{path}
        NOT:
            {timestamp}{method}{path}{body}

        This is different from many other API exchanges (like Coinbase, Binance)
        which DO include the body. The body is still sent in the request, but
        it's NOT part of the signature computation.
        """
        body_json = json.dumps(body_dict, separators=(",", ":"))

        # Sign WITHOUT the body — Kalshi doesn't include body in signature
        auth_headers = self._get_auth_headers("POST", path)

        all_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "KALSHI-ACCESS-KEY": auth_headers["KALSHI-ACCESS-KEY"],
            "KALSHI-ACCESS-SIGNATURE": auth_headers["KALSHI-ACCESS-SIGNATURE"],
            "KALSHI-ACCESS-TIMESTAMP": auth_headers["KALSHI-ACCESS-TIMESTAMP"],
        }

        sign_path = path if path.startswith(self.API_PATH_PREFIX) else f"{self.API_PATH_PREFIX}{path}"

        try:
            resp = requests.post(
                f"{self.base_url}{path}",
                data=body_json,
                headers=all_headers,
                timeout=15,
            )

            if resp.status_code == 401:
                # Auth failed — log detailed diagnostics
                print(f"[KalshiClient] 401 AUTH FAILED on POST {path}")
                print(f"  Response: {resp.text[:500]}")
                print(f"  Signed message: {auth_headers['KALSHI-ACCESS-TIMESTAMP']}POST{sign_path}")
                print(f"  Body sent: {body_json[:200]}")

            resp.raise_for_status()
            return resp.json()

        except requests.exceptions.RequestException as e:
            print(f"[KalshiClient] POST failed: {e}")
            if hasattr(e, "response") and e.response is not None:
                print(f"  Response: {e.response.text[:500]}")
            return None

    def create_order(self, ticker: str, side: str, count: int,
                     price: Optional[float] = None,
                     action: str = "buy") -> Optional[Dict[str, Any]]:
        """
        Place an order on a Kalshi market.

        Args:
            ticker: Market ticker (e.g., 'KXBTC15M-26MAY040915')
            side: 'yes' or 'no'
            count: Number of contracts
            price: Price per contract in cents (1-99). If None, market order.
            action: 'buy' or 'sell' (default: 'buy')

        Returns:
            Order response dict or None on failure.
        """
        path = "/portfolio/orders"
        body_dict = {
            "ticker": ticker,
            "action": action,
            "side": side,
            "count": count,
            "type": "limit" if price else "market",
        }

        if price is not None:
            body_dict["yes_price"] = int(price) if side == "yes" else None
            body_dict["no_price"] = int(price) if side == "no" else None
            body_dict = {k: v for k, v in body_dict.items() if v is not None}

        result = self._send_authenticated_post(path, body_dict)
        if result:
            print(f"[KalshiClient] Order placed: {action} {side} {count}x {ticker} @ {price}")
        return result

    def create_order_v2(self, ticker: str, side: str, count_fp: str,
                        price_fp: str, action: str = "buy") -> Optional[Dict[str, Any]]:
        """
        Place a V2 order with fixed-point dollar prices.

        Args:
            ticker: Market ticker
            side: 'yes' or 'no'
            count_fp: Contract count as string (e.g., "10.00")
            price_fp: Price per contract as string dollar amount (e.g., "0.55")
            action: 'buy' or 'sell' (default: 'buy')

        Returns:
            Order response dict or None on failure.
        """
        path = "/portfolio/orders/v2"
        body_dict = {
            "ticker": ticker,
            "action": action,
            "side": side,
            "count_fp": count_fp,
            "price_fp": price_fp,
        }

        result = self._send_authenticated_post(path, body_dict)
        if result:
            print(f"[KalshiClient] V2 Order placed: {action} {side} {count_fp}x {ticker} @ $" + str(price_fp))
        return result

    def cancel_order(self, order_id: str) -> bool:
        """Cancel an existing order by ID."""
        path = f"/portfolio/orders/{order_id}"
        auth_headers = self._get_auth_headers("DELETE", path)

        # Use requests.delete() directly to avoid session interference
        all_headers = {
            "Accept": "application/json",
            "KALSHI-ACCESS-KEY": auth_headers["KALSHI-ACCESS-KEY"],
            "KALSHI-ACCESS-SIGNATURE": auth_headers["KALSHI-ACCESS-SIGNATURE"],
            "KALSHI-ACCESS-TIMESTAMP": auth_headers["KALSHI-ACCESS-TIMESTAMP"],
        }

        try:
            resp = requests.delete(
                f"{self.base_url}{path}",
                headers=all_headers,
                timeout=10,
            )
            resp.raise_for_status()
            print(f"[KalshiClient] Order cancelled: {order_id}")
            return True

        except requests.exceptions.RequestException as e:
            print(f"[KalshiClient] Cancel failed for {order_id}: {e}")
            return False

    def get_positions(self) -> List[Dict[str, Any]]:
        """Get all current positions."""
        path = "/portfolio/positions"
        auth_headers = self._get_auth_headers("GET", path)

        # Use requests.get() directly to be consistent with POST auth
        all_headers = {
            "Accept": "application/json",
            "KALSHI-ACCESS-KEY": auth_headers["KALSHI-ACCESS-KEY"],
            "KALSHI-ACCESS-SIGNATURE": auth_headers["KALSHI-ACCESS-SIGNATURE"],
            "KALSHI-ACCESS-TIMESTAMP": auth_headers["KALSHI-ACCESS-TIMESTAMP"],
        }

        try:
            resp = requests.get(
                f"{self.base_url}{path}",
                headers=all_headers,
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("positions", [])

        except requests.exceptions.RequestException as e:
            print(f"[KalshiClient] Failed to get positions: {e}")
            return []

    def get_balance(self) -> Optional[Dict[str, Any]]:
        """Get account balance."""
        path = "/portfolio/balance"
        auth_headers = self._get_auth_headers("GET", path)

        all_headers = {
            "Accept": "application/json",
            "KALSHI-ACCESS-KEY": auth_headers["KALSHI-ACCESS-KEY"],
            "KALSHI-ACCESS-SIGNATURE": auth_headers["KALSHI-ACCESS-SIGNATURE"],
            "KALSHI-ACCESS-TIMESTAMP": auth_headers["KALSHI-ACCESS-TIMESTAMP"],
        }

        try:
            resp = requests.get(
                f"{self.base_url}{path}",
                headers=all_headers,
                timeout=10,
            )
            resp.raise_for_status()
            return resp.json()

        except requests.exceptions.RequestException as e:
            print(f"[KalshiClient] Failed to get balance: {e}")
            return None

    # ── Convenience Methods ────────────────────────────────────────

    def find_15min_contracts(self, symbol: str) -> Dict[str, Any]:
        """
        Find the current 15-minute contract for a crypto symbol.

        Kalshi 15-min markets are SINGLE binary contracts:
        - Title: "BTC price up in next 15 mins?"
        - YES = price will be >= floor_strike at close → "UP"
        - NO  = price will be < floor_strike at close → "DOWN"
        - floor_strike = the target/strike price
        """
        info = SYMBOL_MAP.get(symbol)
        if not info:
            print(f"[KalshiClient] Unknown symbol: {symbol}")
            return {}

        series_ticker = info["kalshi_series"]

        # First try active markets, then fall back to all markets
        markets = self.get_active_markets(series_ticker)

        if not markets:
            # Try getting all markets and filtering for active/upcoming
            path = f"/markets?series_ticker={series_ticker}&limit=100"
            try:
                headers = {}
                if self.api_key and self._authenticated:
                    headers = self._get_auth_headers("GET", path)

                resp = self.session.get(
                    f"{self.base_url}{path}",
                    headers=headers,
                    timeout=10,
                )
                resp.raise_for_status()
                all_markets = resp.json().get("markets", [])
            except Exception:
                all_markets = []

            now = datetime.now(timezone.utc)
            markets = []
            for m in all_markets:
                status = m.get("status", "")
                close_str = m.get("close_time", "")
                if status == "active":
                    markets.append(m)
                elif status not in ("finalized", "closed"):
                    try:
                        close_time = datetime.fromisoformat(close_str.replace("Z", "+00:00"))
                        if close_time > now:
                            markets.append(m)
                    except Exception:
                        pass

        if not markets:
            print(f"[KalshiClient] No active/upcoming markets for {series_ticker}")
            return {}

        # Find the nearest closing market (the current 15-min window)
        now = datetime.now(timezone.utc)
        nearest = None
        min_time_diff = float("inf")

        for market in markets:
            close_time_str = market.get("close_time", "")
            if not close_time_str:
                continue
            try:
                close_time = datetime.fromisoformat(
                    close_time_str.replace("Z", "+00:00")
                )
                time_diff = (close_time - now).total_seconds()
                if 0 < time_diff < min_time_diff:
                    min_time_diff = time_diff
                    nearest = market
            except (ValueError, TypeError):
                continue

        if not nearest:
            print(f"[KalshiClient] No upcoming 15-min window found for {symbol}")
            return {}

        # Extract contract information
        # Kalshi 15-min is a SINGLE binary: "BTC price up in next 15 mins?"
        # YES = price >= floor_strike → "UP"
        # NO  = price < floor_strike → "DOWN"
        yes_price = float(nearest.get("last_price_dollars", 0) or 0)
        no_price = round(1.0 - yes_price, 4)

        # Kalshi order prices must be WHOLE CENTS (1-99)
        # Use ask prices for buying (what you pay), bid prices for reference
        yes_ask = float(nearest.get("yes_ask_dollars", 0) or 0)
        no_ask = float(nearest.get("no_ask_dollars", 0) or 0)
        yes_bid = float(nearest.get("yes_bid_dollars", 0) or 0)
        no_bid = float(nearest.get("no_bid_dollars", 0) or 0)

        # Convert to whole cents for order placement
        # Ask = what you pay to buy, Bid = what you'd get to sell
        # If no ask available, use last_price as fallback
        yes_ask_cents = max(1, min(99, round(yes_ask * 100))) if yes_ask > 0 else max(1, min(99, round(yes_price * 100)))
        no_ask_cents = max(1, min(99, round(no_ask * 100))) if no_ask > 0 else max(1, min(99, round(no_price * 100)))
        yes_last_cents = max(1, min(99, round(yes_price * 100)))
        no_last_cents = max(1, min(99, round(no_price * 100)))

        result = {
            "symbol": symbol,
            "series_ticker": series_ticker,
            "market_ticker": nearest.get("ticker", ""),
            "title": nearest.get("title", ""),
            "yes_sub_title": nearest.get("yes_sub_title", ""),
            "no_sub_title": nearest.get("no_sub_title", ""),
            "close_time": nearest.get("close_time", ""),
            "floor_strike": float(nearest.get("floor_strike", 0) or 0),
            "target_price": float(nearest.get("floor_strike", 0) or 0),
            # Price data (in dollars, $0.55 = 55% probability)
            "yes_price_dollars": yes_price,
            "no_price_dollars": no_price,
            "yes_ask_dollars": yes_ask,
            "no_ask_dollars": no_ask,
            "yes_bid_dollars": yes_bid,
            "no_bid_dollars": no_bid,
            # Order placement prices (WHOLE CENTS, 1-99)
            # up_price = YES price (buy YES for UP prediction)
            # down_price = NO price (buy NO for DOWN prediction)
            "up_ticker": nearest.get("ticker", ""),   # Buy YES for UP
            "down_ticker": nearest.get("ticker", ""),  # Same ticker, buy NO for DOWN
            "up_price": yes_last_cents,       # YES price in whole cents
            "down_price": no_last_cents,      # NO price in whole cents
            "up_ask_cents": yes_ask_cents,    # YES ask in whole cents (for buying)
            "down_ask_cents": no_ask_cents,   # NO ask in whole cents (for buying)
            # Timing
            "time_remaining_sec": min_time_diff,
            "status": nearest.get("status", ""),
            "result": nearest.get("result"),
            # Market metadata
            "volume_fp": nearest.get("volume_fp", "0"),
            "open_interest_fp": nearest.get("open_interest_fp", "0"),
            "strike_type": nearest.get("strike_type", "greater_or_equal"),
        }

        return result

    def get_implied_price(self, symbol: str) -> Optional[float]:
        """
        Get the Kalshi implied price for a crypto symbol using
        the 50% crossover interpolation method (same as the predictor).
        """
        info = SYMBOL_MAP.get(symbol)
        if not info:
            return None

        series_ticker = info["kalshi_series"]
        markets = self.get_active_markets(series_ticker)

        if not markets:
            return None

        # Group markets by their parent event to find strike prices
        strikes = []
        for market in markets:
            subtitle = market.get("subtitle", "") or ""
            last_price = market.get("last_price")

            if last_price is None:
                continue

            try:
                import re
                amounts = re.findall(r'\$([\d,]+\.?\d*)', subtitle)
                if amounts:
                    strike = float(amounts[0].replace(',', ''))
                    prob = last_price / 100.0
                    direction = "above" if "above" in subtitle.lower() else "below"
                    strikes.append({
                        "strike": strike,
                        "prob": prob,
                        "direction": direction,
                    })
            except (ValueError, IndexError):
                continue

        if not strikes:
            return None

        strikes.sort(key=lambda x: x["strike"])

        for i in range(len(strikes) - 1):
            s1, s2 = strikes[i], strikes[i + 1]
            if s1["direction"] == "above" and s2["direction"] == "above":
                if s1["prob"] >= 0.5 and s2["prob"] < 0.5:
                    ratio = (s1["prob"] - 0.5) / (s1["prob"] - s2["prob"])
                    implied = s1["strike"] + ratio * (s2["strike"] - s1["strike"])
                    return implied

        if strikes:
            closest = min(strikes, key=lambda x: abs(x["prob"] - 0.5))
            return closest["strike"]

        return None
