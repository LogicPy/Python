#!/usr/bin/env python3
"""Kalshi Multi-Strategy AI Trading Bot — CLI Launcher"""

import os, sys, json, time, threading

# ── Package resolver ────────────────────────────────────────
_PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
_PARENT_DIR  = os.path.dirname(_PACKAGE_DIR)
if _PARENT_DIR not in sys.path:
    sys.path.insert(0, _PARENT_DIR)

from auto_trader.config import (
    KalshiConfig, TradingConfig, BinanceConfig, OpenRouterConfig,
    StrategyConfig, WeatherTradingConfig, DynamicCategoryConfig,
    QuantitativeProbabilityConfig
)
from auto_trader.circular_buffer import CircularBuffer
from auto_trader.ai_chat import AIChat
from auto_trader.market_scanner import MarketScanner
from auto_trader.ev_analyzer import EVAnalyzer
from auto_trader.weather_strategy import WeatherStrategy
from auto_trader.weather_bot import WeatherTradingBot
from auto_trader.politics_econ_strategy import PoliticsEconStrategy
from auto_trader.category_manager import DynamicCategoryManager


# ── Composite config wrapper ───────────────────────────────
class CompositeConfig:
    """Wraps sub-configs so cli.config.STRATEGY / .TRADING etc. work."""
    def __init__(self, kalshi, trading, binance, openrouter, strategy, weather, dynamic, quant):
        self.KALSHI     = kalshi
        self.TRADING    = trading
        self.BINANCE    = binance
        self.OPENROUTER = openrouter
        self.STRATEGY   = strategy
        self.WEATHER    = weather
        self.DYNAMIC    = dynamic
        self.QUANT      = quant

    def __getattr__(self, name):
        for sub in (self.KALSHI, self.TRADING, self.BINANCE,
                    self.OPENROUTER, self.STRATEGY, self.WEATHER, self.DYNAMIC, self.QUANT):
            try:
                return getattr(sub, name)
            except AttributeError:
                pass
        raise AttributeError(f"Config has no attribute '{name}'")


# ── CLI ─────────────────────────────────────────────────────
class TradingCLI:
    def __init__(self):
        self.config       = None
        self.kalshi       = None
        self.kalshi_config = None
        self.scanner      = None
        self.ev           = None
        self.memory       = None
        self.chat         = None
        self.weather_strat  = None
        self.weather_bot    = None
        self.politics_strat = None
        self.category_mgr   = None
        self.paper_mode   = True
        self.running      = False
        self.bot_thread   = None
        self._active_bot  = None  # Reference to running CryptoScalperBot for mode propagation

    # ── Initialisation ───────────────────────────────────────
    def init(self):
        kc = KalshiConfig()
        tc = TradingConfig()
        bc = BinanceConfig()
        oc = OpenRouterConfig()
        sc = StrategyConfig()
        wc = WeatherTradingConfig()
        dc = DynamicCategoryConfig()
        qc = QuantitativeProbabilityConfig()
        self.config = CompositeConfig(kc, tc, bc, oc, sc, wc, dc, qc)
        self.kalshi_config = kc

        self.memory = CircularBuffer(capacity=1000)
        self.chat   = AIChat(buffer=self.memory,
                              openrouter_api_key=oc.API_KEY,
                              model=oc.MODEL)

        # Kalshi client
        try:
            from auto_trader.kalshi_client import KalshiClient
            self.kalshi = KalshiClient(kc)
            bal_resp = self.kalshi.get_balance()
            bal_val = bal_resp.get("balance", 0) if isinstance(bal_resp, dict) else (bal_resp or 0)
            bal_s = f"{float(bal_val):,.2f}"
            print(f"  Kalshi connected  (balance: $" + bal_s + ")")
        except Exception as e:
            print(f"  Kalshi auth failed: {e}")
            self.kalshi = None

        # Market scanner
        try:
            self.scanner = MarketScanner(kc)
            print("  MarketScanner ready (with rate limiting)")
        except Exception as e:
            print(f"  MarketScanner failed: {e}")
            self.scanner = None

        # EV Analyzer
        try:
            self.ev = EVAnalyzer(sc)
            print("  EVAnalyzer ready")
        except Exception as e:
            print(f"  EVAnalyzer failed: {e}")
            self.ev = None

        # Strategies
        try:
            self.weather_strat = WeatherStrategy()
            print("  WeatherStrategy ready")
        except Exception as e:
            print(f"  WeatherStrategy failed: {e}")

        try:
            self.politics_strat = PoliticsEconStrategy(oc.API_KEY)
            print("  PoliticsEconStrategy ready")
        except Exception as e:
            print(f"  PoliticsEconStrategy failed: {e}")

        # Weather Trading Bot
        try:
            current_mode = tc.TRADING_MODE  # Use current CLI config trading mode
            self.weather_bot = WeatherTradingBot(paper_mode=self.paper_mode, trading_mode=current_mode)
            print("  WeatherTradingBot ready")
        except Exception as e:
            print(f"  WeatherTradingBot failed: {e}")

        # Category Manager
        try:
            self.category_mgr = DynamicCategoryManager(sc, dc)
            print("  DynamicCategoryManager ready")
        except Exception as e:
            print(f"  DynamicCategoryManager failed: {e}")

        self.memory.append_observation(
            "Bot initialized — multi-strategy CLI ready",
            category="system"
        )

    # ── Help ─────────────────────────────────────────────────
    def do_help(self):
        print("""
  +==========================================================+
  |           KALSHI AI TRADING BOT  --  COMMANDS             |
  +==========================================================+
  |                                                            |
  |   SCANNING                                                 |
  |   scan              Scan all markets for +EV               |
  |   scan weather      Scan weather markets                   |
  |   scan politics     Scan politics markets                  |
  |   scan economics    Scan economics markets                 |
  |   scan sports       Scan sports markets                    |
  |   scan crypto       Scan crypto markets                    |
  |                                                            |
  |   WEATHER TRADING                                          |
  |   weather scan      Run weather scan + analyze now         |
  |   weather start     Start weather auto-trading bot         |
  |   weather stop      Stop weather auto-trading bot          |
  |   weather status    Weather bot status & positions         |
  |   weather trade     Toggle weather auto-trade on/off       |
  |   weather meteostat Show Meteostat data sources            |
  |                                                            |
  |   CATEGORY MANAGEMENT                                      |
  |   categories        Show category status & priorities      |
  |   cat enable <name> Enable a category                      |
  |   cat disable <name> Disable a category                    |
  |                                                            |
  |   STATUS                                                   |
  |   status            Active positions & win rate            |
  |   positions         List open positions                    |
  |   history           Recent trade history                   |
  |   pnl               Detailed P&L breakdown                |
  |                                                            |
  |   AI CHAT                                                  |
  |   chat <message>   Talk to the AI about trades             |
  |   why <ticker>      Ask why a trade was taken              |
  |   memory             View circular buffer contents         |
  |                                                            |
  |   CONTROL                                                  |
  |   run               Start automated trading loop           |
  |   stop              Stop the trading loop                  |
  |   paper              Switch to paper trading               |
  |   live               Switch to LIVE trading                |
  |   mode <name>     Set trading mode (scalper/quant_probability) |
  |   reset              Reset daily P&L and unlock trading    |
  |   losslimit <val>   Set daily loss limit (e.g. 50)        |
  |   config             Show current configuration            |
  |   exit / quit        Shut down the bot                     |
  |                                                            |
  |   DATA SOURCES                                             |
  |   Meteostat: Station-based historical observations         |
  |   NWS/NOAA: US government weather forecasts                |
  |   Open-Meteo: Global forecast & historical archive         |
  |                                                            |
  +==========================================================+
        """)

    # ── Scan ─────────────────────────────────────────────────
    def do_scan(self, category=None):
        if not self.scanner:
            print("  MarketScanner not available")
            return

        print(f"\n  Scanning {'all markets' if not category else category + ' markets'}...")

        try:
            if category:
                # Use efficient direct scan for specific categories
                markets = self.scanner.get_by_category(category)
            else:
                markets = self.scanner.scan(limit=50)
        except Exception as e:
            print(f"  Scan failed: {e}")
            return

        if not markets:
            print("  No markets found.")
            return

        print(f"  Found {len(markets)} market(s). Analyzing for +EV...\n")
        print(f"  {'Ticker':<30} {'Yes$':>6} {'No$':>6}  {'EV%':>6}  Strategy")
        print(f"  {'-'*30} {'-'*6} {'-'*6}  {'-'*6}  {'-'*20}")

        opportunities = 0
        for m in markets:
            try:
                rec = self._analyze_market(m)
                if rec and rec.suggested_size > 0:
                    ev_pct = rec.expected_value * 100 if hasattr(rec, 'expected_value') else rec.ev_cents
                    marker = "+" if ev_pct >= 10 else "~"
                    print(f"  {marker} {m.ticker:<28} {m.yes_price:>5.2f} {m.no_price:>5.2f}"
                          f"  {ev_pct:>+5.1f}  {rec.strategy or 'heuristic'}")
                    self.memory.append_signal(
                        ticker=m.ticker,
                        direction=rec.direction,
                        strength=rec.ev_cents,
                        confidence=rec.confidence,
                        recommendation=rec.direction,
                        reason=rec.reasoning,
                        category=m.category or "unknown",
                    )
                    opportunities += 1
            except Exception:
                continue

        if opportunities == 0:
            print("  No +EV opportunities found this scan.")
        else:
            print(f"\n  {opportunities} +EV opportunit{'y' if opportunities == 1 else 'ies'} found!")

        # Report to category manager
        if self.category_mgr and category:
            self.category_mgr.report_scan_result(category, opportunities)

    def _analyze_market(self, market):
        """Route market to appropriate strategy, fall back to EVAnalyzer."""
        cat = getattr(market, "category", "") or ""

        # Try strategy-specific analysis
        if "weather" in cat and self.weather_strat:
            try:
                rec = self.weather_strat.analyze_market(market)
                if rec:
                    return rec
            except Exception:
                pass

        if cat in ("politics", "economics") and self.politics_strat:
            try:
                rec = self.politics_strat.analyze_market(market)
                if rec:
                    return rec
            except Exception:
                pass

        # Fallback: EV analyzer if available
        if self.ev:
            try:
                rec = self.ev.analyze_market(market)
                if rec:
                    return rec
            except Exception:
                pass

        return None

    # ── Weather Commands ─────────────────────────────────────
    def do_weather(self, args):
        """Handle weather subcommands."""
        parts = args.split(None, 1) if args else []
        subcmd = parts[0].lower() if parts else ""
        subarg = parts[1] if len(parts) > 1 else ""

        if subcmd == "scan":
            self._weather_scan()
        elif subcmd == "start":
            self._weather_start()
        elif subcmd == "stop":
            self._weather_stop()
        elif subcmd == "status":
            self._weather_status()
        elif subcmd == "trade":
            self._weather_toggle_trade()
        elif subcmd == "meteostat":
            self._weather_meteostat()
        else:
            print("  Usage: weather <scan|start|stop|status|trade|meteostat>")

    def _weather_scan(self):
        """Run a one-shot weather scan and analysis."""
        if not self.weather_bot:
            print("  WeatherTradingBot not available")
            return
        print("\n  Running weather market scan...")
        self.weather_bot.scan_and_trade()
        status = self.weather_bot.get_status()
        print(f"\n  Weather scan complete:")
        print(f"    Markets found: {status.get('category_status', {}).get('weather', {}).get('markets_found', '?')}")
        print(f"    Opportunities: {status.get('category_status', {}).get('weather', {}).get('opportunities', '?')}")
        if status.get('last_scan_results'):
            print(f"\n  Top opportunities:")
            for r in status['last_scan_results'][:5]:
                print(f"    {r['ticker']} | {r['direction'].upper()} | "
                      f"EV={r['ev_cents']:+.1f}c | conf={r['confidence']:.0%}")

    def _weather_start(self):
        """Start the weather auto-trading bot."""
        if not self.weather_bot:
            print("  WeatherTradingBot not available")
            return
        if self.weather_bot._running:
            print("  Weather bot is already running.")
            return
        self.weather_bot.start()
        print("  Weather auto-trading bot started.")

    def _weather_stop(self):
        """Stop the weather auto-trading bot."""
        if not self.weather_bot:
            return
        self.weather_bot.stop()
        print("  Weather auto-trading bot stopped.")

    def _weather_status(self):
        """Show weather bot status."""
        if not self.weather_bot:
            print("  WeatherTradingBot not available")
            return
        status = self.weather_bot.get_status()
        print(f"\n  Weather Trading Bot Status")
        print(f"  -------------------------")
        print(f"  Running:      {status.get('running', False)}")
        print(f"  Mode:         {status.get('mode', 'N/A')}")
        print(f"  Auto-Trade:   {status.get('auto_trade', False)}")
        print(f"  AI Enhanced:  {status.get('ai_enhanced', False)}")
        print(f"  Scans:        {status.get('scan_count', 0)}")
        print(f"  Trades:       {status.get('total_trades', 0)}")
        print(f"  Wins/Losses:  {status.get('wins', 0)}/{status.get('losses', 0)}")
        print(f"  Win Rate:     {status.get('win_rate', '0%')}")
        print(f"  Net P&L:      {status.get('net_pnl', '$0.00')}")
        print(f"  Active Pos:   {status.get('active_positions', 0)}/{status.get('max_positions', 0)}")
        cat_status = status.get('category_status', {}).get('weather', {})
        if cat_status:
            print(f"  Last Scan:    {cat_status.get('last_scan', 'never')[:19]}")
            print(f"  Markets:      {cat_status.get('markets_found', 0)}")
            print(f"  Opportunities:{cat_status.get('opportunities', 0)}")

    def _weather_toggle_trade(self):
        """Toggle weather auto-trade on/off."""
        if not self.weather_bot:
            print("  WeatherTradingBot not available")
            return
        wc = self.weather_bot.weather_config
        wc.WEATHER_AUTO_TRADE = not wc.WEATHER_AUTO_TRADE
        state = "ON" if wc.WEATHER_AUTO_TRADE else "OFF"
        print(f"  Weather auto-trade: {state}")

    def _weather_meteostat(self):
        """Show Meteostat data source information."""
        try:
            import meteostat
            print(f"\n  Meteostat Integration")
            print(f"  ----------------------")
            print(f"  Status:    ACTIVE")
            print(f"  Version:   {meteostat.__version__ if hasattr(meteostat, '__version__') else 'installed'}")
            print(f"  Enabled:   {self.config.WEATHER.METEOSTAT_ENABLED}")
            print(f"  Lookback:  {self.config.WEATHER.METEOSTAT_LOOKBACK_YEARS} years")
            print(f"  Recent:    {self.config.WEATHER.METEOSTAT_RECENT_DAYS} days")
            print()
            print(f"  Data Sources:")
            print(f"    1. Meteostat — Station-based historical observations (PRIMARY)")
            print(f"    2. NWS/NOAA — US government forecasts")
            print(f"    3. Open-Meteo — Global forecasts + archive (FALLBACK)")
            print()
            print(f"  Meteostat provides:")
            print(f"    - Real weather station observations (not model reanalysis)")
            print(f"    - Climate normals with 10-30 year lookback")
            print(f"    - Recent actual conditions for reality checks")
            print(f"    - More precise location data than model-based sources")
        except ImportError:
            print(f"\n  Meteostat NOT installed")
            print(f"  Install with: pip install meteostat")
            print(f"  Then add to requirements.txt")

    # ── Category Commands ────────────────────────────────────
    def do_categories(self):
        """Show category status and priorities."""
        if not self.category_mgr:
            print("  CategoryManager not available")
            return
        status = self.category_mgr.get_status()
        print(f"\n  Category Status & Priorities")
        print(f"  -----------------------------")
        print(f"  Active: {', '.join(status.get('active_categories', []))}")
        print()
        for name, info in status.get('categories', {}).items():
            enabled = "ON" if info['enabled'] else "OFF"
            eff_pri = info.get('effective_priority', 0)
            print(f"  [{enabled}] {name:<12} pri={info['priority']:.0f} eff={eff_pri:.1f} "
                  f"opp={info['opportunities_found']} empty_scans={info['consecutive_empty_scans']} "
                  f"wr={info['win_rate']} rate={info['opportunity_rate']}")

    def do_cat_enable(self, category):
        if not self.category_mgr:
            return
        self.category_mgr.enable_category(category)
        print(f"  Category '{category}' enabled")

    def do_cat_disable(self, category):
        if not self.category_mgr:
            return
        self.category_mgr.disable_category(category)
        print(f"  Category '{category}' disabled")

    # ── Status / History / PnL ────────────────────────────────
    def do_status(self):
        stats = self.memory.trade_stats()
        w    = stats.get("wins", 0)
        l_   = stats.get("losses", 0)
        total = w + l_
        wr   = (w / total * 100) if total else 0
        print(f"\n  Status")
        print(f"  -------------------------")
        print(f"  Wins:    {w}")
        print(f"  Losses:  {l_}")
        print(f"  WinRate: {wr:.1f}%")
        print(f"  Mode:    {'PAPER' if self.paper_mode else 'LIVE'}")
        print(f"  Bot:     {'Running' if self.running else 'Stopped'}")
        print(f"  Weather: {'Running' if (self.weather_bot and self.weather_bot._running) else 'Stopped'}")
        if self.kalshi:
            try:
                bal = self.kalshi.get_balance()
                print(f"  Balance: $" + f"{bal:,.2f}")
            except Exception:
                pass

    def do_positions(self):
        print("\n  Open Positions")
        print(f"  -------------------------")
        positions = self.memory.recent_trades(n=20)
        active = [p for p in positions if p.get("status") == "open"]
        if not active:
            print("  No open positions.")
        for p in active:
            ticker = p.get("ticker", "?")
            side   = p.get("side", "?")
            entry  = p.get("entry_price", 0)
            print(f"  * {ticker} | {side} @ {entry}c")

    def do_history(self):
        print("\n  Trade History")
        print(f"  -------------------------")
        trades = self.memory.recent_trades(n=15)
        if not trades:
            print("  No trades yet.")
        for t in trades:
            ticker  = t.get("ticker", "?")
            side    = t.get("side", "?")
            result  = t.get("result", "pending")
            entry   = t.get("entry_price", 0)
            r_icon  = "W" if result == "win" else "L" if result == "loss" else "~"
            print(f"  {r_icon} {ticker} | {side} @ {entry}c -> {result}")

    def do_pnl(self):
        stats = self.memory.trade_stats()
        pnl = stats.get("total_pnl", 0)
        w   = stats.get("wins", 0)
        l_  = stats.get("losses", 0)
        print(f"\n  P&L Breakdown")
        print(f"  -------------------------")
        print(f"  Total P&L: $" + f"{pnl:+,.2f}")
        print(f"  Wins: {w}  |  Losses: {l_}")
        avg_win  = stats.get("avg_pnl", 0) if stats.get("avg_pnl", 0) > 0 else 0
        avg_loss = stats.get("avg_pnl", 0) if stats.get("avg_pnl", 0) < 0 else 0
        if avg_win or avg_loss:
            aw = f"{avg_win:+.2f}" if avg_win else "0.00"
            al = f"{avg_loss:+.2f}" if avg_loss else "0.00"
            print(f"  Avg Win: ${aw}  |  Avg Loss: ${al}")

    # ── AI Chat / Why ────────────────────────────────────────
    def do_chat(self, message):
        try:
            response = self.chat.send(message)
            print(f"\n  AI: {response}")
        except Exception as e:
            print(f"  Chat error: {e}")

    def do_why(self, ticker):
        prompts = [
            f"Why did you trade {ticker}?",
            "Explain the reasoning, data sources, and EV calculation."
        ]
        try:
            response = self.chat.send(" ".join(prompts))
            print(f"\n  AI: {response}")
        except Exception as e:
            print(f"  {e}")

    def do_memory(self):
        entries = self.memory.recent(n=20)
        if not entries:
            print("\n  Memory is empty.")
            return
        print(f"\n  Circular Buffer  (showing last {len(entries)})")
        print(f"  -------------------------")
        for e in entries:
            cat = e.get("category", "?")
            ts  = e.get("timestamp", "")
            txt = e.get("content", "")[:80]
            print(f"  [{cat}] {ts} - {txt}")

    # ── Config ────────────────────────────────────────────────
    def do_config(self):
        kc = self.config.KALSHI
        tc = self.config.TRADING
        sc = self.config.STRATEGY
        oc = self.config.OPENROUTER
        wc = self.config.WEATHER
        qc = self.config.QUANT
        print(f"\n  Configuration")
        print(f"  -------------------------")
        print(f"  Mode:         {'PAPER' if self.paper_mode else 'LIVE'}")
        print(f"  Kalshi Key:   {kc.API_KEY[:8]}..." if kc.API_KEY else "  Kalshi Key:   NOT SET")
        print(f"  Min EV:       {sc.MIN_EV_THRESHOLD_CENTS}c")
        mp = getattr(tc, 'MAX_POSITION_SIZE', '?')
        print(f"  Max Position:  ${mp}")
        print(f"  AI Model:      {oc.MODEL}")
        print(f"  Weather Auto:  {wc.WEATHER_AUTO_TRADE}")
        print(f"  Weather AI:    {wc.WEATHER_AI_ENHANCED}")
        print(f"  Trading Mode:  {tc.TRADING_MODE}")
        print(f"  Quant Enabled: {qc.QUANT_MODE_ENABLED}")
        print(f"  Weather Scan:  {wc.SCAN_INTERVAL_MINUTES}min")
        print(f"  Weather Max:   {wc.MAX_WEATHER_POSITIONS} pos @ ${wc.MAX_WEATHER_POSITION_DOLLARS}")
        print(f"  Daily Loss:    ${tc.MAX_DAILY_LOSS:.2f}")
        print(f"  Meteostat:     {wc.METEOSTAT_ENABLED} ({wc.METEOSTAT_LOOKBACK_YEARS}yr lookback)")

    # ── Bot Control ──────────────────────────────────────────
    def start_bot(self):
        if self.running:
            print("  Bot is already running.")
            return
        self.running = True
        try:
            from auto_trader.bot import CryptoScalperBot
            current_mode = self.config.TRADING.TRADING_MODE  # Use current CLI config
            bot = CryptoScalperBot(paper_mode=self.paper_mode, trading_mode=current_mode)
            def _loop():
                try:
                    bot.start()
                except Exception as e:
                    self.memory.append_observation(
                        f"Bot crashed: {e}", category="error"
                    )
            self.bot_thread = threading.Thread(target=_loop, daemon=True)
            self.bot_thread.start()
            # Keep reference to bot so mode changes can propagate
            self._active_bot = bot
            print("  Bot started in background thread.")
        except Exception as e:
            print(f"  Failed to start bot: {e}")

    def stop_bot(self):
        self.running = False
        self._active_bot = None
        if self.weather_bot:
            self.weather_bot.stop()
        print("  Bot stopped.")

    # ── REPL ──────────────────────────────────────────────────
    def repl(self):
        print(f"\n  +==========================================================+")
        print(f"  |  Kalshi Multi-Strategy AI Bot v3.0.0                      |")
        print(f"  |  Type 'help' for commands | 'exit' to quit                |")
        print(f"  +==========================================================+")
        if self.kalshi:
            try:
                bal = self.kalshi.get_balance()
                bal_s = f"{bal:,.2f}"
                print(f"  Balance: ${bal_s}", end="")
            except Exception:
                pass
        print(f"  | Mode: {'PAPER' if self.paper_mode else 'LIVE'}\n")

        while True:
            try:
                line = input("kalshi> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n  Goodbye!")
                break
            if not line:
                continue

            parts = line.split(None, 1)
            cmd = parts[0].lower()
            arg = parts[1] if len(parts) > 1 else ""

            if cmd in ("exit", "quit"):
                print("  Goodbye!")
                break
            elif cmd == "help":
                self.do_help()
            elif cmd == "scan":
                self.do_scan(arg if arg else None)
            elif cmd == "weather":
                self.do_weather(arg)
            elif cmd == "categories":
                self.do_categories()
            elif cmd == "cat":
                cat_parts = arg.split(None, 1)
                if len(cat_parts) >= 2:
                    cat_action = cat_parts[0].lower()
                    cat_name = cat_parts[1].lower()
                    if cat_action == "enable":
                        self.do_cat_enable(cat_name)
                    elif cat_action == "disable":
                        self.do_cat_disable(cat_name)
                    else:
                        print("  Usage: cat <enable|disable> <category>")
                else:
                    print("  Usage: cat <enable|disable> <category>")
            elif cmd == "status":
                self.do_status()
            elif cmd == "positions":
                self.do_positions()
            elif cmd == "history":
                self.do_history()
            elif cmd == "pnl":
                self.do_pnl()
            elif cmd == "chat":
                if arg:
                    self.do_chat(arg)
                else:
                    print("  Usage: chat <message>")
            elif cmd == "why":
                if arg:
                    self.do_why(arg)
                else:
                    print("  Usage: why <ticker>")
            elif cmd == "memory":
                self.do_memory()
            elif cmd == "run":
                self.start_bot()
            elif cmd == "stop":
                self.stop_bot()
            elif cmd == "mode":
                if arg in ("scalper", "quant_probability"):
                    self.config.TRADING.TRADING_MODE = arg
                    print(f"  Trading mode set to: {arg.upper()}")
                    if arg == "quant_probability":
                        print(f"  >60% probability | +15c EV | Safe-Bet chains")
                    # Propagate mode change to already-created weather bot
                    if self.weather_bot:
                        self.weather_bot.set_trading_mode(arg)
                    # Propagate mode change to active crypto bot
                    if hasattr(self, '_active_bot') and self._active_bot:
                        self._active_bot.set_trading_mode(arg)
                else:
                    print("  Usage: mode <scalper|quant_probability>")
            elif cmd == "reset":
                # Reset daily P&L to unlock trading after loss limit hit
                if self._active_bot and hasattr(self._active_bot, 'executor'):
                    self._active_bot.executor.reset_daily_stats()
                    print(f"  Daily P&L reset — crypto bot trading unlocked!")
                if self.weather_bot:
                    print(f"  Weather bot: no daily loss limit (uses position count instead)")
                if not self._active_bot:
                    print(f"  No active bot running. Start with 'run' first.")
            elif cmd == "losslimit":
                if not arg:
                    current = self.config.TRADING.MAX_DAILY_LOSS
                    print(f"  Current daily loss limit: ${current:.2f}")
                    print(f"  Usage: losslimit <value>  (e.g. losslimit 50)")
                else:
                    try:
                        new_limit = float(arg)
                        if new_limit <= 0:
                            print(f"  Loss limit must be positive")
                        else:
                            self.config.TRADING.MAX_DAILY_LOSS = new_limit
                            print(f"  Daily loss limit set to: ${new_limit:.2f}")
                            # Propagate to active bot's executor
                            if self._active_bot and hasattr(self._active_bot, 'executor'):
                                self._active_bot.executor.set_daily_loss_limit(new_limit)
                    except ValueError:
                        print(f"  Invalid value. Usage: losslimit <number>  (e.g. losslimit 50)")
            elif cmd == "paper":
                self.paper_mode = True
                print("  Switched to PAPER trading mode")
            elif cmd == "live":
                self.paper_mode = False
                print("  Switched to LIVE trading mode")
            elif cmd == "config":
                self.do_config()
            else:
                print(f"  Unknown command: {cmd}  (type 'help')")


def main():
    cli = TradingCLI()
    cli.init()
    cli.repl()


if __name__ == "__main__":
    main()
