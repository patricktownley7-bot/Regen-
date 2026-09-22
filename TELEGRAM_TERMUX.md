# Telegram community alerts on Termux

This package adds a read-only Telegram monitor to Regen-. It prints keyword matches from Telegram communities your own account is authorized to access.

It does not post messages, execute trades, open links, or treat community messages as financial advice.

## Setup

```bash
cp communities.example.json communities.json
cp .env.example .env
nano .env
source .venv/bin/activate
pip install -r requirements.txt
python community_monitor.py
```

Add these values to `.env`:

```env
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_SESSION=regen_readonly
COMMUNITIES_FILE=communities.json
```

Create Telegram API credentials at https://my.telegram.org. Keep the API hash and generated session file private. Add only official channels you are authorized to monitor to `communities.json`.

On first run Telethon prompts for your phone number, login code, and—if enabled—your password. Keep the session file private and never commit it.

Keep Termux awake:

```bash
termux-wake-lock
python community_monitor.py
```

Stop with Ctrl+C.
