from pyrogram import Client
from pytgcalls import PyTgCalls
from . import API_ID, API_HASH, BOT_TOKEN, SESSION_STRING

bot = Client("vcbot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN, in_memory=True)
user = Client("vcuser", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING, in_memory=True)
calls = PyTgCalls(user)
