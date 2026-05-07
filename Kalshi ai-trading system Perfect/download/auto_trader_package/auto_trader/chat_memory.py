"""
Circular Buffer Memory for AI Chat & Trade Context.

Provides a fixed-size, rolling memory of:
- Trade events (entries, exits, resolutions)
- Chat messages (user ↔ bot)
- Strategy signals and reasoning
- Emotional context (user feedback on wins/near-misses)

The circular buffer ensures memory usage stays bounded while
preserving the most recent N interactions.
"""

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
import json


class MemoryType(Enum):
    TRADE = "trade"
    SIGNAL = "signal"
    CHAT_USER = "chat_user"
    CHAT_BOT = "chat_bot"
    SYSTEM = "system"
    EMOTIONAL = "emotional"  # user feedback (praise, frustration, etc.)


class EmotionalTone(Enum):
    POSITIVE = "positive"       # "Nice win!", "Great call!"
    NEUTRAL = "neutral"         # "What's the status?"
    NEGATIVE = "negative"      # "That was a rough loss"
    ENCOURAGING = "encouraging"  # "Almost had it!", "Close one!"
    CURIOUS = "curious"         # "Why did you pick that?"


@dataclass
class MemoryEntry:
    """Single entry in the circular buffer."""
    timestamp: datetime
    memory_type: MemoryType
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    emotional_tone: Optional[EmotionalTone] = None
    trade_id: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "type": self.memory_type.value,
            "content": self.content,
            "metadata": self.metadata,
            "emotional_tone": self.emotional_tone.value if self.emotional_tone else None,
            "trade_id": self.trade_id,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MemoryEntry":
        return cls(
            timestamp=datetime.fromisoformat(data["timestamp"]),
            memory_type=MemoryType(data["type"]),
            content=data["content"],
            metadata=data.get("metadata", {}),
            emotional_tone=EmotionalTone(data["emotional_tone"]) if data.get("emotional_tone") else None,
            trade_id=data.get("trade_id"),
        )


class CircularBufferMemory:
    """
    Fixed-size circular buffer that stores the most recent N entries.

    Older entries are automatically evicted when the buffer is full,
    ensuring memory stays bounded regardless of runtime duration.
    """

    def __init__(self, max_size: int = 500):
        """
        Initialize the circular buffer.

        Args:
            max_size: Maximum number of entries to keep. Default 500
                      gives roughly several hours of active trading context.
        """
        self.max_size = max_size
        self._buffer: deque[MemoryEntry] = deque(maxlen=max_size)
        self._trade_index: Dict[str, MemoryEntry] = {}  # trade_id → latest entry
        self._stats = {
            "total_entries": 0,
            "total_evicted": 0,
            "trades_logged": 0,
            "chats_logged": 0,
        }

    def add(self, entry: MemoryEntry) -> None:
        """Add an entry to the circular buffer."""
        # Track eviction
        if len(self._buffer) == self.max_size:
            self._stats["total_evicted"] += 1

        self._buffer.append(entry)
        self._stats["total_entries"] += 1

        # Index by trade_id for quick lookup
        if entry.trade_id:
            self._trade_index[entry.trade_id] = entry

        # Track type counts
        if entry.memory_type == MemoryType.TRADE:
            self._stats["trades_logged"] += 1
        elif entry.memory_type in (MemoryType.CHAT_USER, MemoryType.CHAT_BOT):
            self._stats["chats_logged"] += 1

        # Prune stale trade index entries
        if len(self._trade_index) > 100:
            active_ids = {e.trade_id for e in self._buffer if e.trade_id}
            self._trade_index = {
                k: v for k, v in self._trade_index.items()
                if k in active_ids
            }

    # ── Convenience Factories ────────────────────────────────────────

    def log_trade(self, trade_id: str, action: str, details: str,
                  metadata: Optional[Dict] = None) -> MemoryEntry:
        """Log a trade event."""
        entry = MemoryEntry(
            timestamp=datetime.now(timezone.utc),
            memory_type=MemoryType.TRADE,
            content=f"[{action}] {details}",
            metadata=metadata or {},
            trade_id=trade_id,
        )
        self.add(entry)
        return entry

    def log_signal(self, signal_content: str,
                   metadata: Optional[Dict] = None) -> MemoryEntry:
        """Log a strategy signal."""
        entry = MemoryEntry(
            timestamp=datetime.now(timezone.utc),
            memory_type=MemoryType.SIGNAL,
            content=signal_content,
            metadata=metadata or {},
        )
        self.add(entry)
        return entry

    def log_chat_user(self, message: str,
                      emotional_tone: Optional[EmotionalTone] = None,
                      metadata: Optional[Dict] = None) -> MemoryEntry:
        """Log a user chat message."""
        entry = MemoryEntry(
            timestamp=datetime.now(timezone.utc),
            memory_type=MemoryType.CHAT_USER,
            content=message,
            metadata=metadata or {},
            emotional_tone=emotional_tone,
        )
        self.add(entry)
        return entry

    def log_chat_bot(self, message: str,
                     metadata: Optional[Dict] = None) -> MemoryEntry:
        """Log a bot chat response."""
        entry = MemoryEntry(
            timestamp=datetime.now(timezone.utc),
            memory_type=MemoryType.CHAT_BOT,
            content=message,
            metadata=metadata or {},
        )
        self.add(entry)
        return entry

    def log_system(self, message: str,
                   metadata: Optional[Dict] = None) -> MemoryEntry:
        """Log a system event."""
        entry = MemoryEntry(
            timestamp=datetime.now(timezone.utc),
            memory_type=MemoryType.SYSTEM,
            content=message,
            metadata=metadata or {},
        )
        self.add(entry)
        return entry

    def log_emotional_feedback(self, message: str,
                                tone: EmotionalTone,
                                trade_id: Optional[str] = None,
                                metadata: Optional[Dict] = None) -> MemoryEntry:
        """Log user emotional feedback (praise, frustration, etc.)."""
        entry = MemoryEntry(
            timestamp=datetime.now(timezone.utc),
            memory_type=MemoryType.EMOTIONAL,
            content=message,
            metadata=metadata or {},
            emotional_tone=tone,
            trade_id=trade_id,
        )
        self.add(entry)
        return entry

    # ── Query Methods ───────────────────────────────────────────────

    def get_recent(self, n: int = 20) -> List[MemoryEntry]:
        """Get the N most recent entries."""
        return list(self._buffer)[-n:]

    def get_recent_chats(self, n: int = 10) -> List[MemoryEntry]:
        """Get the N most recent chat entries (user + bot)."""
        chats = [
            e for e in self._buffer
            if e.memory_type in (MemoryType.CHAT_USER, MemoryType.CHAT_BOT)
        ]
        return chats[-n:]

    def get_recent_trades(self, n: int = 10) -> List[MemoryEntry]:
        """Get the N most recent trade entries."""
        trades = [
            e for e in self._buffer
            if e.memory_type == MemoryType.TRADE
        ]
        return trades[-n:]

    def get_recent_signals(self, n: int = 10) -> List[MemoryEntry]:
        """Get the N most recent signal entries."""
        signals = [
            e for e in self._buffer
            if e.memory_type == MemoryType.SIGNAL
        ]
        return signals[-n:]

    def get_emotional_context(self, n: int = 5) -> List[MemoryEntry]:
        """Get recent emotional feedback entries."""
        emotional = [
            e for e in self._buffer
            if e.memory_type == MemoryType.EMOTIONAL
        ]
        return emotional[-n:]

    def get_trade_context(self, trade_id: str) -> Optional[MemoryEntry]:
        """Look up a trade by ID."""
        return self._trade_index.get(trade_id)

    def search(self, query: str, n: int = 10) -> List[MemoryEntry]:
        """Simple keyword search across all entries."""
        query_lower = query.lower()
        results = [
            e for e in self._buffer
            if query_lower in e.content.lower()
        ]
        return results[-n:]

    def get_by_type(self, memory_type: MemoryType,
                    n: int = 20) -> List[MemoryEntry]:
        """Get entries of a specific type."""
        filtered = [
            e for e in self._buffer
            if e.memory_type == memory_type
        ]
        return filtered[-n:]

    # ── AI Context Generation ────────────────────────────────────────

    def build_ai_context(self, max_entries: int = 30) -> str:
        """
        Build a context string for LLM prompts from recent memory.

        This creates a condensed narrative of recent activity
        that the AI can reference when responding to user queries.
        """
        recent = self.get_recent(max_entries)
        if not recent:
            return "No recent activity."

        lines = []
        for entry in recent:
            ts = entry.timestamp.strftime("%H:%M:%S")

            if entry.memory_type == MemoryType.TRADE:
                lines.append(f"[{ts}] TRADE: {entry.content}")

            elif entry.memory_type == MemoryType.SIGNAL:
                lines.append(f"[{ts}] SIGNAL: {entry.content}")

            elif entry.memory_type == MemoryType.CHAT_USER:
                tone = ""
                if entry.emotional_tone:
                    tone = f" ({entry.emotional_tone.value})"
                lines.append(f"[{ts}] USER{tone}: {entry.content}")

            elif entry.memory_type == MemoryType.CHAT_BOT:
                lines.append(f"[{ts}] BOT: {entry.content}")

            elif entry.memory_type == MemoryType.EMOTIONAL:
                lines.append(
                    f"[{ts}] FEEDBACK ({entry.emotional_tone.value}): "
                    f"{entry.content}"
                )

            elif entry.memory_type == MemoryType.SYSTEM:
                lines.append(f"[{ts}] SYSTEM: {entry.content}")

        return "\n".join(lines)

    def build_trade_summary(self, n: int = 5) -> str:
        """Build a summary of recent trade outcomes for AI context."""
        trades = self.get_recent_trades(n)
        if not trades:
            return "No recent trades."

        lines = []
        for t in trades:
            lines.append(f"- {t.content}")

        return "\n".join(lines)

    # ── Stats & Export ────────────────────────────────────────────────

    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        return {
            **self._stats,
            "buffer_size": len(self._buffer),
            "max_size": self.max_size,
            "trade_index_size": len(self._trade_index),
        }

    def export_recent(self, n: int = 50) -> List[dict]:
        """Export recent entries as dicts for serialization."""
        return [e.to_dict() for e in self.get_recent(n)]

    def save_to_file(self, filepath: str) -> None:
        """Save entire buffer to a JSON file."""
        data = {
            "stats": self._stats,
            "entries": [e.to_dict() for e in self._buffer],
        }
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    def load_from_file(self, filepath: str) -> None:
        """Load buffer from a JSON file."""
        with open(filepath, "r") as f:
            data = json.load(f)

        self._buffer.clear()
        self._trade_index.clear()

        for entry_data in data.get("entries", []):
            entry = MemoryEntry.from_dict(entry_data)
            self._buffer.append(entry)
            if entry.trade_id:
                self._trade_index[entry.trade_id] = entry

        self._stats.update(data.get("stats", {}))