import logging, asyncio
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream, AudioQuality
from pytgcalls.exceptions import NoActiveGroupCall

from . import queue as Q

log = logging.getLogger(__name__)

class Player:
    def __init__(self, user_client):
        self.user = user_client
        self.calls = PyTgCalls(user_client)
        self.current: dict[int, dict] = {}
        self.paused: dict[int, bool] = {}

    async def start(self):
        await self.calls.start()

    async def join_and_play(self, chat_id: int, track: dict):
        try:
            await self.calls.play(
                chat_id,
                MediaStream(track["stream"], audio_parameters=AudioQuality.HIGH),
            )
            self.current[chat_id] = track
            self.paused[chat_id] = False
            return True, None
        except NoActiveGroupCall:
            return False, "no_vc"
        except Exception as e:
            log.exception("play err")
            return False, str(e)

    async def skip(self, chat_id: int):
        nxt = Q.pop(chat_id)
        if not nxt:
            await self.stop(chat_id)
            return None
        ok, err = await self.join_and_play(chat_id, nxt)
        return nxt if ok else None

    async def pause(self, chat_id: int):
        await self.calls.pause_stream(chat_id)
        self.paused[chat_id] = True

    async def resume(self, chat_id: int):
        await self.calls.resume_stream(chat_id)
        self.paused[chat_id] = False

    async def stop(self, chat_id: int):
        Q.clear(chat_id)
        self.current.pop(chat_id, None)
        self.paused.pop(chat_id, None)
        try:
            await self.calls.leave_call(chat_id)
        except Exception:
            pass

    def is_playing(self, chat_id: int) -> bool:
        return chat_id in self.current

    def setup_handlers(self, on_end):
        from pytgcalls import filters as fl
        @self.calls.on_update(fl.stream_end())
        async def _(_, update):
            await on_end(update.chat_id)
