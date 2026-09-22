#!/usr/bin/env python3
"""Termux-safe Alpaca paper trading bot for SPY.

This bot refuses live trading. Set PAPER_TRADING=true (the default).
"""
import os
import time
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv

load_dotenv()

SYMBOL = os.getenv("SYMBOL", "SPY").upper()
QTY = int(os.getenv("QTY", "1"))
POLL_SECONDS = int(os.getenv("POLL_SECONDS", "60"))
SHORT_WINDOW = int(os.getenv("SHORT_WINDOW", "5"))
LONG_WINDOW = int(os.getenv("LONG_WINDOW", "20"))
PAPER_TRADING = os.getenv("PAPER_TRADING", "true").lower() == "true"
API_KEY = os.getenv("APCA_API_KEY_ID", "")
API_SECRET = os.getenv("APCA_API_SECRET_KEY", "")
TRADING_URL = "https://paper-api.alpaca.markets"
DATA_URL = "https://data.alpaca.markets"

if not PAPER_TRADING:
    raise SystemExit("Safety stop: this project only supports PAPER_TRADING=true.")
if not API_KEY or not API_SECRET:
    raise SystemExit("Set APCA_API_KEY_ID and APCA_API_SECRET_KEY in .env first.")
if SHORT_WINDOW >= LONG_WINDOW:
    raise SystemExit("SHORT_WINDOW must be smaller than LONG_WINDOW.")

HEADERS = {"APCA-API-KEY-ID": API_KEY, "APCA-API-SECRET-KEY": API_SECRET}


def log(message):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"[{now}] {message}", flush=True)


def latest_price():
    response = requests.get(
        f"{DATA_URL}/v2/stocks/{SYMBOL}/quotes/latest",
        headers=HEADERS,
        params={"feed": "iex"},
        timeout=20,
    )
    response.raise_for_status()
    quote = response.json()["quote"]
    return (float(quote["bp"]) + float(quote["ap"])) / 2


def current_position():
    response = requests.get(f"{TRADING_URL}/v2/positions/{SYMBOL}", headers=HEADERS, timeout=20)
    if response.status_code == 404:
        return 0
    response.raise_for_status()
    return int(float(response.json()["qty"]))


def submit_order(side):
    payload = {"symbol": SYMBOL, "qty": str(QTY), "side": side, "type": "market", "time_in_force": "day"}
    response = requests.post(f"{TRADING_URL}/v2/orders", headers={**HEADERS, "Content-Type": "application/json"}, json=payload, timeout=20)
    response.raise_for_status()
    order = response.json()
    log(f"PAPER {side.upper()} {QTY} {SYMBOL}; order_id={order['id']}")


def main():
    prices = []
    log(f"Starting PAPER trading only: {SYMBOL}, polling every {POLL_SECONDS}s")
    while True:
        try:
            price = latest_price()
            prices.append(price)
            prices[:] = prices[-LONG_WINDOW:]
            position = current_position()
            if len(prices) >= LONG_WINDOW:
                short = sum(prices[-SHORT_WINDOW:]) / SHORT_WINDOW
                long = sum(prices) / LONG_WINDOW
                log(f"{SYMBOL} price=${price:.2f} short={short:.2f} long={long:.2f} position={position}")
                if short > long and position == 0:
                    submit_order("buy")
                elif short < long and position > 0:
                    submit_order("sell")
            else:
                log(f"{SYMBOL} price=${price:.2f}; collecting {len(prices)}/{LONG_WINDOW} prices")
        except KeyboardInterrupt:
            log("Stopped by user")
            return
        except Exception as exc:
            log(f"ERROR: {exc}")
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()
