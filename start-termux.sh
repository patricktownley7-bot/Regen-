#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail

# Termux startup script for the Regen bot.
# Usage: chmod +x start-termux.sh && ./start-termux.sh

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Keep the Android device awake while the bot is running, when available.
if command -v termux-wake-lock >/dev/null 2>&1; then
    termux-wake-lock
    cleanup() {
        if command -v termux-wake-unlock >/dev/null 2>&1; then
            termux-wake-unlock
        fi
    }
    trap cleanup EXIT INT TERM
fi

# Use the project virtual environment when it exists.
if [[ -f "$SCRIPT_DIR/.venv/bin/activate" ]]; then
    # shellcheck disable=SC1091
    source "$SCRIPT_DIR/.venv/bin/activate"
fi

if ! command -v python >/dev/null 2>&1; then
    echo "Python is not installed. Run: pkg install python -y" >&2
    exit 1
fi

# Select the first conventional Python entry point that exists.
entry_point=""
for candidate in main.py bot.py app.py; do
    if [[ -f "$SCRIPT_DIR/$candidate" ]]; then
        entry_point="$candidate"
        break
    fi
done

if [[ -z "$entry_point" ]]; then
    echo "No bot entry point found. Expected main.py, bot.py, or app.py." >&2
    echo "The current repository does not yet contain runnable bot source code." >&2
    exit 1
fi

# Install declared dependencies on first run, if provided.
if [[ -f "$SCRIPT_DIR/requirements.txt" ]]; then
    python -m pip install -r "$SCRIPT_DIR/requirements.txt"
fi

echo "Starting Regen bot: $entry_point"
exec python "$SCRIPT_DIR/$entry_point" "$@"
