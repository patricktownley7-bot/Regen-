#!/usr/bin/env python3
"""Read-only Telegram keyword alerts for Termux.

This module never posts, trades, follows links, or executes commands from messages.
It only reads chats the configured Telegram account is authorized to access.
"""
import json
import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from telethon import TelegramClient, events

load_dotenv()

API_ID = os.getenv("TELEGRAM_API_ID")
API_HASH = os.getenv("TELEGRAM_API_HASH")
SESSION = os.getenv("TELEGRAM_SESSION", "regen_readonly")
CONFIG = os.getenv("COMMUNITIES_FILE", "communities.json")


def log(message):
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"[{stamp}] {message}", flush=True)


def main():
    if not API_ID or not API_HASH:
        raise SystemExit("Set TELEGRAM_API_ID and TELEGRAM_API_HASH in .env first.")
    try:
        with open(CONFIG, encoding="utf-8") as stream:
            communities = json.load(stream)
    except FileNotFoundError:
        raise SystemExit(f"Create {CONFIG} from communities.example.json first.")
    if not isinstance(communities, list):
        raise SystemExit("Communities configuration must be a JSON list.")

    chats = [item["telegram"] for item in communities if item.get("telegram")]
    keywords = {word.lower() for item in communities for word in item.get("keywords", []) if isinstance(word, str) and word.strip()}
    if not chats:
        raise SystemExit("Add authorized Telegram channels to communities.json first.")

    client = TelegramClient(SESSION, int(API_ID), API_HASH)

    @client.on(events.NewMessage(chats=chats))
    async def on_message(event):
        text = event.raw_text or ""
        matches = sorted(word for word in keywords if word in text.lower())
        if not matches:
            return
        chat = await event.get_chat()
        name = getattr(chat, "title", None) or getattr(chat, "username", None) or "Telegram"
        log(f"ALERT [{name}] keywords={','.join(matches)}")
        print(text[:2000], flush=True)
        print("---", flush=True)

    log(f"Read-only monitor started for {len(chats)} Telegram communities")
    log("No messages are posted and no trades are executed.")
    with client:
        client.run_until_disconnected()


if __name__ == "__main__":
    main()
