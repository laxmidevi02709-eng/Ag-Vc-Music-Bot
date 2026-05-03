import os, logging, asyncio
from pyrogram import Client, filters
from pyrogram.types import (
    Message, CallbackQuery, InputMediaPhoto,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from pyrogram.enums import ChatType

from .config import Config
from .font import f
from . import youtube as yt
from . import queue as Q
from .buttons import player_kb, start_kb, help_kb
from .utils import ensure_start_images

log = logging.getLogger(__name__)

PLAYER = None  # set by bot.py

# ---- helpers ----
async def _now_playing_text(track, chat_title):
    return (
        f"🎶 **{f('Now Streaming')}**\n\n"
        f"🎵 {f('Title')}: `{track['title']}`\n"
        f"⏱ {f('Duration')}: `{yt.fmt_duration(track['duration'])}`\n"
        f"👤 {f('Requested in')}: `{chat_title}`\n"
        f"📡 {f('By')}: `{track.get('uploader','')}`"
    )

# ---- /start ----
def register(app: Client):

    @app.on_message(filters.command("start") & filters.private)
    async def start_cmd(_, m: Message):
        clear_p, blur_p = await ensure_start_images(Config.START_IMG)
        caption = (
            f"👋 **{f('Hey')}** {m.from_user.mention}\n\n"
            f"✨ {f('Welcome to')} **{f(Config.BOT_NAME)}**\n"
            f"🎧 {f('Premium VC Music Bot')}\n\n"
            f"👉 {f('Tap Reveal to continue')}"
        )
        if blur_p and os.path.exists(blur_p):
            await m.reply_photo(blur_p, caption=caption, reply_markup=start_kb(True))
        else:
            await m.reply_text(caption, reply_markup=start_kb(True))

    @app.on_message(filters.command("start") & filters.group)
    async def start_group(_, m: Message):
        await m.reply_text(
            f"✨ **{f(Config.BOT_NAME)}** {f('is alive')}\n"
            f"🎧 {f('Use /play song name to begin')}"
        )

    @app.on_callback_query(filters.regex("^reveal$"))
    async def reveal(_, cq: CallbackQuery):
        clear_p, _b = await ensure_start_images(Config.START_IMG)
        caption = (
            f"🎉 **{f('Welcome to')}** **{f(Config.BOT_NAME)}**\n\n"
            f"💎 {f('Premium voice chat music streaming')}\n"
            f"🎵 {f('YouTube search and direct URL support')}\n"
            f"🎛 {f('Full inline player controls')}\n\n"
            f"👉 /help {f('to view all commands')}"
        )
        try:
            await cq.message.edit_media(InputMediaPhoto(clear_p, caption=caption), reply_markup=start_kb(False))
        except Exception:
            await cq.message.edit_caption(caption, reply_markup=start_kb(False))
        await cq.answer(f("Revealed"))

    @app.on_callback_query(filters.regex("^start_back$"))
    async def start_back(_, cq: CallbackQuery):
        await cq.message.edit_caption(
            f"🎉 **{f('Welcome to')}** **{f(Config.BOT_NAME)}**", reply_markup=start_kb(False)
        )

    @app.on_callback_query(filters.regex("^help$"))
    async def help_cb(_, cq: CallbackQuery):
        await cq.message.edit_caption(_help_text(), reply_markup=help_kb())

    @app.on_callback_query(filters.regex("^cmds$"))
    async def cmds_cb(_, cq: CallbackQuery):
        await cq.message.edit_caption(_cmds_text(), reply_markup=help_kb())

    @app.on_message(filters.command("help"))
    async def help_cmd(_, m: Message):
        await m.reply_text(_help_text())

    @app.on_message(filters.command("ping"))
    async def ping(_, m: Message):
        await m.reply_text(f"🏓 {f('Pong!')} `{f(Config.BOT_NAME)}` {f('is online')}")

    # ---- /play ----
    @app.on_message(filters.command(["play", "p"]) & filters.group)
    async def play_cmd(_, m: Message):
        if len(m.command) < 2 and not m.reply_to_message:
            return await m.reply_text(f"❗ {f('Give me a song name or YouTube URL')}\n\n`/play faded`")
        query = " ".join(m.command[1:]) if len(m.command) > 1 else (
            m.reply_to_message.text or m.reply_to_message.caption or ""
        )
        msg = await m.reply_text(f"🔎 {f('Searching')}...")
        track = await yt.get_stream_url(query)
        if not track or not track.get("stream"):
            return await msg.edit(f"❌ {f('No results found')}")

        if PLAYER.is_playing(m.chat.id):
            pos = Q.add(m.chat.id, track)
            return await msg.edit(
                f"➕ **{f('Added to Queue')}** #{pos}\n🎵 `{track['title']}`"
            )

        ok, err = await PLAYER.join_and_play(m.chat.id, track)
        if not ok:
            if err == "no_vc":
                return await msg.edit(f"⚠️ {f('Pls make VC live stream first')}")
            return await msg.edit(f"❌ {f('Error')}: `{err}`")

        await msg.delete()
        text = await _now_playing_text(track, m.chat.title or "")
        if track.get("thumb"):
            try:
                return await m.reply_photo(track["thumb"], caption=text, reply_markup=player_kb(m.chat.id))
            except Exception:
                pass
        await m.reply_text(text, reply_markup=player_kb(m.chat.id))

    # ---- control commands ----
    @app.on_message(filters.command(["pause"]) & filters.group)
    async def pause_c(_, m: Message):
        if not PLAYER.is_playing(m.chat.id):
            return await m.reply_text(f"❎ {f('Nothing playing')}")
        await PLAYER.pause(m.chat.id); await m.reply_text(f"⏸ {f('Paused')}")

    @app.on_message(filters.command(["resume"]) & filters.group)
    async def resume_c(_, m: Message):
        if not PLAYER.is_playing(m.chat.id):
            return await m.reply_text(f"❎ {f('Nothing playing')}")
        await PLAYER.resume(m.chat.id); await m.reply_text(f"▶️ {f('Resumed')}")

    @app.on_message(filters.command(["skip", "next"]) & filters.group)
    async def skip_c(_, m: Message):
        nxt = await PLAYER.skip(m.chat.id)
        if nxt:
            await m.reply_text(f"⏭ {f('Skipped → Now')}: `{nxt['title']}`")
        else:
            await m.reply_text(f"⏹ {f('Queue empty, stopped')}")

    @app.on_message(filters.command(["stop", "end", "leave"]) & filters.group)
    async def stop_c(_, m: Message):
        await PLAYER.stop(m.chat.id); await m.reply_text(f"⏹ {f('Stopped & left VC')}")

    @app.on_message(filters.command(["queue", "q"]) & filters.group)
    async def queue_c(_, m: Message):
        cur = PLAYER.current.get(m.chat.id)
        items = Q.list_items(m.chat.id)
        if not cur and not items:
            return await m.reply_text(f"📭 {f('Queue is empty')}")
        txt = ""
        if cur:
            txt += f"▶️ **{f('Now')}**: `{cur['title']}`\n\n"
        for i, t in enumerate(items, 1):
            txt += f"`{i}.` {t['title']}\n"
        await m.reply_text(txt)

    @app.on_message(filters.command(["song"]))
    async def song_dl(_, m: Message):
        if len(m.command) < 2:
            return await m.reply_text(f"❗ /song <name>")
        msg = await m.reply_text(f"⬇️ {f('Fetching')}...")
        t = await yt.get_stream_url(" ".join(m.command[1:]))
        if not t:
            return await msg.edit(f"❌ {f('Not found')}")
        await msg.edit(
            f"🎵 `{t['title']}`\n⏱ `{yt.fmt_duration(t['duration'])}`\n🔗 {t['url']}"
        )

    # ---- callbacks ----
    @app.on_callback_query(filters.regex(r"^pp:(-?\d+)$"))
    async def cb_pp(_, cq: CallbackQuery):
        cid = int(cq.matches[0].group(1))
        if not PLAYER.is_playing(cid):
            return await cq.answer(f("Nothing playing"), show_alert=True)
        if PLAYER.paused.get(cid):
            await PLAYER.resume(cid); await cq.answer(f("Resumed"))
        else:
            await PLAYER.pause(cid); await cq.answer(f("Paused"))
        try:
            await cq.message.edit_reply_markup(player_kb(cid, PLAYER.paused.get(cid, False)))
        except Exception:
            pass

    @app.on_callback_query(filters.regex(r"^stop:(-?\d+)$"))
    async def cb_stop(_, cq: CallbackQuery):
        cid = int(cq.matches[0].group(1))
        await PLAYER.stop(cid); await cq.answer(f("Stopped"))
        try: await cq.message.edit_reply_markup(None)
        except: pass

    @app.on_callback_query(filters.regex(r"^skip:(-?\d+)$"))
    async def cb_skip(_, cq: CallbackQuery):
        cid = int(cq.matches[0].group(1))
        nxt = await PLAYER.skip(cid)
        await cq.answer(f("Skipped"))
        if nxt:
            await cq.message.reply_text(f"⏭ {f('Now')}: `{nxt['title']}`", reply_markup=player_kb(cid))

    @app.on_callback_query(filters.regex(r"^seek:(-?\d+):(-?\d+)$"))
    async def cb_seek(_, cq: CallbackQuery):
        # py-tgcalls seek requires re-streaming; minimal acknowledge
        await cq.answer(f("Seek requested"))

    @app.on_callback_query(filters.regex(r"^queue:(-?\d+)$"))
    async def cb_queue(_, cq: CallbackQuery):
        cid = int(cq.matches[0].group(1))
        items = Q.list_items(cid)
        if not items:
            return await cq.answer(f("Queue empty"), show_alert=True)
        txt = "\n".join(f"{i+1}. {t['title']}" for i, t in enumerate(items[:10]))
        await cq.answer(txt[:200], show_alert=True)

    @app.on_callback_query(filters.regex(r"^close:"))
    async def cb_close(_, cq: CallbackQuery):
        try: await cq.message.delete()
        except: pass

def _help_text():
    return (
        f"💎 **{f(Config.BOT_NAME)} — Help**\n\n"
        f"▫️ /play <name|url> — {f('Play in VC')}\n"
        f"▫️ /pause /resume — {f('Pause / Resume')}\n"
        f"▫️ /skip — {f('Next track')}\n"
        f"▫️ /stop — {f('Stop & leave VC')}\n"
        f"▫️ /queue — {f('Show queue')}\n"
        f"▫️ /song <name> — {f('Get YT link')}\n"
        f"▫️ /ping — {f('Latency')}\n"
    )

def _cmds_text():
    return _help_text()
