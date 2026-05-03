"""Run locally: python gen_session.py — paste the printed string into SESSION_STRING env var on Render."""
from pyrogram import Client

API_ID = int(input("API_ID: ").strip())
API_HASH = input("API_HASH: ").strip()

with Client("genstr", api_id=API_ID, api_hash=API_HASH, in_memory=True) as app:
    s = app.export_session_string()
    print("\n===== SESSION_STRING =====\n")
    print(s)
    print("\n==========================\n")
