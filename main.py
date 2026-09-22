#!/usr/bin/env python3
"""Termux-safe Alpaca paper trader for stocks and crypto.

This bot refuses live trading. Set PAPER_TRADING=true (the default).
Configure SYMBOLS as a comma-separated list, for example: SPY,BTC/USD.
"""
import os
import time
from collections import defaultdict
from datetime import datetime, timezone
from urllib.parse import quote

import requests
from dotenv import load_dotenv

load_dotenv()

SYMBOLS = [item.strip().upper() for item in os.getenv("SYMBOLS", "SPY,BTC/USD").split(",") if item.strip()]
QTY = float(os.getenv("QTY", "1"))
CRYPTO_QTY = float(os.getenv("CRYPTO_QTY", "0.001"))
POLL_SECONDS = int(os.getenv("POLL_SECONDS", "60"))
SHORT_WINDOW = int(os.getenv("SHORT_WINDOW", "5"))
LONG_WINDOW = int(os.getenv("LONG_WINDOW", "20"))
PAPER_TRADING = os.getenv("PAPER_TRADING", "true").lower() == "true"
API_KEY = os.getenv("APCA_API_KEY_ID", "")
API_SECRET = os.getenv("APCA_API_SECRET_KEY", "")
TRADING_URL = "https://paper-api.alpaca.markets"
STOCK_DATA_URL = "https://data.alpaca.markets"
CRYPTO_DATA_URL = "https://data.alpaca.markets/v1beta3/crypto/us"

if not PAPER_TRADING:
    raise SystemExit("Safety stop: this project only supports PAPER_TRADING=true.")
if not API_KEY or not API_SECRET:
    raise SystemExit("Set APCA_API_KEY_ID and APCA_API_SECRET_KEY in .env first.")
if not SYMBOLS:
    raise SystemExit("Set at least one symbol in SYMBOLS.")
if SHORT_WINDOW >= LONG_WINDOW:
    raise SystemExit("SHORT_WINDOW must be smaller than LONG_WINDOW.")
if QTY <= 0 or CRYPTO_QTY <= 0:
    raise SystemExit("QTY and CRYPTO_QTY must be positive.")

HEADERS = {"APCA-API-KEY-ID": API_KEY, "APCA-API-SECRET-KEY": API_SECRET}
prices = defaultdict(list)


def is_crypto(symbol):
    return "/" in symbol


def log(message):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"[{now}] {message}", flush=True)


def latest_price(symbol):
    if is_crypto(symbol):
        response = requests.get(
            f"{CRYPTO_DATA_URL}/latest/quotes",
            headers=HEADERS,
            params={"symbols": symbol},
            timeout=20,
        )
        response.raise_for_status()
        quote = response.json()["quotes"][symbol]
    else:
        response = requests.get(
            f"{STOCK_DATA_URL}/v2/stocks/{quote(symbol, safe='')}/quotes/latest",
            headers=HEADERS,
            params={"feed": "iex"},
            timeout=20,
        )
        response.raise_for_status()
        quote = response.json()["quote"]
    return (float(quote["bp"]) + float(quote["ap"])) / 2


def current_position(symbol):
    encoded_symbol = quote(symbol, safe="")
    response = requests.get(f"{TRADING_URL}/v2/positions/{encoded_symbol}", headers=HEADERS, timeout=20)
    if response.status_code == 404:
        return 0.0
    response.raise_for_status()
    return float(response.json()["qty"])


def submit_order(symbol, side):
    crypto = is_crypto(symbol)
    payload = {
        "symbol": symbol,
        "qty": str(CRYPTO_QTY if crypto else QTY),
        "side": side,
        "type": "market",
        "time_in_force": "gtc" if crypto else "day",
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


def process_symbol(symbol):
    price = latest_price(symbol)
    prices[symbol].append(price)
    prices[symbol][:] = prices[symbol][-LONG_WINDOW:]
    position = current_position(symbol)
    if len(prices[symbol]) < LONG_WINDOW:
        log(f"{symbol} price=${price:.6f}; collecting {len(prices[symbol])}/{LONG_WINDOW} prices")
        return

    short = sum(prices[symbol][-SHORT_WINDOW:]) / SHORT_WINDOW
    long = sum(prices[symbol]) / LONG_WINDOW
    log(f"{symbol} price=${price:.6f} short={short:.6f} long={long:.6f} position={position:g}")
    if short > long and position == 0:
        submit_order(symbol, "buy")
    elif short < long and position > 0:
        submit_order(symbol, "sell")


def main():
    log(f"Starting PAPER trading only: {', '.join(SYMBOLS)}; polling every {POLL_SECONDS}s")
    while True:
        try:
            for symbol in SYMBOLS:
                try:
                    process_symbol(symbol)
                except Exception as exc:
                    log(f"ERROR {symbol}: {exc}")
        except KeyboardInterrupt:
            log("Stopped by user")
            return
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()
