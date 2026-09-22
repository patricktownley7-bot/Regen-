# Regen-

Regeneration coin project with a Termux-ready **paper-trading** demonstration app for both an S&P 500 ETF and crypto.

## Install on Termux

```bash
bash install-termux.sh
nano .env
./start-termux.sh
```

Configure an Alpaca **paper** account in `.env`:

```env
APCA_API_KEY_ID=your_paper_key
APCA_API_SECRET_KEY=your_paper_secret
PAPER_TRADING=true
SYMBOLS=SPY,BTC/USD
```

`SPY` is the S&P 500 ETF example and `BTC/USD` is the crypto example. You can change `SYMBOLS` to other symbols supported by your paper account. `QTY` controls stock quantity and `CRYPTO_QTY` controls crypto quantity.

The app polls quotes and uses a simple moving-average demonstration strategy. It prints paper signals and orders for every configured symbol. This is not financial advice and does not guarantee returns.

## Safety

- `PAPER_TRADING=true` is required; the app refuses to run otherwise.
- Use paper credentials only.
- Never commit `.env` or expose API keys.
- Stop the app with `Ctrl+C`.
