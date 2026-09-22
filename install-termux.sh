#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail

# One-command installer for the Regen paper-trading app on Termux.
# Usage: bash install-termux.sh

APP_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$APP_DIR"

info() { printf '\033[1;36m[Regen]\033[0m %s\n' "$*"; }
fail() { printf '\033[1;31m[Regen] ERROR:\033[0m %s\n' "$*" >&2; exit 1; }

command -v pkg >/dev/null 2>&1 || fail "This installer must run inside Termux."

info "Updating Termux packages"
pkg update -y
pkg install -y python git

command -v python >/dev/null 2>&1 || fail "Python installation failed."

if [[ ! -d .venv ]]; then
    info "Creating Python virtual environment"
    python -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate
info "Installing Python dependencies"
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if [[ ! -f .env ]]; then
    cp .env.example .env
    info "Created .env from .env.example"
    printf '\033[1;33m[Regen] Add your Alpaca PAPER credentials to .env before starting.\033[0m\n'
else
    info "Keeping existing .env"
fi

chmod +x start-termux.sh 2>/dev/null || true

cat <<'EOF'

Installation complete.

Next steps:
  1. Edit credentials: nano .env
  2. Confirm PAPER_TRADING=true
  3. Start the app:   ./start-termux.sh
  4. Stop it:          Ctrl+C

This app is paper-trading only and will not submit live orders.
EOF
