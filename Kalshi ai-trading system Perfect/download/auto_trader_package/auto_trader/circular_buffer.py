"""
Circular Buffer Memory — Fixed-size rolling memory for trades, signals, and chat.

Overwrites oldest entries when full. Provides recent context to the AI chat system
so it can reference past trades, user feedback, and market observations.
"""

from collections import deque
from datetime import datetime
from typing import Any, Dict, List, Optional
import json
import threading


class CircularBuffer:
    """Thread-safe circular buffer with rich querying."""

    def __init__(self, capacity: int = 500):
        self._buffer: deque = deque(maxlen=capacity)
        self._lock = threading.Lock()
        self._capacity = capacity

    # ── Core Operations ──────────────────────────────────────────

    def append(self, entry: Dict[str, Any]) -> None:
        """Add an entry. Oldest entries are evicted when capacity is reached."""
        if "timestamp" not in entry:
            entry["timestamp"] = datetime.utcnow().isoformat()
        with self._lock:
            self._buffer.append(entry)

    def append_trade(self, ticker: str, direction: str, outcome: str,
                     pnl: float, confidence: float, reason: str = "",
                     category: str = "crypto") -> None:
        """Convenience: log a completed trade."""
        self.append({
            "type": "trade",
            "ticker": ticker,
            "direction": direction,
            "outcome": outcome,
            "pnl": round(pnl, 4),
            "confidence": round(confidence, 3),
            "reason": reason,
            "category": category,
        })

    def append_signal(self, ticker: str, direction: str, strength: float,
                      confidence: float, recommendation: str, reason: str = "",
                      category: str = "crypto") -> None:
        """Convenience: log a signal that was generated."""
        self.append({
            "type": "signal",
            "ticker": ticker,
            "direction": direction,
            "strength": round(strength, 4),
            "confidence": round(confidence, 3),
            "recommendation": recommendation,
            "reason": reason,
            "category": category,
        })

    def append_chat(self, speaker: str, message: str,
                    sentiment: str = "neutral") -> None:
        """Convenience: log a chat message (user or bot)."""
        self.append({
            "type": "chat",
            "speaker": speaker,
            "message": message,
            "sentiment": sentiment,
        })

    def append_observation(self, observation: str, category: str = "general",
                           data: Optional[Dict] = None) -> None:
        """Convenience: log a market observation or AI insight."""
        self.append({
            "type": "observation",
            "observation": observation,
            "category": category,
            "data": data or {},
        })

    # ── Query Operations ─────────────────────────────────────────

    def recent(self, n: int = 20) -> List[Dict[str, Any]]:
        """Return the N most recent entries (newest last)."""
        with self._lock:
            items = list(self._buffer)
            return items[-n:] if n < len(items) else items

    def recent_trades(self, n: int = 20) -> List[Dict[str, Any]]:
        """Return the N most recent trade entries."""
        with self._lock:
            trades = [e for e in self._buffer if e.get("type") == "trade"]
            return trades[-n:]

    def recent_signals(self, n: int = 20) -> List[Dict[str, Any]]:
        """Return the N most recent signal entries."""
        with self._lock:
            signals = [e for e in self._buffer if e.get("type") == "signal"]
            return signals[-n:]

    def recent_chat(self, n: int = 50) -> List[Dict[str, Any]]:
        """Return the N most recent chat entries."""
        with self._lock:
            chats = [e for e in self._buffer if e.get("type") == "chat"]
            return chats[-n:]

    def recent_observations(self, n: int = 20) -> List[Dict[str, Any]]:
        """Return the N most recent observation entries."""
        with self._lock:
            obs = [e for e in self._buffer if e.get("type") == "observation"]
            return obs[-n:]

    def by_category(self, category: str, n: int = 20) -> List[Dict[str, Any]]:
        """Return recent entries filtered by category."""
        with self._lock:
            filtered = [e for e in self._buffer if e.get("category") == category]
            return filtered[-n:]

    # ── Statistics ───────────────────────────────────────────────

    def trade_stats(self) -> Dict[str, Any]:
        """Compute win/loss stats from recent trade history."""
        trades = self.recent_trades(n=self._capacity)
        if not trades:
            return {"wins": 0, "losses": 0, "total_pnl": 0.0,
                    "win_rate": 0.0, "avg_pnl": 0.0}

        wins = [t for t in trades if t.get("outcome") == "win"]
        losses = [t for t in trades if t.get("outcome") == "loss"]
        total_pnl = sum(t.get("pnl", 0) for t in trades)

        return {
            "wins": len(wins),
            "losses": len(losses),
            "total_pnl": round(total_pnl, 4),
            "win_rate": round(len(wins) / len(trades), 3) if trades else 0.0,
            "avg_pnl": round(total_pnl / len(trades), 4) if trades else 0.0,
        }

    def category_breakdown(self) -> Dict[str, Dict[str, Any]]:
        """Breakdown of trades by category."""
        trades = self.recent_trades(n=self._capacity)
        categories: Dict[str, list] = {}
        for t in trades:
            cat = t.get("category", "unknown")
            categories.setdefault(cat, []).append(t)

        result = {}
        for cat, cat_trades in categories.items():
            wins = [t for t in cat_trades if t.get("outcome") == "win"]
            result[cat] = {
                "total": len(cat_trades),
                "wins": len(wins),
                "win_rate": round(len(wins) / len(cat_trades), 3) if cat_trades else 0.0,
                "total_pnl": round(sum(t.get("pnl", 0) for t in cat_trades), 4),
            }
        return result

    # ── Context Generation ──────────────────────────────────────

    def build_chat_context(self, last_n: int = 10) -> str:
        """Build a formatted chat context string for the AI prompt."""
        entries = self.recent(last_n)
        if not entries:
            return "No recent activity."

        lines = []
        for e in entries:
            ts = e.get("timestamp", "?")[:19]
            etype = e.get("type", "?")

            if etype == "trade":
                lines.append(
                    f"[{ts}] TRADE: {e.get('ticker')} {e.get('direction')} → "
                    f"{e.get('outcome')} (PnL: ${e.get('pnl', 0):.2f}, "
                    f"conf: {e.get('confidence', 0):.0%}, cat: {e.get('category', '?')})"
                )
            elif etype == "signal":
                lines.append(
                    f"[{ts}] SIGNAL: {e.get('ticker')} {e.get('direction')} "
                    f"(str: {e.get('strength', 0):.4f}, conf: {e.get('confidence', 0):.0%}, "
                    f"rec: {e.get('recommendation', '?')}, cat: {e.get('category', '?')})"
                )
            elif etype == "chat":
                lines.append(
                    f"[{ts}] {e.get('speaker', '?').upper()}: {e.get('message', '')}"
                )
            elif etype == "observation":
                lines.append(
                    f"[{ts}] OBS: {e.get('observation', '')}"
                )
            else:
                lines.append(f"[{ts}] {etype}: {e}")

        return "\n".join(lines)

    def build_trade_summary(self) -> str:
        """Short summary of recent trading performance for AI context."""
        stats = self.trade_stats()
        breakdown = self.category_breakdown()

        lines = [
            f"Recent Performance: {stats['wins']}W / {stats['losses']}L, "
            f"win rate: {stats['win_rate']:.1%}, PnL: ${stats['total_pnl']:.2f}",
        ]

        for cat, cat_stats in breakdown.items():
            lines.append(
                f"  {cat}: {cat_stats['wins']}/{cat_stats['total']} "
                f"({cat_stats['win_rate']:.1%}), PnL: ${cat_stats['total_pnl']:.2f}"
            )

        return "\n".join(lines)

    # ── Persistence ─────────────────────────────────────────────

    def to_json(self) -> str:
        """Serialize buffer to JSON string."""
        with self._lock:
            return json.dumps(list(self._buffer), indent=2, default=str)

    def from_json(self, data: str) -> None:
        """Load buffer from JSON string (clears existing data)."""
        with self._lock:
            self._buffer.clear()
            entries = json.loads(data)
            for entry in entries:
                self._buffer.append(entry)

    def save_to_file(self, filepath: str) -> None:
        """Persist buffer to disk."""
        with open(filepath, "w") as f:
            f.write(self.to_json())

    def load_from_file(self, filepath: str) -> None:
        """Load buffer from disk (if file exists)."""
        import os
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                self.from_json(f.read())

    # ── Utility ──────────────────────────────────────────────────

    def __len__(self) -> int:
        with self._lock:
            return len(self._buffer)

    def __repr__(self) -> str:
        return f"CircularBuffer(capacity={self._capacity}, entries={len(self)})"