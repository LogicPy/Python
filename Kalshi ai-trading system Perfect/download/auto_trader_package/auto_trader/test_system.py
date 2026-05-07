"""
Quick test script for the auto-trader.
Tests each component individually without placing real orders.
"""

import sys
import json
from datetime import datetime, timezone


def test_config():
    """Test configuration loading."""
    print("=" * 50)
    print("TEST: Configuration")
    print("=" * 50)

    from auto_trader.config import (
        KalshiConfig, TradingConfig, BinanceConfig,
        SYMBOL_MAP, TradingConfig as TC
    )

    print(f"  Kalshi API Key: {KalshiConfig.API_KEY[:8]}...")
    print(f"  Kalshi Env: {KalshiConfig.ENV}")
    print(f"  Paper Trading: {TC.PAPER_TRADING}")
    print(f"  Max Position: ${TC.MAX_POSITION_SIZE:.2f}")
    print(f"  Daily Loss Limit: ${TC.MAX_DAILY_LOSS:.2f}")
    print(f"  Min Momentum: {TC.MIN_MOMENTUM_PCT:.3f}%")
    print(f"  Active Symbols: {TC.ACTIVE_SYMBOLS}")
    print(f"  Supported Symbols: {list(SYMBOL_MAP.keys())}")
    print("  ✅ Config loaded successfully\n")


def test_kalshi_client():
    """Test Kalshi client authentication."""
    print("=" * 50)
    print("TEST: Kalshi Client")
    print("=" * 50)

    from auto_trader.kalshi_client import KalshiClient

    client = KalshiClient()
    print(f"  Base URL: {client.base_url}")

    # Try to login
    success = client.login()
    if success:
        print("  ✅ Authentication successful!\n")
    else:
        print("  ⚠️  Authentication failed (check .env and key file)\n")
        print("  Market data may still work via public endpoints\n")


def test_momentum_detector():
    """Test momentum detection on all active symbols."""
    print("=" * 50)
    print("TEST: Momentum Detector")
    print("=" * 50)

    from auto_trader.momentum_detector import MomentumDetector
    from auto_trader.config import TradingConfig, BinanceConfig

    detector = MomentumDetector(TradingConfig(), BinanceConfig())

    for symbol in TradingConfig.ACTIVE_SYMBOLS:
        print(f"\n  Analyzing {symbol}...")

        # Get current price
        price = detector.fetch_current_price(symbol)
        if price:
            print(f"  Current price: ${price:,.2f}")
        else:
            print(f"  ⚠️  Could not fetch price for {symbol}")
            continue

        # Analyze momentum
        signal = detector.analyze_momentum(symbol)
        print(f"  Direction: {signal.direction}")
        print(f"  Strength: {signal.strength}")
        print(f"  Confidence: {signal.confidence:.0%}")
        print(f"  Price Change: {signal.price_change_pct:+.3f}%")
        print(f"  Consistency: {signal.direction_consistency:.0%}")
        print(f"  Volatility: {signal.volatility:.4f}%")
        print(f"  Recommendation: {signal.recommendation}")
        print(f"  Reason: {signal.reason}")

    print("\n  ✅ Momentum detector working\n")


def test_scheduler():
    """Test the window scheduler."""
    print("=" * 50)
    print("TEST: Scheduler")
    print("=" * 50)

    from auto_trader.scheduler import TradingWindowScheduler

    scheduler = TradingWindowScheduler()
    window = scheduler.get_current_window()

    print(f"  Current Window: {window['window_id']}")
    print(f"  Phase: {window['phase']}")
    print(f"  Entry Time: {window['entry_time'][:19]}")
    print(f"  Close Time: {window['close_time'][:19]}")
    print(f"  Seconds to Entry: {window['seconds_to_entry']:.0f}s")
    print(f"  Seconds to Close: {window['seconds_to_close']:.0f}s")

    next_entry = scheduler.get_next_entry_time()
    print(f"  Next Entry: {next_entry.isoformat()[:19]}")
    print("  ✅ Scheduler working\n")


def test_order_executor():
    """Test the order executor (paper mode only)."""
    print("=" * 50)
    print("TEST: Order Executor")
    print("=" * 50)

    from auto_trader.kalshi_client import KalshiClient
    from auto_trader.order_executor import OrderExecutor
    from auto_trader.config import TradingConfig

    client = KalshiClient()
    executor = OrderExecutor(client, TradingConfig())

    print(f"  Paper Trading: {executor.paper_trading}")
    print(f"  {executor.get_status_summary()}")
    print("  Order executor initialized\n")


def test_post_auth():
    """Test POST request authentication (for live mode debugging)."""
    print("=" * 50)
    print("TEST: POST Authentication")
    print("=" * 50)

    from auto_trader.kalshi_client import KalshiClient

    client = KalshiClient()
    print(f"  Base URL: {client.base_url}")

    # First verify GET auth works
    if not client.login():
        print("  GET auth failed — cannot test POST")
        return

    # Now test POST auth
    success = client.test_post_auth()
    if success:
        print("  POST auth works — live trading should work!")
    else:
        print("  POST auth FAILED — see debug output above")
        print("  This means your API key can READ but cannot PLACE ORDERS")
        print("  Possible fixes:")
        print("    1. Check if your API key has 'trade' permissions")
        print("    2. Regenerate your API key on Kalshi with full permissions")
        print("    3. Contact Kalshi support about API key permissions")


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("  KALSHI CRYPTO SCALPER — System Test")
    print("  " + datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"))
    print("=" * 50 + "\n")

    try:
        test_config()
    except Exception as e:
        print(f"  ❌ Config test failed: {e}\n")

    try:
        test_kalshi_client()
    except Exception as e:
        print(f"  ❌ Kalshi client test failed: {e}\n")

    try:
        test_momentum_detector()
    except Exception as e:
        print(f"  ❌ Momentum detector test failed: {e}\n")

    try:
        test_scheduler()
    except Exception as e:
        print(f"  ❌ Scheduler test failed: {e}\n")

    try:
        test_order_executor()
    except Exception as e:
        print(f"  ❌ Order executor test failed: {e}\n")

    try:
        test_post_auth()
    except Exception as e:
        print(f"  ❌ POST auth test failed: {e}\n")

    print("=" * 50)
    print("  TESTS COMPLETE")
    print("=" * 50)
