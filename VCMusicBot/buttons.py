from pyrogram.types import InlineKeyboardButton as B, InlineKeyboardMarkup as M
from .font import f

def player_kb(chat_id: int, paused: bool = False):
    pp = "▶️" if paused else "⏸"
    return M([
        [B("⏮ -10s", f"seek:{chat_id}:-10"),
         B(pp, f"pp:{chat_id}"),
         B("⏹", f"stop:{chat_id}"),
         B("+10s ⏭", f"seek:{chat_id}:10")],
        [B(f("Skip"), f"skip:{chat_id}"),
         B(f("Queue"), f"queue:{chat_id}"),
         B(f("Close"), f"close:{chat_id}")],
    ])

def start_kb(blurred: bool = True):
    if blurred:
        return M([[B(f("Reveal"), "reveal")]])
    return M([
        [B(f("Help"), "help"), B(f("Commands"), "cmds")],
        [B(f("Add me to Group"), url="https://t.me/?startgroup=true")],
    ])

def help_kb():
    return M([[B(f("Back"), "start_back")]])
