"""
Dynamic Category Manager — Adjusts trading focus based on market conditions.

Dynamically manages which categories (weather, politics, economics, sports, crypto)
to prioritize based on:
1. Opportunity density (how many +EV trades are available)
2. Time-of-day weighting (when each category is most profitable)
3. Recent performance (win rates per category)
4. Auto-disable/enable based on scan results
"""

import time
import threading
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

from .config import StrategyConfig, DynamicCategoryConfig


@dataclass
class CategoryState:
    """Runtime state for a single trading category."""
    name: str
    enabled: bool = True
    priority: int = 0          # Higher = scanned first
    opportunities_found: int = 0
    consecutive_empty_scans: int = 0
    last_scan_time: float = 0.0
    last_opportunity_time: float = 0.0
    total_scans: int = 0
    total_opportunities: int = 0
    wins: int = 0
    losses: int = 0
    disabled_at: float = 0.0

    @property
    def win_rate(self) -> float:
        total = self.wins + self.losses
        return self.wins / total if total > 0 else 0.0

    @property
    def opportunity_rate(self) -> float:
        return self.total_opportunities / self.total_scans if self.total_scans > 0 else 0.0


class DynamicCategoryManager:
    """
    Manages dynamic adjustment of trading categories.

    Features:
    - Auto-disable categories after N empty scans
    - Auto-re-enable after cooldown period
    - Time-of-day weighting for optimal scanning
    - Priority adjustment based on opportunity density
    - Performance-based weighting (higher win rates = higher priority)
    """

    def __init__(
        self,
        strategy_config: Optional[StrategyConfig] = None,
        dynamic_config: Optional[DynamicCategoryConfig] = None,
    ):
        self.strategy_config = strategy_config or StrategyConfig()
        self.dynamic_config = dynamic_config or DynamicCategoryConfig()

        # Initialize category states
        self._categories: Dict[str, CategoryState] = {}
        for i, cat in enumerate(self.strategy_config.CATEGORY_PRIORITY):
            self._categories[cat] = CategoryState(
                name=cat,
                enabled=self._is_category_toggled(cat),
                priority=len(self.strategy_config.CATEGORY_PRIORITY) - i,
            )

        self._lock = threading.Lock()
        self._last_rotation_time: float = 0.0

    def _is_category_toggled(self, category: str) -> bool:
        """Check if a category is enabled via config toggles."""
        toggle_map = {
            "weather": self.strategy_config.ENABLE_WEATHER,
            "politics": self.strategy_config.ENABLE_POLITICS,
            "economics": self.strategy_config.ENABLE_ECONOMICS,
            "sports": self.strategy_config.ENABLE_SPORTS,
            "crypto": self.strategy_config.ENABLE_CRYPTO,
        }
        return toggle_map.get(category, True)

    # ── Category Management ───────────────────────────────────────

    def get_active_categories(self) -> List[str]:
        """Get list of currently active categories, sorted by priority."""
        now = time.time()

        with self._lock:
            active = []
            for cat_name, state in self._categories.items():
                # Check if auto-re-enable applies
                if not state.enabled and state.disabled_at > 0:
                    cooldown = self.dynamic_config.AUTO_REENABLE_AFTER_MINUTES * 60
                    if (now - state.disabled_at) > cooldown:
                        state.enabled = True
                        state.consecutive_empty_scans = 0
                        print(f"[CategoryManager] Auto-re-enabled '{cat_name}' after cooldown")

                if state.enabled:
                    active.append((cat_name, self._calculate_effective_priority(cat_name)))

            # Sort by effective priority (highest first)
            active.sort(key=lambda x: x[1], reverse=True)
            return [cat_name for cat_name, _ in active]

    def _calculate_effective_priority(self, category: str) -> float:
        """
        Calculate effective priority considering:
        1. Base priority from config
        2. Time-of-day bonus
        3. Opportunity density bonus
        4. Win rate bonus
        """
        state = self._categories.get(category)
        if not state:
            return 0.0

        base = state.priority * 10

        # Time-of-day bonus
        time_bonus = self._get_time_bonus(category)

        # Opportunity density bonus
        density_bonus = min(state.opportunity_rate * 20, 15)

        # Win rate bonus (only if we have enough data)
        win_bonus = 0.0
        if (state.wins + state.losses) >= 5:
            win_bonus = state.win_rate * 10

        return base + time_bonus + density_bonus + win_bonus

    def _get_time_bonus(self, category: str) -> float:
        """Get time-of-day bonus for a category."""
        now = datetime.now(timezone.utc)
        current_hour = now.hour

        weights = self.dynamic_config.TIME_WEIGHTS.get(category, {})
        peak_hours = weights.get("peak_hours", [])

        if current_hour in peak_hours:
            return 15.0  # Significant bonus during peak hours
        return 0.0

    # ── Scan Reporting ────────────────────────────────────────────

    def report_scan_result(
        self,
        category: str,
        opportunities_found: int,
        best_edge: float = 0.0,
    ):
        """
        Report the results of a category scan.
        This drives the dynamic adjustment logic.
        """
        with self._lock:
            state = self._categories.get(category)
            if not state:
                return

            now = time.time()
            state.last_scan_time = now
            state.total_scans += 1
            state.opportunities_found = opportunities_found

            if opportunities_found > 0:
                state.total_opportunities += opportunities_found
                state.consecutive_empty_scans = 0
                state.last_opportunity_time = now
            else:
                state.consecutive_empty_scans += 1

                # Auto-disable if too many empty scans
                threshold = self.dynamic_config.AUTO_DISABLE_AFTER_EMPTY_SCANS
                if state.consecutive_empty_scans >= threshold:
                    if state.enabled:
                        state.enabled = False
                        state.disabled_at = now
                        print(f"[CategoryManager] Auto-disabled '{category}' — "
                              f"{state.consecutive_empty_scans} consecutive empty scans")

    def report_trade_result(self, category: str, won: bool):
        """Report the result of a trade for a category."""
        with self._lock:
            state = self._categories.get(category)
            if not state:
                return

            if won:
                state.wins += 1
            else:
                state.losses += 1

    # ── Manual Control ────────────────────────────────────────────

    def enable_category(self, category: str):
        """Manually enable a category."""
        with self._lock:
            state = self._categories.get(category)
            if state:
                state.enabled = True
                state.disabled_at = 0.0
                state.consecutive_empty_scans = 0

    def disable_category(self, category: str):
        """Manually disable a category."""
        with self._lock:
            state = self._categories.get(category)
            if state:
                state.enabled = False
                state.disabled_at = time.time()

    # ── Status ────────────────────────────────────────────────────

    def get_status(self) -> Dict[str, Any]:
        """Get full category management status."""
        with self._lock:
            return {
                "active_categories": self.get_active_categories(),
                "categories": {
                    name: {
                        "enabled": state.enabled,
                        "priority": state.priority,
                        "effective_priority": self._calculate_effective_priority(name),
                        "opportunities_found": state.opportunities_found,
                        "consecutive_empty_scans": state.consecutive_empty_scans,
                        "total_scans": state.total_scans,
                        "win_rate": f"{state.win_rate:.1%}",
                        "opportunity_rate": f"{state.opportunity_rate:.1%}",
                    }
                    for name, state in self._categories.items()
                },
            }
