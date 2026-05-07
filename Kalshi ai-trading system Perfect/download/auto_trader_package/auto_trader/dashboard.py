"""
Dashboard Module — Rich terminal UI with integrated AI Chat panel.

Displays real-time trading stats, positions, signal feed, trade history,
and an interactive chat panel that uses the circular buffer memory.
"""

import os
import sys
import time
import threading
from datetime import datetime
from typing import Dict, List, Optional, Any

try:
    from rich.console import Console
    from rich.live import Live
    from rich.table import Table
    from rich.panel import Panel
    from rich.layout import Layout
    from rich.text import Text
    from rich.columns import Columns
    from rich.align import Align
    from rich.prompt import Prompt
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from .circular_buffer import CircularBuffer
from .ai_chat import AIChat


class Dashboard:
    """Real-time terminal dashboard with integrated AI chat.

    Layout:
    ┌──────────────────────────────────────────────────┐
    │  HEADER: Status bar (strategies, mode, uptime)     │
    ├────────────────┬─────────────────────────────────│
    │  STATS PANEL   │  POSITIONS / SIGNALS            │
    │  (PnL, Win%)   │  (active trades, recent signals)│
    ├────────────────┴─────────────────────────────────│
    │  TRADE HISTORY (scrollable)                        │
    ├──────────────────────────────────────────────────┤
    │  AI CHAT PANEL (interactive)                       │
    └──────────────────────────────────────────────────┘
    """

    def __init__(
        self,
        buffer: CircularBuffer,
        chat: AIChat,
        config: Optional[Dict] = None,
        refresh_rate: float = 2.0,
    ):
        if not RICH_AVAILABLE:
            raise ImportError(
                "Rich library required for dashboard. "
                "Install with: pip install rich"
            )

        self.buffer = buffer
        self.chat = chat
        self.config = config or {}
        self.refresh_rate = refresh_rate

        # State tracking
        self._running = False
        self._start_time = datetime.utcnow()
        self._active_positions: List[Dict] = []
        self._current_signals: List[Dict] = []
        self._strategy_status: Dict[str, str] = {}
        self._mode = "PAPER"  # PAPER or LIVE

        # Chat state
        self._chat_messages: List[Dict[str, str]] = []
        self._chat_input = ""
        self._chat_scroll_pos = 0

        self.console = Console()

    # ── State Updates (called by bot.py) ────────────────────────

    def update_positions(self, positions: List[Dict]) -> None:
        """Update the positions display."""
        self._active_positions = positions

    def update_signals(self, signals: List[Dict]) -> None:
        """Update the signals feed."""
        self._current_signals = signals[-10:]  # Keep last 10

    def update_strategy_status(self, status: Dict[str, str]) -> None:
        """Update strategy status indicators."""
        self._strategy_status = status

    def set_mode(self, mode: str) -> None:
        """Set trading mode (PAPER or LIVE)."""
        self._mode = mode.upper()

    # ── Dashboard Rendering ──────────────────────────────────────

    def _build_header(self) -> Panel:
        """Build the header panel."""
        uptime = datetime.utcnow() - self._start_time
        hours, remainder = divmod(int(uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)

        mode_color = "green" if self._mode == "PAPER" else "red"
        mode_text = f"[{mode_color}]{self._mode}[/{mode_color}]"

        strategy_count = len(self._strategy_status) or len(
            self.config.get("strategies", {})
        )

        header_text = Text()
        header_text.append("🤖 Kalshi Multi-Strategy AI Trader", style="bold cyan")
        header_text.append(f"  │  {mode_text}  │  ")
        header_text.append(f"Strategies: {strategy_count}", style="white")
        header_text.append(f"  │  ")
        header_text.append(f"Uptime: {hours:02d}:{minutes:02d}:{seconds:02d}", style="white")
        header_text.append(f"  │  ")
        header_text.append(f"Buffer: {len(self.buffer)} entries", style="dim")

        return Panel(header_text, style="bold white on #1a1a2e", padding=(0, 1))

    def _build_stats_panel(self) -> Panel:
        """Build the performance stats panel."""
        stats = self.buffer.trade_stats()
        breakdown = self.buffer.category_breakdown()

        pnl_color = "green" if stats["total_pnl"] >= 0 else "red"
        wr_color = "green" if stats["win_rate"] >= 0.5 else "yellow"

        table = Table(show_header=True, header_style="bold cyan", box=None)
        table.add_column("Metric", style="white")
        table.add_column("Value", justify="right")

        table.add_row("Total PnL", f"[{pnl_color}]${stats['total_pnl']:+.2f}[/{pnl_color}]")
        table.add_row("Win Rate", f"[{wr_color}]{stats['win_rate']:.1%}[/{wr_color}]")
        table.add_row("Wins", f"[green]{stats['wins']}[/green]")
        table.add_row("Losses", f"[red]{stats['losses']}[/red]")
        table.add_row("Avg PnL", f"${stats['avg_pnl']:.2f}")

        if breakdown:
            table.add_row("─── By Category ───", "")
            for cat, cat_stats in breakdown.items():
                cat_color = "green" if cat_stats["total_pnl"] >= 0 else "red"
                table.add_row(
                    f"  {cat}",
                    f"[{cat_color}]${cat_stats['total_pnl']:+.2f}[/{cat_color}] "
                    f"({cat_stats['win_rate']:.0%})"
                )

        return Panel(table, title="📊 Performance", border_style="cyan", padding=(0, 1))

    def _build_positions_panel(self) -> Panel:
        """Build the active positions panel."""
        if not self._active_positions:
            return Panel(
                "[dim]No active positions[/dim]",
                title="📈 Positions",
                border_style="blue",
                padding=(0, 1),
            )

        table = Table(show_header=True, header_style="bold cyan", box=None)
        table.add_column("Ticker", style="white", width=15)
        table.add_column("Dir", width=4)
        table.add_column("PnL", justify="right", width=8)
        table.add_column("Conf", justify="right", width=6)

        for pos in self._active_positions[:8]:
            pnl = pos.get("pnl", 0)
            pnl_color = "green" if pnl >= 0 else "red"
            table.add_row(
                pos.get("ticker", "?")[:15],
                pos.get("direction", "?"),
                f"[{pnl_color}]${pnl:+.2f}[/{pnl_color}]",
                f"{pos.get('confidence', 0):.0%}",
            )

        return Panel(table, title="📈 Positions", border_style="blue", padding=(0, 1))

    def _build_signals_panel(self) -> Panel:
        """Build the recent signals panel."""
        if not self._current_signals:
            return Panel(
                "[dim]No recent signals[/dim]",
                title="📡 Signals",
                border_style="yellow",
                padding=(0, 1),
            )

        lines = []
        for sig in self._current_signals[-5:]:
            conf = sig.get("confidence", 0)
            conf_emoji = "🟢" if conf >= 0.7 else "🟡" if conf >= 0.5 else "🔴"
            lines.append(
                f"{conf_emoji} {sig.get('ticker', '?')[:12]} "
                f"{sig.get('direction', '?')} "
                f"@ {conf:.0%} — {sig.get('recommendation', '?')[:25]}"
            )

        content = "\n".join(lines)
        return Panel(content, title="📡 Signals", border_style="yellow", padding=(0, 1))

    def _build_history_panel(self) -> Panel:
        """Build the trade history scroll panel."""
        trades = self.buffer.recent_trades(n=8)

        if not trades:
            return Panel(
                "[dim]No trade history yet[/dim]",
                title="📋 Trade History",
                border_style="magenta",
                padding=(0, 1),
            )

        lines = []
        for t in reversed(trades):
            pnl = t.get("pnl", 0)
            outcome = t.get("outcome", "?")
            color = "green" if outcome == "win" else "red"
            ts = t.get("timestamp", "?")[:16]
            lines.append(
                f"[{color}]{outcome.upper():4s}[/{color}] "
                f"{t.get('ticker', '?')[:12]} {t.get('direction', '?'):3s} "
                f"[{color}]${pnl:+6.2f}[/{color}] "
                f"{t.get('category', '?')[:6]} "
                f"[dim]{ts}[/dim]"
            )

        content = "\n".join(lines)
        return Panel(content, title="📋 Trade History", border_style="magenta", padding=(0, 1))

    def _build_chat_panel(self) -> Panel:
        """Build the AI chat panel."""
        # Show last 6 chat messages
        chat_history = self.buffer.recent_chat(n=6)

        lines = []
        for msg in chat_history:
            speaker = msg.get("speaker", "?")
            text = msg.get("message", "")[:80]  # Truncate long messages
            ts = msg.get("timestamp", "?")[:16]

            if speaker == "user":
                lines.append(f"[cyan]You[/cyan] [{ts}]: {text}")
            else:
                lines.append(f"[yellow]🤖 Bot[/yellow] [{ts}]: {text}")

        if not lines:
            lines.append("[dim]Type a message to chat with the AI trader...[/dim]")

        lines.append("")
        lines.append("[bold green]> Type your message and press Enter[/bold green]")

        content = "\n".join(lines)
        return Panel(content, title="💬 AI Chat", border_style="green", padding=(0, 1))

    def _build_strategy_status_panel(self) -> Panel:
        """Build strategy status indicators."""
        if not self._strategy_status:
            strategies = self.config.get("strategies", {})
            self._strategy_status = {k: "active" for k in strategies}

        lines = []
        for name, status in self._strategy_status.items():
            icon = "🟢" if status == "active" else "🔴" if status == "error" else "🟡"
            lines.append(f"{icon} {name}: {status}")

        if not lines:
            lines.append("[dim]No strategies configured[/dim]")

        content = "\n".join(lines)
        return Panel(content, title="⚙️ Strategies", border_style="white", padding=(0, 1))

    def build_layout(self) -> Layout:
        """Build the complete dashboard layout."""
        layout = Layout()

        # Split into rows
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body", ratio=1),
            Layout(name="history", size=10),
            Layout(name="chat", size=10),
        )

        # Split body into columns
        layout["body"].split_row(
            Layout(name="stats", ratio=1),
            Layout(name="main", ratio=2),
        )

        layout["main"].split_column(
            Layout(name="positions", ratio=1),
            Layout(name="signals", ratio=1),
        )

        # Populate
        layout["header"].update(self._build_header())
        layout["stats"].update(self._build_stats_panel())
        layout["positions"].update(self._build_positions_panel())
        layout["signals"].update(self._build_signals_panel())
        layout["history"].update(self._build_history_panel())
        layout["chat"].update(self._build_chat_panel())

        return layout

    # ── Interactive Mode ─────────────────────────────────────────

    def run_interactive(self) -> None:
        """Run the dashboard with interactive chat capability.

        This is the main loop. It:
        1. Renders the dashboard in a Live display
        2. Accepts chat input in a background thread
        3. Processes chat messages through the AI Chat module
        4. Updates the display in real-time
        """
        self._running = True

        # Start chat input thread
        chat_thread = threading.Thread(
            target=self._chat_input_loop, daemon=True
        )
        chat_thread.start()

        # Main display loop
        try:
            with Live(
                self.build_layout(),
                console=self.console,
                refresh_per_second=1 / self.refresh_rate,
                screen=True,
            ) as live:
                while self._running:
                    time.sleep(self.refresh_rate)
                    live.update(self.build_layout())
        except KeyboardInterrupt:
            self._running = False
            self.console.print("\n[bold yellow]Dashboard stopped.[/bold yellow]")

    def _chat_input_loop(self) -> None:
        """Background thread for accepting chat input."""
        # Small delay to let the dashboard render
        time.sleep(1)

        while self._running:
            try:
                # Use console input (falls back to simple input)
                user_input = input("")
                if not user_input.strip():
                    continue

                # Process through AI chat
                response = self.chat.send(user_input.strip())

                # Print response below dashboard
                self.console.print()
                self.console.print(
                    Panel(
                        response,
                        title="🤖 AI Trader",
                        border_style="yellow",
                        padding=(0, 1),
                    )
                )
                self.console.print()

                # Special commands
                cmd = user_input.strip().lower()
                if cmd in ("quit", "exit", "stop"):
                    self._running = False
                elif cmd == "stats":
                    self._print_detailed_stats()
                elif cmd == "history":
                    self._print_detailed_history()

            except (EOFError, KeyboardInterrupt):
                self._running = False
                break
            except Exception as e:
                self.console.print(f"[red]Chat error: {e}[/red]")

    def _print_detailed_stats(self) -> None:
        """Print detailed stats outside the dashboard."""
        stats = self.buffer.trade_stats()
        breakdown = self.buffer.category_breakdown()

        table = Table(title="Detailed Performance Stats", show_lines=True)
        table.add_column("Category", style="cyan")
        table.add_column("Trades", justify="right")
        table.add_column("Win Rate", justify="right")
        table.add_column("Total PnL", justify="right")
        table.add_column("Avg PnL", justify="right")

        # Overall row
        table.add_row(
            "[bold]OVERALL[/bold]",
            str(stats["wins"] + stats["losses"]),
            f"{stats['win_rate']:.1%}",
            f"${stats['total_pnl']:+.2f}",
            f"${stats['avg_pnl']:+.2f}",
        )

        # Per category
        for cat, cat_stats in breakdown.items():
            table.add_row(
                cat,
                str(cat_stats["total"]),
                f"{cat_stats['win_rate']:.1%}",
                f"${cat_stats['total_pnl']:+.2f}",
                f"${cat_stats['total_pnl'] / cat_stats['total']:+.2f}"
                if cat_stats["total"] > 0 else "$0.00",
            )

        self.console.print(table)

    def _print_detailed_history(self) -> None:
        """Print detailed trade history outside the dashboard."""
        trades = self.buffer.recent_trades(n=50)

        if not trades:
            self.console.print("[yellow]No trade history available.[/yellow]")
            return

        table = Table(title="Trade History", show_lines=True)
        table.add_column("Time", style="dim")
        table.add_column("Ticker")
        table.add_column("Dir")
        table.add_column("Outcome")
        table.add_column("PnL", justify="right")
        table.add_column("Conf", justify="right")
        table.add_column("Category")
        table.add_column("Reason")

        for t in trades:
            pnl = t.get("pnl", 0)
            pnl_color = "green" if pnl >= 0 else "red"
            outcome = t.get("outcome", "?")
            outcome_color = "green" if outcome == "win" else "red"

            table.add_row(
                t.get("timestamp", "?")[:16],
                t.get("ticker", "?")[:15],
                t.get("direction", "?"),
                f"[{outcome_color}]{outcome}[/{outcome_color}]",
                f"[{pnl_color}]${pnl:+.2f}[/{pnl_color}]",
                f"{t.get('confidence', 0):.0%}",
                t.get("category", "?")[:8],
                t.get("reason", "")[:30],
            )

        self.console.print(table)

    # ── Non-Interactive Mode ─────────────────────────────────────

    def print_snapshot(self) -> None:
        """Print a one-time snapshot (non-interactive mode)."""
        self.console.print(self._build_header())
        self.console.print()
        self.console.print(self._build_stats_panel())
        self.console.print(self._build_positions_panel())
        self.console.print(self._build_signals_panel())
        self.console.print(self._build_history_panel())

        # Recent chat
        chat_history = self.buffer.recent_chat(n=5)
        if chat_history:
            self.console.print(self._build_chat_panel())

    # ── Persistence ──────────────────────────────────────────────

    def save_buffer(self, filepath: str = "") -> None:
        """Save buffer state to disk."""
        path = filepath or os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "data",
            "buffer_state.json",
        )
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.buffer.save_to_file(path)
        self.console.print(f"[green]Buffer saved to {path}[/green]")

    def load_buffer(self, filepath: str = "") -> None:
        """Load buffer state from disk."""
        path = filepath or os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "data",
            "buffer_state.json",
        )
        self.buffer.load_from_file(path)
        self.console.print(f"[green]Buffer loaded from {path}[/green]")