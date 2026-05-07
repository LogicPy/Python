"""
Rate Limiter with Exponential Backoff for API calls.

Prevents 429 (Too Many Requests) errors by:
1. Enforcing a minimum interval between requests
2. Exponential backoff on 429/5xx responses
3. Jitter to prevent thundering herd
4. Per-domain rate tracking
"""

import time
import random
import threading
from typing import Dict, Optional
from collections import defaultdict


class RateLimiter:
    """
    Thread-safe rate limiter with exponential backoff.

    Usage:
        limiter = RateLimiter(min_interval=0.5, max_backoff=30.0)

        # Before each API call:
        limiter.wait("api.elections.kalshi.com")

        # After a 429 response:
        limiter.backoff("api.elections.kalshi.com")

        # After a successful response:
        limiter.reset("api.elections.kalshi.com")
    """

    def __init__(
        self,
        min_interval: float = 0.5,     # Min seconds between requests per domain
        max_backoff: float = 60.0,       # Max backoff time in seconds
        initial_backoff: float = 1.0,    # First backoff duration
        backoff_factor: float = 2.0,     # Multiply backoff by this each time
        jitter_range: float = 0.1,       # Add random jitter (0-0.1s)
    ):
        self.min_interval = min_interval
        self.max_backoff = max_backoff
        self.initial_backoff = initial_backoff
        self.backoff_factor = backoff_factor
        self.jitter_range = jitter_range

        # Per-domain state
        self._last_request: Dict[str, float] = defaultdict(float)
        self._backoff_level: Dict[str, int] = defaultdict(int)
        self._current_backoff: Dict[str, float] = defaultdict(float)
        self._lock = threading.Lock()

    def wait(self, domain: str):
        """
        Wait the appropriate amount of time before making a request
        to the given domain. Call this BEFORE each API request.
        """
        with self._lock:
            now = time.time()

            # Apply any active backoff first
            current_backoff = self._current_backoff.get(domain, 0.0)
            if current_backoff > 0:
                backoff_wait = current_backoff
                self._current_backoff[domain] = 0.0  # Reset after applying
            else:
                backoff_wait = 0.0

            # Calculate time since last request
            last_time = self._last_request.get(domain, 0.0)
            elapsed = now - last_time
            min_wait = max(0.0, self.min_interval - elapsed)

            # Total wait = backoff + min_interval + jitter
            total_wait = backoff_wait + min_wait + random.uniform(0, self.jitter_range)

        # Sleep outside the lock
        if total_wait > 0:
            time.sleep(total_wait)

        with self._lock:
            self._last_request[domain] = time.time()

    def backoff(self, domain: str):
        """
        Trigger exponential backoff after a 429 or 5xx response.
        Call this AFTER receiving a rate-limited response.
        """
        with self._lock:
            level = self._backoff_level.get(domain, 0)
            level += 1
            self._backoff_level[domain] = level

            # Exponential backoff with jitter
            backoff_time = min(
                self.initial_backoff * (self.backoff_factor ** (level - 1)),
                self.max_backoff
            )
            # Add jitter (±20%)
            jitter = backoff_time * random.uniform(-0.2, 0.2)
            self._current_backoff[domain] = max(0.1, backoff_time + jitter)

            print(f"[RateLimiter] 429 backoff on {domain}: "
                  f"level={level}, wait={self._current_backoff[domain]:.1f}s")

    def reset(self, domain: str):
        """
        Reset backoff after a successful response.
        Call this AFTER receiving a 200 response.
        """
        with self._lock:
            # Gradual reset: reduce level by 1 instead of fully resetting
            # This prevents oscillation between backoff and normal
            level = self._backoff_level.get(domain, 0)
            if level > 0:
                self._backoff_level[domain] = level - 1
            self._current_backoff[domain] = 0.0

    def get_status(self, domain: str) -> Dict:
        """Get current rate limiter status for a domain."""
        with self._lock:
            return {
                "domain": domain,
                "backoff_level": self._backoff_level.get(domain, 0),
                "current_backoff": self._current_backoff.get(domain, 0.0),
                "last_request": self._last_request.get(domain, 0.0),
            }


class KalshiRateLimiter(RateLimiter):
    """
    Kalshi-specific rate limiter with appropriate defaults.

    Kalshi API limits (approximate):
    - Public endpoints: ~10 requests/second
    - Authenticated endpoints: ~5 requests/second
    - Market data: ~20 requests/second
    - 429 responses should trigger immediate backoff

    We use conservative defaults to stay well under limits.
    """

    def __init__(self):
        super().__init__(
            min_interval=0.35,      # ~2.9 req/s max sustained rate
            max_backoff=60.0,       # Max 1 minute backoff
            initial_backoff=2.0,    # Start with 2s backoff on 429
            backoff_factor=2.0,     # Double each time: 2, 4, 8, 16, 32, 60
            jitter_range=0.15,      # Small jitter to avoid synchronization
        )


class WeatherAPIRateLimiter(RateLimiter):
    """
    Rate limiter for weather API calls (NWS, Open-Meteo).

    NWS API: max 1000 requests/hour (~0.28 req/s)
    Open-Meteo: generous limits but still rate limited
    """

    def __init__(self):
        super().__init__(
            min_interval=1.0,       # ~1 req/s for weather APIs
            max_backoff=30.0,
            initial_backoff=3.0,
            backoff_factor=2.0,
            jitter_range=0.3,
        )


# Global singleton instances
_kalshi_limiter: Optional[KalshiRateLimiter] = None
_weather_limiter: Optional[WeatherAPIRateLimiter] = None
_lock = threading.Lock()


def get_kalshi_limiter() -> KalshiRateLimiter:
    """Get the global Kalshi rate limiter singleton."""
    global _kalshi_limiter
    with _lock:
        if _kalshi_limiter is None:
            _kalshi_limiter = KalshiRateLimiter()
        return _kalshi_limiter


def get_weather_limiter() -> WeatherAPIRateLimiter:
    """Get the global weather API rate limiter singleton."""
    global _weather_limiter
    with _lock:
        if _weather_limiter is None:
            _weather_limiter = WeatherAPIRateLimiter()
        return _weather_limiter
