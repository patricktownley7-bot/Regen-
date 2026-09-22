#!/usr/bin/env python3
"""Termux-safe Alpaca paper trading bot for stocks and crypto.

This bot refuses live trading. Set PAPER_TRADING=true (the default).
Example assets: SPY,BTC/USD
"""
import os
import time
from collections import defaultdict, deque
from datetime import datetime, timezone
from urllib.parse import quote

import requests
from dotenv import load_dotenv

load_dotenv()

ASSETS = [item.strip().upper() for item in os.getenv("ASSETS", "SPY,BTC/USD").split(",") if item.strip()]
DEFAULT_QTY = os.getenv("QTY", "1")
POLL_SECONDS = int(os.getenv("POLL_SECONDS", "60"))
SHORT_WINDOW = int(os.getenv("SHORT_WINDOW", "5"))
LONG_WINDOW = int(os.getenv("LONG_WINDOW", "20"))
PAPER_TRADING = os.getenv("PAPER_TRADING", "true").lower() == "true"
API_KEY = os.getenv("APCA_API_KEY_ID", "")
API_SECRET = os.getenv("APCA_API_SECRET_KEY", "")
TRADING_URL = "https://paper-api.alpaca.markets"
STOCK_DATA_URL = "https://data.alpaca.markets/v2"
CRYPTO_DATA_URL = "https://data.alpaca.markets/v1beta3/crypto/us"

if not PAPER_TRADING:
    raise SystemExit("Safety stop: this project only supports PAPER_TRADING=true.")
if not API_KEY or not API_SECRET:
    raise SystemExit("Set APCA_API_KEY_ID and APCA_API_SECRET_KEY in .env first.")
if not ASSETS:
    raise SystemExit("Set at least one asset in ASSETS.")
if SHORT_WINDOW >= LONG_WINDOW:
    raise SystemExit("SHORT_WINDOW must be smaller than LONG_WINDOW.")

HEADERS = {"APCA-API-KEY-ID": API_KEY, "APCA-API-SECRET-KEY": API_SECRET}
prices = defaultdict(lambda: deque(maxlen=LONG_WINDOW))


def log(message):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"[{now}] {message}", flush=True)


def is_crypto(symbol):
    return "/" in symbol


def quantity_for(symbol):
    return os.getenv(f"QTY_{symbol.replace('/', '_')}", DEFAULT_QTY)


def latest_price(symbol):
    if is_crypto(symbol):
        url = f"{CRYPTO_DATA_URL}/{quote(symbol, safe='')}/latest/quotes"
        params = {}
    else:
        url = f"{STOCK_DATA_URL}/stocks/{quote(symbol, safe='')}/quotes/latest"
        params = {"feed": "iex"}
    response = requests.get(url, headers=HEADERS, params=params, timeout=20)
    response.raise_for_status()
    quote_data = response.json()["quote"]
    return (float(quote_data["bp"]) + float(quote_data["ap"])) / 2


def current_position(symbol):
    encoded = quote(symbol, safe="")
    response = requests.get(f"{TRADING_URL}/v2/positions/{encoded}", headers=HEADERS, timeout=20)
    if response.status_code == 404:
        return 0.0
    response.raise_for_status()
    return float(response.json()["qty"])


def submit_order(symbol, side):
    payload = {
        "symbol": symbol,
        "qty": quantity_for(symbol),
        "side": side,
        "type": "market",
        "time_in_force": "gtc" if is_crypto(symbol) else "day",
    }
    response = requests.post(
        f"{TRADING_URL}/v2/orders",
        headers={**HEADERS, "Content-Type": "application/json"},
        json=payload,
        timeout=20,
    )
    response.raise_for_status()
    order = response.json()
    log(f"PAPER {side.upper()} {payload['qty']} {symbol}; order_id={order['id']}")


def evaluate(symbol):
    price = latest_price(symbol)
    history = prices[symbol]
    history.append(price)
    position = current_position(symbol)
    if len(history) < LONG_WINDOW:
        log(f"{symbol} price=${price:.6f}; collecting {len(history)}/{LONG_WINDOW} prices")
        return
    short = sum(list(history)[-SHORT_WINDOW:]) / SHORT_WINDOW
    long = sum(history) / LONG_WINDOW
    log(f"{symbol} price=${price:.6f} short={short:.6f} long={long:.6f} position={position}")
    if short > long and position <= 0:
        submit_order(symbol, "buy")
    elif short < long and position > 0:
        submit_order(symbol, "sell")


def main():
    log(f"Starting PAPER trading only: {', '.join(ASSETS)}, polling every {POLL_SECONDS}s")
    while True:
        try:
            for symbol in ASSETS:
                try:
                    evaluate(symbol)
                except Exception as exc:
                    log(f"{symbol} ERROR: {exc}")
        except KeyboardInterrupt:
            log("Stopped by user")
            return
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()
