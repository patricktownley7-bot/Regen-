# Regen-

Regeneration coin project with a Termux-ready SPY paper-trading demonstration app.

## Install on Termux

From the cloned repository, run:

```bash
bash install-termux.sh
```

The installer updates Termux, installs Python, creates `.venv`, installs dependencies, and creates `.env` without overwriting an existing configuration.

Configure your **Alpaca paper account**:

```bash
nano .env
```

Set:

```env
APCA_API_KEY_ID=your_paper_key
APCA_API_SECRET_KEY=your_paper_secret
PAPER_TRADING=true
```

Start the app:

```bash
./start-termux.sh
```

The app polls SPY quotes and displays paper-trading signals/orders in the terminal. It uses a simple moving-average demonstration strategy and is not financial advice.

## Safety

- `PAPER_TRADING=true` is required; the app refuses to run otherwise.
- Use paper credentials only.
- Never commit `.env` or expose API keys.
- Stop the app with `Ctrl+C`.
