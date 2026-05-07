"""
Scheduler for 15-minute Kalshi trading windows.

Syncs to quarter-hour boundaries and manages the trading cycle:
1. Wait for T-5 minutes (5 min before window closes)
2. Analyze momentum
3. Execute trade if signal is strong enough
4. Track the outcome
5. Repeat for next window
"""

import time
import threading
from datetime import datetime, timezone, timedelta
from typing import Optional, Callable, Dict, Any

from .config import TradingConfig, SYMBOL_MAP


class TradingWindowScheduler:
    """
    Schedules trading actions to align with Kalshi 15-minute windows.

    Kalshi windows close at :00, :15, :30, :45 of each hour.
    Our strategy enters at T-5 minutes (5 min before close).

    Timeline for each 15-min window:
        :00 ──────────── :05 ──────── :10 ──────── :15
        |    WAITING      | ANALYZING  | TRACKING   | RESOLVE
                          ^            ^
                          Entry point  Window closes
    """

    def __init__(self, config: Optional[TradingConfig] = None):
        self.config = config or TradingConfig()
        self.entry_minutes_before_close = self.config.ENTRY_WINDOW_MINUTES  # 5

        # Callbacks
        self._on_entry: Optional[Callable] = None
        self._on_resolve: Optional[Callable] = None

        # State
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._current_window_id: Optional[str] = None
        self._last_trade_window: Optional[str] = None

    # ── Window Timing ──────────────────────────────────────────────

    def get_current_window(self) -> Dict[str, Any]:
        """
        Get information about the current 15-minute trading window.

        Returns dict with:
            - window_id: Unique identifier (e.g., "2026-05-04T14:15")
            - close_time: When the window closes
            - entry_time: When we should enter (T-5 min)
            - seconds_to_entry: Seconds until entry time
            - seconds_to_close: Seconds until window closes
            - phase: "WAITING", "ENTRY", "PAST_CLOSE"
        """
        now = datetime.now(timezone.utc)

        # Find the current 15-min window close time
        # Kalshi windows close at :00, :15, :30, :45
        minute = now.minute
        if minute < 15:
            close_minute = 15
        elif minute < 30:
            close_minute = 30
        elif minute < 45:
            close_minute = 45
        else:
            close_minute = 60  # Next hour

        # Calculate close time
        if close_minute == 60:
            close_time = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        else:
            close_time = now.replace(minute=close_minute, second=0, microsecond=0)

        # Entry time = close time - entry window
        entry_time = close_time - timedelta(minutes=self.entry_minutes_before_close)

        # Window ID
        window_id = close_time.strftime("%Y-%m-%dT%H:%M")

        # Calculate seconds
        seconds_to_entry = (entry_time - now).total_seconds()
        seconds_to_close = (close_time - now).total_seconds()

        # Determine phase
        if seconds_to_entry > 0:
            phase = "WAITING"
        elif seconds_to_close > 0:
            phase = "ENTRY"
        else:
            phase = "PAST_CLOSE"

        return {
            "window_id": window_id,
            "close_time": close_time.isoformat(),
            "entry_time": entry_time.isoformat(),
            "seconds_to_entry": max(0, seconds_to_entry),
            "seconds_to_close": max(0, seconds_to_close),
            "phase": phase,
            "now_utc": now.isoformat(),
        }

    def get_next_entry_time(self) -> datetime:
        """Get the next entry time (when we should analyze and trade)."""
        window = self.get_current_window()
        if window["phase"] == "WAITING":
            return datetime.fromisoformat(window["entry_time"])
        else:
            # Next window's entry time
            next_close = datetime.fromisoformat(window["close_time"]) + timedelta(minutes=15)
            return next_close - timedelta(minutes=self.entry_minutes_before_close)

    def wait_for_entry(self) -> str:
        """
        Block until the next entry time (T-5 minutes before window close).
        Returns the window_id for the upcoming window.
        """
        while self._running:
            window = self.get_current_window()

            if window["phase"] == "ENTRY":
                return window["window_id"]

            if window["phase"] == "WAITING":
                wait_seconds = window["seconds_to_entry"]
                print(f"[Scheduler] Waiting {wait_seconds:.0f}s until entry time "
                      f"({window['entry_time'][:19]})")

                # Sleep in small increments so we can stop
                sleep_chunk = min(wait_seconds, 10)
                while sleep_chunk > 0 and self._running:
                    time.sleep(sleep_chunk)
                    wait_seconds -= sleep_chunk
                    sleep_chunk = min(wait_seconds, 10)

            if window["phase"] == "PAST_CLOSE":
                # Window already closed, wait for next one
                time.sleep(1)

        return ""

    # ── Callback Registration ───────────────────────────────────────

    def on_entry(self, callback: Callable):
        """Register a callback for when entry time arrives."""
        self._on_entry = callback

    def on_resolve(self, callback: Callable):
        """Register a callback for when a window closes."""
        self._on_resolve = callback

    # ── Main Loop ──────────────────────────────────────────────────

    def start(self):
        """Start the scheduler in a background thread."""
        if self._running:
            print("[Scheduler] Already running")
            return

        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        print("[Scheduler] Started — syncing to 15-min Kalshi windows")

    def stop(self):
        """Stop the scheduler."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        print("[Scheduler] Stopped")

    def _run_loop(self):
        """Main scheduler loop."""
        while self._running:
            try:
                # Wait for the next entry time
                window_id = self.wait_for_entry()

                if not self._running or not window_id:
                    break

                # Skip if we already traded this window
                if window_id == self._last_trade_window:
                    time.sleep(30)
                    continue

                print(f"\n{'='*60}")
                print(f"[Scheduler] ENTRY TIME — Window: {window_id}")
                print(f"{'='*60}")

                # Call the entry callback
                if self._on_entry:
                    self._on_entry(window_id)

                self._last_trade_window = window_id

                # Wait for window to close, then resolve
                window = self.get_current_window()
                wait_seconds = window["seconds_to_close"]

                if wait_seconds > 0:
                    print(f"[Scheduler] Waiting {wait_seconds:.0f}s for window to close...")
                    sleep_chunk = min(wait_seconds, 10)
                    while sleep_chunk > 0 and self._running:
                        time.sleep(sleep_chunk)
                        wait_seconds -= sleep_chunk
                        sleep_chunk = min(wait_seconds, 10)

                # Resolve outcomes
                if self._running and self._on_resolve:
                    print(f"[Scheduler] Window closed — resolving outcomes")
                    self._on_resolve(window_id)

            except Exception as e:
                print(f"[Scheduler] Error in loop: {e}")
                time.sleep(10)

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def status(self) -> Dict[str, Any]:
        """Get current scheduler status."""
        window = self.get_current_window()
        return {
            "running": self._running,
            "current_window": window,
            "last_trade_window": self._last_trade_window,
        }
