"""
Configuration loader for the auto-trader.
Reads from .env file and provides typed access to all settings.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the auto_trader package directory
ENV_PATH = Path(__file__).parent.parent / ".env"
load_dotenv(ENV_PATH)


class KalshiConfig:
    """Kalshi API configuration."""
    API_KEY: str = os.getenv("KALSHI_API_KEY", "")
    PRIVATE_KEY_PATH: str = os.getenv("KALSHI_PRIVATE_KEY_PATH", "./kalshi_private_key.pem")
    ENV: str = os.getenv("KALSHI_ENV", "demo")  # "demo" or "prod"

    # API base URLs — verified working endpoints
    # Production: api.elections.kalshi.com (the ONLY working prod URL)
    # Demo: demo-api.kalshi.co (sandbox, no real money)
    # NOTE: api.kalshi.co does NOT resolve (NXDOMAIN) — do not use it!
    DEMO_BASE_URL = "https://demo-api.kalshi.co/trade-api/v2"
    PROD_BASE_URL = "https://api.elections.kalshi.com/trade-api/v2"

    @classmethod
    def get_base_url(cls) -> str:
        """Get the appropriate base URL for the current environment."""
        if cls.ENV == "prod":
            return cls.PROD_BASE_URL
        return cls.DEMO_BASE_URL

    @classmethod
    def get_all_possible_urls(cls) -> list:
        """Return all possible base URLs to try for authentication."""
        urls = []
        if cls.ENV == "prod":
            urls.append(cls.PROD_BASE_URL)   # api.elections.kalshi.com (prod only)
            # Skip demo URL — prod API keys will NEVER work on demo
            # (avoids wasted request + "Auth rejected" log spam)
        else:
            urls.append(cls.DEMO_BASE_URL)   # demo-api.kalshi.co
            urls.append(cls.PROD_BASE_URL)   # Try prod as fallback
        return urls

    @classmethod
    def get_private_key(cls) -> str:
        """
        Load the RSA private key.

        Supports two methods:
        1. From a .pem file (KALSHI_PRIVATE_KEY_PATH)
        2. From a raw PEM string in KALSHI_PRIVATE_KEY env var
        """
        # Method 1: Try loading from environment variable (raw PEM string)
        raw_key = os.getenv("KALSHI_PRIVATE_KEY", "").strip()
        if raw_key:
            # Ensure it has proper PEM formatting
            if "-----BEGIN" not in raw_key:
                # It's a raw base64 key, wrap it in PEM format
                raw_key = f"-----BEGIN RSA PRIVATE KEY-----\n{raw_key}\n-----END RSA PRIVATE KEY-----"
            # Normalize line endings for PEM format
            raw_key = raw_key.replace("\\n", "\n")
            return raw_key

        # Method 2: Load from file path
        key_path = Path(cls.PRIVATE_KEY_PATH)
        if not key_path.is_absolute():
            key_path = Path(__file__).parent.parent / key_path
        if key_path.exists():
            return key_path.read_text()

        raise FileNotFoundError(
            f"Private key not found! Either set KALSHI_PRIVATE_KEY env var "
            f"with the raw PEM content, or place a .pem file at: {key_path}"
        )


class TradingConfig:
    """
    Trading strategy configuration.

    SCALPING MODE (default): Optimized for frequent small wins on
    15-minute Kalshi crypto markets. Trades on ANY detectable momentum,
    even slight edges, because small consistent wins compound.

    Key philosophy: In a 10-min window, BTC typically moves 0.03-0.10%.
    That's STILL enough to predict the 15-min direction with ~55-65%
    accuracy, which is profitable at scale.
    """
    PAPER_TRADING: bool = os.getenv("PAPER_TRADING", "true").lower() == "true"
    MAX_POSITION_SIZE: float = float(os.getenv("MAX_POSITION_SIZE_DOLLARS", "5.00"))
    MAX_DAILY_LOSS: float = float(os.getenv("MAX_DAILY_LOSS_DOLLARS", "50.00"))

    # ── Momentum Thresholds ──────────────────────────────────────
    # Minimum price movement to consider a direction "real"
    # 0.03% = ~$24 move on $80K BTC (easily detectable, very common)
    # Old value 0.15% was WAY too high — almost never triggered
    MIN_MOMENTUM_PCT: float = float(os.getenv("MIN_MOMENTUM_PCT", "0.03"))

    # ── Aggression Level ─────────────────────────────────────────
    # Controls how aggressive the bot is with WEAK signals:
    #   "conservative" — only trade STRONG/MODERATE signals
    #   "aggressive"   — trade WEAK+ signals (recommended for scalping)
    #   "hyper"        — trade ANY directional signal (risky but frequent)
    AGGRESSION: str = os.getenv("AGGRESSION", "aggressive").lower()

    # ── Multi-Symbol Trading ─────────────────────────────────────
    # Trade ALL symbols with directional signals, not just the best one
    TRADE_ALL_SIGNALS: bool = os.getenv("TRADE_ALL_SIGNALS", "true").lower() == "true"

    # ── Entry Window ─────────────────────────────────────────────
    # How many minutes before window close to start analyzing
    # 8 min = wider window = more data = better signals
    ENTRY_WINDOW_MINUTES: int = int(os.getenv("ENTRY_WINDOW_MINUTES", "8"))

    # ── Risk Controls ────────────────────────────────────────────
    COOLDOWN_AFTER_LOSS: bool = os.getenv("COOLDOWN_AFTER_LOSS", "true").lower() == "true"
    COOLDOWN_WINDOWS: int = int(os.getenv("COOLDOWN_WINDOWS", "1"))

    # Active crypto symbols
    ACTIVE_SYMBOLS: list = [s.strip() for s in os.getenv("ACTIVE_SYMBOLS", "BTC,ETH,XRP").split(",")]

    # ── Confidence Thresholds ─────────────────────────────────────
    # Minimum confidence to execute a trade (lower = more trades)
    # 0.20 = very aggressive, 0.35 = moderate, 0.50 = conservative
    MIN_CONFIDENCE: float = float(os.getenv("MIN_CONFIDENCE", "0.20"))

    # ── Trading Mode ──────────────────────────────────────────────
    # "scalper" — Trade on ANY detectable momentum, frequent small wins
    # "quant_probability" — Only trade >60% probability, +EV focus, systematic duplication
    TRADING_MODE: str = os.getenv("TRADING_MODE", "scalper").lower()


class BinanceConfig:
    """
    Binance API configuration.

    IMPORTANT: US users MUST use api.binance.us (not api.binance.com).
    api.binance.com returns HTTP 451 (Unavailable For Legal Reasons) for US IPs.
    The klines/ticker endpoints are public but benefit from API key auth for rate limits.
    """
    BASE_URL: str = os.getenv("BINANCE_BASE_URL", "https://api.binance.us")
    API_KEY: str = os.getenv("BINANCE_API_KEY", "")
    API_SECRET: str = os.getenv("BINANCE_API_SECRET", "")

    @classmethod
    def is_us(cls) -> bool:
        """Check if using Binance US endpoint."""
        return "binance.us" in cls.BASE_URL


class StrategyConfig:
    """
    Multi-strategy configuration for new trading categories.
    Controls EV thresholds, niche targeting, and strategy toggles.
    """
    # ── EV Threshold ──────────────────────────────────────────────
    # Minimum expected value edge to recommend a trade (in cents)
    # 10 = 10¢ edge (e.g., price 40¢ but fair value 50¢+)
    MIN_EV_THRESHOLD_CENTS: float = float(os.getenv("MIN_EV_THRESHOLD_CENTS", "10"))

    # Legacy alias
    @classmethod
    @property
    def MIN_EV_THRESHOLD(cls):
        return cls.MIN_EV_THRESHOLD_CENTS / 100.0

    # ── Position Sizing for EV-based strategies ──────────────────
    BASE_POSITION_SIZE: int = int(os.getenv("BASE_POSITION_SIZE", "5"))
    MAX_POSITION_SIZE: int = int(os.getenv("STRATEGY_MAX_POSITION_SIZE", "25"))

    # ── Strategy Toggles ──────────────────────────────────────────
    ENABLE_WEATHER: bool = os.getenv("ENABLE_WEATHER", "true").lower() == "true"
    ENABLE_POLITICS: bool = os.getenv("ENABLE_POLITICS", "true").lower() == "true"
    ENABLE_ECONOMICS: bool = os.getenv("ENABLE_ECONOMICS", "true").lower() == "true"
    ENABLE_SPORTS: bool = os.getenv("ENABLE_SPORTS", "true").lower() == "true"
    ENABLE_CRYPTO: bool = os.getenv("ENABLE_CRYPTO", "true").lower() == "true"
    ENABLE_MARKET_MAKING: bool = os.getenv("ENABLE_MARKET_MAKING", "false").lower() == "true"

    # ── Category Priority ─────────────────────────────────────────
    # Order of preference when scanning (higher = scanned first)
    CATEGORY_PRIORITY: list = ["weather", "politics", "economics", "sports", "crypto"]

    # ── Niche Targeting ───────────────────────────────────────────
    # Avoid high-liquidity markets (too efficient, no edge)
    MAX_MARKET_LIQUIDITY: int = int(os.getenv("MAX_MARKET_LIQUIDITY", "50000"))

    # ── Market Making ──────────────────────────────────────────────
    MM_SPREAD_MIN: float = float(os.getenv("MM_SPREAD_MIN", "0.03"))  # Min spread to capture
    MM_ORDER_SIZE: int = int(os.getenv("MM_ORDER_SIZE", "5"))          # Contracts per side

    # ── Sports Final Minute ────────────────────────────────────────
    SPORTS_MIN_WIN_PROB: float = float(os.getenv("SPORTS_MIN_WIN_PROB", "0.95"))  # 95%+ to enter
    SPORTS_MINUTES_REMAINING: int = int(os.getenv("SPORTS_MINUTES_REMAINING", "5"))


class WeatherTradingConfig:
    """
    Weather trading system configuration.
    Mirrors the crypto trading system but adapted for weather markets.
    """
    # ── Scan Interval ──────────────────────────────────────────────
    # How often to scan for new weather market opportunities (minutes)
    SCAN_INTERVAL_MINUTES: int = int(os.getenv("WEATHER_SCAN_INTERVAL", "30"))

    # ── Max Positions ─────────────────────────────────────────────
    # Maximum number of concurrent weather positions
    MAX_WEATHER_POSITIONS: int = int(os.getenv("MAX_WEATHER_POSITIONS", "5"))

    # ── Position Size ─────────────────────────────────────────────
    # Max dollar amount per weather trade
    MAX_WEATHER_POSITION_DOLLARS: float = float(os.getenv("MAX_WEATHER_POSITION_DOLLARS", "5.00"))

    # ── EV Threshold ──────────────────────────────────────────────
    # Minimum EV edge to enter a weather trade (cents)
    WEATHER_MIN_EV_CENTS: float = float(os.getenv("WEATHER_MIN_EV_CENTS", "10"))

    # ── Confidence ────────────────────────────────────────────────
    # Minimum confidence to enter a weather trade
    WEATHER_MIN_CONFIDENCE: float = float(os.getenv("WEATHER_MIN_CONFIDENCE", "0.55"))

    # ── Auto-Trade ────────────────────────────────────────────────
    # Whether to auto-execute weather trades (false = scan only)
    WEATHER_AUTO_TRADE: bool = os.getenv("WEATHER_AUTO_TRADE", "false").lower() == "true"

    # ── AI Enhancement ─────────────────────────────────────────────
    # Use AI to enhance weather trade analysis
    WEATHER_AI_ENHANCED: bool = os.getenv("WEATHER_AI_ENHANCED", "true").lower() == "true"

    # ── Known Weather Tickers ──────────────────────────────────────
    # Pre-configured weather ticker patterns for scanning.
    #
    # Based on actual Kalshi market ticker patterns discovered via
    # direct market research. These are used by the PRIMARY ticker-based
    # scan (whitelist approach) instead of the unreliable category scan.
    #
    # Pattern: KX{TYPE}{CITY_CODE}  (e.g., KXHIGHNY, KXHIGHTBOS)
    # Some city codes have a 'T' prefix: KXHIGHTBOS, KXHIGHTDEN, etc.
    # Date suffix (-26MAY06) is handled by Kalshi's API automatically.
    #
    # Kalshi weather ticker format: {PREFIX}-{YY}{MON}{DD}
    # Example: KXHIGHNY-26MAY06 = NYC high temp on May 6, 2026
    WEATHER_TICKER_PATTERNS: list = [
        # ── High Temperature ─────────────────────────────────────────
        # Major cities (no T prefix)
        "KXHIGHNY",    # New York City
        "KXHIGHLAX",   # Los Angeles
        "KXHIGHCHI",   # Chicago
        "KXHIGHHOU",   # Houston
        "KXHIGHMIA",   # Miami
        "KXHIGHATL",   # Atlanta
        "KXHIGHDAL",   # Dallas
        "KXHIGHSEA",   # Seattle
        "KXHIGHAUS",   # Austin
        "KXHIGHPOR",   # Portland
        "KXHIGHSLC",   # Salt Lake City
        "KXHIGHLAS",   # Las Vegas
        # Cities WITH T prefix (Kalshi-specific coding)
        "KXHIGHTBOS",  # Boston
        "KXHIGHTDEN",  # Denver
        "KXHIGHTPHX",  # Phoenix
        "KXHIGHTMIN",  # Minneapolis
        "KXHIGHTLV",   # Las Vegas (alternate ticker)
        "KXHIGHTATL",  # Atlanta (alternate ticker)
        # Additional cities
        "KXHIGHPHL",   # Philadelphia
        "KXHIGHSAN",   # San Antonio
        "KXHIGHSAN",   # San Diego
        "KXHIGHTPA",   # Tampa
        "KXHIGHORL",   # Orlando
        "KXHIGHDET",   # Detroit
        "KXHIGHNAS",   # Nashville
        "KXHIGHSF",    # San Francisco
        "KXHIGHDC",    # Washington DC
        "KXHIGHLAS",   # Las Vegas
        "KXHIGHJAX",   # Jacksonville
        "KXHIGHPIT",   # Pittsburgh
        "KXHIGHCLE",   # Cleveland
        "KXHIGHIND",   # Indianapolis
        "KXHIGHCMH",   # Columbus
        "KXHIGHMEM",   # Memphis
        "KXHIGHMIL",   # Milwaukee
        "KXHIGHTHOU2", # Houston alternate
        # ── Low Temperature ──────────────────────────────────────────
        "KXLLOWNY",    # NYC low temp
        "KXLLOWLAX",   # LA low temp
        "KXLLOWCHI",   # Chicago low temp
        "KXLLOWHOU",   # Houston low temp
        "KXLLOWBOS",   # Boston low temp
        "KXLLOWDEN",   # Denver low temp
        "KXLLOWPHX",   # Phoenix low temp
        "KXLLOWMIN",   # Minneapolis low temp
        # ── Precipitation (Rain) ─────────────────────────────────────
        "KXRAINNY",    # NYC rain
        "KXRAINLAX",   # LA rain
        "KXRAINCHI",   # Chicago rain
        "KXRAINHOU",   # Houston rain
        "KXRAINMIA",   # Miami rain
        "KXRAINATL",   # Atlanta rain
        "KXRAINBOS",   # Boston rain
        "KXRAINDEN",   # Denver rain
        "KXRAINSEA",   # Seattle rain
        "KXRAINDAL",   # Dallas rain
        "XRAINCHI",    # Rain in Chicago (variant)
        # ── Snow ─────────────────────────────────────────────────────
        "KXSNOWDEN",   # Snow in Denver
        "KXSNOWCHI",   # Snow in Chicago
        "KXSNOWNY",    # Snow in NYC
        "KXSNOWBOS",   # Snow in Boston
        "KXSNOWMIN",   # Snow in Minneapolis
        # ── Severe Weather ───────────────────────────────────────────
        "KXHURR",      # Hurricane markets (all variants)
        "KXEQK",       # Earthquake markets
        "KXVOL",       # Volcano markets
        "KXTORN",      # Tornado markets
        "KXWIND",      # Wind markets
        "KXFLOOD",     # Flood markets
        "KXWILD",      # Wildfire markets
        "KXDRGT",      # Drought markets
        # ── Generic / Climate ────────────────────────────────────────
        "KXTEMP",      # Temperature (generic)
        "KXCLIM",      # Climate markets
        # ── Variant tickers (without KX prefix) ──────────────────────
        "XRAIN",       # Rain variant
        "XHIGH",       # High temp variant
        "XLOW",        # Low temp variant
        "XSNOW",       # Snow variant
    ]

    # ── Meteostat Integration ─────────────────────────────────────
    # Use Meteostat for station-based historical weather observations
    METEOSTAT_ENABLED: bool = os.getenv("METEOSTAT_ENABLED", "true").lower() == "true"
    # Number of years to look back for climate normals
    METEOSTAT_LOOKBACK_YEARS: int = int(os.getenv("METEOSTAT_LOOKBACK_YEARS", "10"))
    # Number of recent days to fetch for reality checks
    METEOSTAT_RECENT_DAYS: int = int(os.getenv("METEOSTAT_RECENT_DAYS", "5"))


class QuantitativeProbabilityConfig:
    """
    Quantitative Probability Mode configuration.
    
    TRADING STRATEGY: QUANTITATIVE PROBABILITY MODE
    
    Objective: Discover profitable instances using cold logical percentage 
    calculation and identify the HIGHEST chance of success for duplicating 
    funds at scale.
    
    Key Philosophy: 
    1. Statistical Dominance: Prioritize trades where the calculated 
       probability of success is >60%, moving beyond "any detectable momentum."
    2. Expected Value (EV) Focus: Every trade must represent a positive 
       mathematical edge. Ignore "low-confidence" noise to protect capital 
       for high-conviction windows.
    3. Scalable Replication: Use 15-minute BTC delta and Meteostat weather 
       baselines to find "mispriced" contracts where the market's emotional 
       pricing lags behind the logical reality of the data.
    4. Compound Multiplication: The goal is not just winning, but 
       identifying "Safe-Bet" chains that allow for systematic 
       fund duplication over long-term execution.
    
    Contrast with Scalper Mode:
    - Scalper: trades on ANY momentum edge (min confidence 20%, min EV 10c)
    - Quant Prob: ONLY trades with statistical dominance (min confidence 60%, min EV 15c)
    - Scalper: many small trades, compound through frequency
    - Quant Prob: fewer but high-conviction trades, compound through "Safe-Bet" chains
    """
    # ── Minimum Win Probability ──────────────────────────────────
    # Only enter trades where our calculated probability exceeds this threshold
    # 0.60 = 60% — significantly higher than scalper mode's implicit ~50%
    MIN_WIN_PROBABILITY: float = float(os.getenv("QUANT_MIN_WIN_PROBABILITY", "0.60"))

    # ── Minimum EV Edge ──────────────────────────────────────────
    # Minimum edge in cents to enter a trade (higher than scalper's 10c)
    # 15c = the market must be mispriced by at least 15 cents
    MIN_EV_EDGE_CENTS: float = float(os.getenv("QUANT_MIN_EV_EDGE_CENTS", "15.0"))

    # ── Minimum Confidence ───────────────────────────────────────
    # How confident we must be in our fair value estimate
    # 0.60 = 60% — much higher than scalper's 20% minimum
    MIN_CONFIDENCE: float = float(os.getenv("QUANT_MIN_CONFIDENCE", "0.60"))

    # ── Compound Threshold ───────────────────────────────────────
    # Edge * confidence must exceed this to be a "Safe-Bet"
    # 0.10 = e.g., 15c edge * 0.70 confidence = 0.105 (passes)
    COMPOUND_THRESHOLD: float = float(os.getenv("QUANT_COMPOUND_THRESHOLD", "0.10"))

    # ── Safe-Bet Chains ──────────────────────────────────────────
    # Maximum number of concurrent "Safe-Bet" chain positions
    MAX_SAFE_BET_CHAINS: int = int(os.getenv("QUANT_MAX_SAFE_BET_CHAINS", "3"))

    # ── Mispricing Detection ─────────────────────────────────────
    # Threshold for detecting "emotionally mispriced" contracts
    # Markets where the price lags behind data reality
    MISPRICING_THRESHOLD: float = float(os.getenv("QUANT_MISPRICING_THRESHOLD", "0.08"))

    # ── Direction Consistency ────────────────────────────────────
    # For crypto signals: minimum direction_consistency to trust the signal
    DIRECTION_CONSISTENCY_MIN: float = float(os.getenv("QUANT_DIRECTION_CONSISTENCY_MIN", "0.70"))

    # ── Position Scaling for High Conviction ─────────────────────
    # Scale UP position size for high-conviction trades
    # Scalper mode trades fixed size; Quant mode bets MORE when confident
    POSITION_SCALE_HIGH_CONV: float = float(os.getenv("QUANT_POSITION_SCALE_HIGH_CONV", "1.5"))
    POSITION_SCALE_VERY_HIGH_CONV: float = float(os.getenv("QUANT_POSITION_SCALE_VERY_HIGH_CONV", "2.0"))
    HIGH_CONV_THRESHOLD: float = float(os.getenv("QUANT_HIGH_CONV_THRESHOLD", "0.75"))
    VERY_HIGH_CONV_THRESHOLD: float = float(os.getenv("QUANT_VERY_HIGH_CONV_THRESHOLD", "0.85"))

    # ── Strategy Toggle ──────────────────────────────────────────
    # Master switch: enable/disable quantitative probability mode
    QUANT_MODE_ENABLED: bool = os.getenv("QUANT_MODE_ENABLED", "true").lower() == "true"


class DynamicCategoryConfig:
    """
    Dynamic category adjustment configuration.
    Controls how the bot dynamically adjusts which categories to focus on
    based on market conditions, time of day, and opportunity density.
    """
    # ── Category Rotation ──────────────────────────────────────────
    # How often to re-evaluate category priorities (minutes)
    ROTATION_INTERVAL_MINUTES: int = int(os.getenv("CATEGORY_ROTATION_INTERVAL", "60"))

    # ── Opportunity Density ────────────────────────────────────────
    # Minimum number of +EV opportunities to consider a category "active"
    MIN_OPPORTUNITIES_PER_CATEGORY: int = int(os.getenv("MIN_OPPORTUNITIES_PER_CATEGORY", "2"))

    # ── Auto-Disable ───────────────────────────────────────────────
    # Auto-disable a category if no opportunities found for N consecutive scans
    AUTO_DISABLE_AFTER_EMPTY_SCANS: int = int(os.getenv("AUTO_DISABLE_AFTER_EMPTY_SCANS", "5"))

    # ── Auto-Re-Enable ─────────────────────────────────────────────
    # Re-enable a disabled category after N minutes
    AUTO_REENABLE_AFTER_MINUTES: int = int(os.getenv("AUTO_REENABLE_AFTER_MINUTES", "120"))

    # ── Time-of-Day Weighting ───────────────────────────────────────
    TIME_WEIGHTS: dict = {
        "weather": {"peak_hours": [6, 7, 8, 9, 10, 17, 18, 19]},  # UTC
        "crypto": {"peak_hours": [13, 14, 15, 16, 20, 21, 22, 23]},  # UTC
        "politics": {"peak_hours": [12, 13, 14, 15, 16, 17]},  # UTC
    }


class OpenRouterConfig:
    """OpenRouter API for AI-enhanced analysis."""
    API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    API_URL: str = os.getenv("OPENROUTER_API_URL", "https://openrouter.ai/api/v1/chat/completions")
    MODEL: str = os.getenv("OPENROUTER_MODEL", "z-ai/glm-5.1")  # Configurable model — GLM 5.1 for quant precision


# Symbol mapping: crypto -> Kalshi series ticker + Binance pair
SYMBOL_MAP = {
    "BTC":  {"kalshi_series": "KXBTC15M",  "binance_pair": "BTCUSDT",  "name": "Bitcoin"},
    "ETH":  {"kalshi_series": "KXETH15M",  "binance_pair": "ETHUSDT",  "name": "Ethereum"},
    "XRP":  {"kalshi_series": "KXXRP15M",  "binance_pair": "XRPUSDT",  "name": "XRP"},
    "SOL":  {"kalshi_series": "KXSOL15M",  "binance_pair": "SOLUSDT",  "name": "Solana"},
    "BNB":  {"kalshi_series": "KXBNB15M",  "binance_pair": "BNBUSDT",  "name": "BNB"},
    "DOGE": {"kalshi_series": "KXDOGE15M", "binance_pair": "DOGEUSDT",  "name": "Dogecoin"},
    "HYPE": {"kalshi_series": "KXHYPE15M",  "binance_pair": "HYPEUSDT",  "name": "Hyperliquid"},
}

# Data directories
DATA_DIR = Path(__file__).parent.parent / "data"
TRADE_LOG_DIR = DATA_DIR / "trade_logs"
POSITION_FILE = DATA_DIR / "positions.json"

# Ensure data directories exist
DATA_DIR.mkdir(exist_ok=True)
TRADE_LOG_DIR.mkdir(exist_ok=True)
