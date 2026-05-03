import os, asyncio, aiohttp
from io import BytesIO
from PIL import Image, ImageFilter
from pyrogram import filters
from pyrogram.types import (
    InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery,
    InputMediaPhoto
)
from pytgcalls.types import MediaStream, AudioQuality
from pytgcalls.exceptions import NoActiveGroupCall

from .clients import bot, user, calls
from .font import f
from . import youtube as yt
from . import queue as Q

ASSETS = os.path.join(os.path.dirname(__file__), "..", "assets")
START_IMG = os.path.join(ASSETS, "start.jpg")
START_BLUR = os.path.join(ASSETS, "start_blur.jpg")

def _ensure_blur():
    if os.path.exists(START_IMG) and not os.path.exists(START_BLUR):
        img = Image.open(START_IMG).convert("RGB")
        img.filter(ImageFilter.GaussianBlur(18)).save(START_BLUR, "JPEG", quality=85)

def kb_start():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f("Tap To Reveal"), callback_data="reveal")],
        [InlineKeyboardButton(f("Help"), callback_data="help"),
         InlineKeyboardButton(f("Owner"), url="https://t.me/")],
    ])

def kb_player(chat_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⏮ -10s", callback_data=f"seek:-10:{chat_id}"),
         InlineKeyboardButton("⏯", callback_data=f"toggle:{chat_id}"),
         InlineKeyboardButton("⏹", callback_data=f"stop:{chat_id}"),
         InlineKeyboardButton("⏭ +10s", callback_data=f"seek:10:{chat_id}")],
        [InlineKeyboardButton(f("Help"), callback_data="help")]
    ])

HELP_TEXT = (
    f("Premium VC Music Bot") + "\n\n"
    + f("Commands") + ":\n"
    + "• /play <" + f("song name or url") + ">\n"
    + "• /pause  /resume  /skip  /stop\n\n"
    + f("Add me and the assistant to your group, start a voice chat, then use /play")
)

@bot.on_message(filters.command("start"))
async def start_cmd(_, m: Message):
    _ensure_blur()
    if os.path.exists(START_BLUR):
        await m.reply_photo(
            START_BLUR,
            caption=f("Welcome to Premium VC Music") + "\n\n" + f("Tap below to reveal"),
            reply_markup=kb_start()
        )
    else:
        await m.reply_text(
            f("Welcome to Premium VC Music") + "\n\n" + f("Tap below to reveal"),
            reply_markup=kb_start()
        )

@bot.on_callback_query(filters.regex("^reveal$"))
async def reveal(_, c: CallbackQuery):
    _ensure_blur()
    try:
        if os.path.exists(START_IMG):
            await c.message.edit_media(
                InputMediaPhoto(START_IMG, caption=f("Premium Unlocked") + "\n\n" + HELP_TEXT),
                reply_markup=kb_start()
            )
        else:
            await c.message.edit_text(f("Premium Unlocked") + "\n\n" + HELP_TEXT, reply_markup=kb_start())
    except Exception:
        await c.message.reply_text(HELP_TEXT)
    await c.answer(f("Revealed"))

@bot.on_callback_query(filters.regex("^help$"))
async def help_cb(_, c: CallbackQuery):
    await c.answer()
    await c.message.reply_text(HELP_TEXT)

@bot.on_message(filters.command(["help"]))
async def help_cmd(_, m: Message):
    await m.reply_text(HELP_TEXT)

async def _fetch_thumb(url: str):
    if not url: return None
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(url, timeout=10) as r:
                if r.status == 200:
                    data = await r.read()
                    bio = BytesIO(data); bio.name = "thumb.jpg"
                    return bio
    except Exception:
        return None
    return None

@bot.on_message(filters.command("play") & filters.group)
async def play_cmd(_, m: Message):
    if len(m.command) < 2 and not m.reply_to_message:
        return await m.reply_text(f("Usage") + ": /play <" + f("song name") + ">")
    query = m.text.split(None, 1)[1] if len(m.command) >= 2 else m.reply_to_message.text
    status = await m.reply_text(f("Searching") + " ...")

    try:
        results = await yt.search(query)
        if not results:
            return await status.edit(f("No results found"))
        first = results[0]
        video_url = first.get("webpage_url") or first.get("url") or f"https://youtu.be/{first.get('id')}"
        title = first.get("title", "Unknown")
        duration = first.get("duration") or 0
        thumb_url = None
        thumbs = first.get("thumbnails") or []
        if thumbs: thumb_url = thumbs[-1].get("url")
        if not thumb_url and first.get("id"):
            thumb_url = f"https://i.ytimg.com/vi/{first['id']}/hqdefault.jpg"

        await status.edit(f("Downloading") + ": " + f(title))
        path, info = await yt.download_audio(video_url)

        # Try to join VC and stream
        try:
            await calls.play(m.chat.id, MediaStream(path, audio_parameters=AudioQuality.HIGH))
        except NoActiveGroupCall:
            return await status.edit(f("Pls make VC live stream first then use /play again"))
        except Exception as e:
            err = str(e).lower()
            if "no active" in err or "group call" in err or "not started" in err:
                return await status.edit(f("Pls make VC live stream first then use /play again"))
            raise

        Q.add(m.chat.id, {"title": title, "url": video_url, "path": path})

        mins, secs = divmod(int(duration or 0), 60)
        caption = (
            f("Now Playing") + "\n\n"
            + f("Title") + ": " + f(title) + "\n"
            + f("Duration") + ": " + f(f"{mins}:{secs:02d}") + "\n"
            + f("Requested By") + ": " + f(m.from_user.first_name if m.from_user else "User")
        )
        thumb = await _fetch_thumb(thumb_url)
        await status.delete()
        if thumb:
            await m.reply_photo(thumb, caption=caption, reply_markup=kb_player(m.chat.id))
        else:
            await m.reply_text(caption, reply_markup=kb_player(m.chat.id))
    except Exception as e:
        await status.edit(f("Error") + ": " + str(e)[:200])

@bot.on_message(filters.command(["pause"]) & filters.group)
async def pause_cmd(_, m):
    try: await calls.pause_stream(m.chat.id); await m.reply_text(f("Paused"))
    except Exception as e: await m.reply_text(f("Error") + ": " + str(e)[:150])

@bot.on_message(filters.command(["resume"]) & filters.group)
async def resume_cmd(_, m):
    try: await calls.resume_stream(m.chat.id); await m.reply_text(f("Resumed"))
    except Exception as e: await m.reply_text(f("Error") + ": " + str(e)[:150])

@bot.on_message(filters.command(["skip", "next"]) & filters.group)
async def skip_cmd(_, m):
    try:
        await calls.leave_call(m.chat.id)
        Q.clear(m.chat.id)
        await m.reply_text(f("Skipped"))
    except Exception as e:
        await m.reply_text(f("Error") + ": " + str(e)[:150])

@bot.on_message(filters.command(["stop", "end"]) & filters.group)
async def stop_cmd(_, m):
    try:
        await calls.leave_call(m.chat.id)
        Q.clear(m.chat.id)
        await m.reply_text(f("Stopped"))
    except Exception as e:
        await m.reply_text(f("Error") + ": " + str(e)[:150])

@bot.on_callback_query(filters.regex(r"^toggle:(-?\d+)$"))
async def toggle_cb(_, c: CallbackQuery):
    chat_id = int(c.data.split(":")[1])
    try:
        try:
            await calls.pause_stream(chat_id); await c.answer(f("Paused"))
        except Exception:
            await calls.resume_stream(chat_id); await c.answer(f("Resumed"))
    except Exception as e:
        await c.answer(str(e)[:180], show_alert=True)

@bot.on_callback_query(filters.regex(r"^stop:(-?\d+)$"))
async def stop_cb(_, c: CallbackQuery):
    chat_id = int(c.data.split(":")[1])
    try:
        await calls.leave_call(chat_id); Q.clear(chat_id)
        await c.answer(f("Stopped"))
    except Exception as e:
        await c.answer(str(e)[:180], show_alert=True)

@bot.on_callback_query(filters.regex(r"^seek:(-?\d+):(-?\d+)$"))
async def seek_cb(_, c: CallbackQuery):
    # py-tgcalls doesn't expose simple seek without re-stream; acknowledge
    await c.answer(f("Seek not supported on free stream"), show_alert=False)
