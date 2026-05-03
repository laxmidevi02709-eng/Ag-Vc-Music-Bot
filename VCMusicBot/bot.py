import logging
from pyrogram import Client
from .config import Config
from .player import Player
from . import handlers
from . import queue as Q

log = logging.getLogger(__name__)

async def start_bot():
    Config.validate()

    bot = Client(
        "vcmbot",
        api_id=Config.API_ID,
        api_hash=Config.API_HASH,
        bot_token=Config.BOT_TOKEN,
        in_memory=True,
    )
    user = Client(
        "vcmuser",
        api_id=Config.API_ID,
        api_hash=Config.API_HASH,
        session_string=Config.SESSION_STRING,
        in_memory=True,
    )

    handlers.register(bot)
    await bot.start()
    await user.start()

    player = Player(user)
    handlers.PLAYER = player

    async def on_end(chat_id):
        nxt = Q.pop(chat_id)
        if nxt:
            await player.join_and_play(chat_id, nxt)
        else:
            try: await player.calls.leave_call(chat_id)
            except: pass
            player.current.pop(chat_id, None)

    player.setup_handlers(on_end)
    await player.start()

    me = await bot.get_me()
    log.info("Bot started as @%s", me.username)
    if Config.LOG_GROUP_ID:
        try:
            await bot.send_message(Config.LOG_GROUP_ID, f"✅ {me.first_name} started")
        except Exception:
            pass

    from pyrogram import idle
    await idle()

    await bot.stop(); await user.stop()
