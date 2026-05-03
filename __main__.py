import asyncio
from . import LOGGER
from .clients import bot, user, calls
from . import handlers  # register

async def main():
    await user.start()
    await bot.start()
    await calls.start()
    me = await bot.get_me()
    LOGGER.info(f"Bot started as @{me.username}")
    # idle
    from pyrogram import idle
    await idle()
    await bot.stop(); await user.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
