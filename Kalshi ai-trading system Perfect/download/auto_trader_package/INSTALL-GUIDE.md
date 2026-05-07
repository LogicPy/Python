# Kalshi Crypto Scalper — Installation Guide

## Quick Start

### 1. Install Python Dependencies
```bash
cd /path/to/crypto-predictor-full
pip install cryptography requests python-dotenv
```

### 2. Copy Files

Copy these files to your project:

```
auto_trader/          →  crypto-predictor-full/auto_trader/
.env                  →  crypto-predictor-full/.env
kalshi_private_key.pem → crypto-predictor-full/kalshi_private_key.pem
```

For API routes, copy each folder to `src/app/api/`:
```
app_api_routes/auto-trader/   →  src/app/api/auto-trader/route.ts
app_api_routes/trade-log/     →  src/app/api/trade-log/route.ts
app_api_routes/bot-status/    →  src/app/api/bot-status/route.ts
```

### 3. Test in Paper Mode (No Real Money!)

```bash
cd /path/to/crypto-predictor-full

# Test with paper trading (default)
python -m auto_trader.bot

# Test with specific symbols
python -m auto_trader.bot --symbols BTC,ETH,XRP

# Check current status
python -m auto_trader.bot --status
```

### 4. Run the Bot

```bash
# Paper mode (safe, no real money)
python -m auto_trader.bot

# Live mode (REAL MONEY — only after validating paper mode!)
python -m auto_trader.bot --live
```

## File Structure

```
crypto-predictor-full/
├── .env                          # API keys and config
├── kalshi_private_key.pem        # RSA private key for Kalshi auth
├── auto_trader/
│   ├── __init__.py
│   ├── config.py                 # Configuration loader
│   ├── kalshi_client.py          # Kalshi API with RSA-PSS auth
│   ├── momentum_detector.py      # Binance price momentum analysis
│   ├── order_executor.py         # Order placement + risk management
│   ├── scheduler.py              # 15-min window timing
│   ├── ai_analyzer.py            # AI-enhanced analysis (OpenRouter)
│   └── bot.py                    # Main orchestrator
├── data/
│   ├── positions.json            # Saved trading state
│   └── trade_logs/               # Daily trade logs (JSONL)
├── src/app/api/
│   ├── auto-trader/route.ts      # Start/stop bot
│   ├── trade-log/route.ts        # Trade history
│   └── bot-status/route.ts       # Bot status
```

## Configuration (.env)

| Variable | Default | Description |
|---|---|---|
| KALSHI_API_KEY | (required) | Your Kalshi API Key ID |
| KALSHI_PRIVATE_KEY_PATH | ./kalshi_private_key.pem | Path to RSA private key |
| KALSHI_ENV | demo | "demo" for sandbox, "prod" for real |
| PAPER_TRADING | true | true = simulate, false = real money |
| MAX_POSITION_SIZE_DOLLARS | 2.00 | Max $ per trade |
| MAX_DAILY_LOSS_DOLLARS | 10.00 | Stop trading if daily loss exceeds |
| MIN_MOMENTUM_PCT | 0.15 | Min % move to trigger a trade |
| ENTRY_WINDOW_MINUTES | 5 | Enter at T-minus this many minutes |
| ACTIVE_SYMBOLS | BTC,ETH,XRP | Which cryptos to watch |
| OPENROUTER_API_KEY | (optional) | For AI-enhanced analysis |

## Strategy: Late-Game Momentum Scalping

1. Every 15 minutes, Kalshi opens a new BTC/ETH/XRP window
2. At T-5 minutes (5 min before close), we check Binance momentum
3. If price is trending strongly UP → buy YES on UP contract
4. If price is trending strongly DOWN → buy YES on DOWN contract
5. If momentum is unclear → SKIP this window
6. Small wins ($0.50 per trade) compound over many windows

## Safety Features

- **Paper trading**: Default mode, no real money
- **Daily loss limit**: Stops bot automatically
- **Cooldown after loss**: Prevents emotional over-trading
- **Max position size**: Caps risk per trade
- **Min momentum threshold**: Only trades on clear signals
- **AI disagreement check**: If AI disagrees with momentum, confidence drops

## IMPORTANT NOTES

1. Always start in PAPER mode to validate the strategy
2. The .env file contains your API keys — NEVER commit to git
3. Add .env and kalshi_private_key.pem to .gitignore
4. Monitor the bot's first 24 hours closely
5. Only switch to LIVE after consistent paper trading profits
