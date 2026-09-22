# Regen-

Regeneration coin project with a Termux-ready multi-asset paper-trading demonstration app.

## Install on Termux

```bash
bash install-termux.sh
nano .env
./start-termux.sh
```

The default configuration watches both `SPY` and `BTC/USD` through Alpaca's paper APIs. Configure paper credentials in `.env`:

```env
APCA_API_KEY_ID=your_paper_key
APCA_API_SECRET_KEY=your_paper_secret
PAPER_TRADING=true
ASSETS=SPY,BTC/USD
QTY=1
QTY_BTC_USD=0.0001
```

The bot keeps an in-memory moving-average window, prints quotes and signals, and submits paper orders only. Crypto quantities may be fractional; stock quantities are normally whole shares.

## Safety

- `PAPER_TRADING=true` is required; the app refuses to run otherwise.
- Use paper credentials only.
- Never commit `.env` or expose API keys.
- This is a simple demonstration strategy, not financial advice or a profit guarantee.
- Stop the app with `Ctrl+C`.
