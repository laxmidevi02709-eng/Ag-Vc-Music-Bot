import asyncio, os, re
import yt_dlp

YDL_AUDIO_OPTS = {
    "format": "bestaudio/best",
    "noplaylist": True,
    "quiet": True,
    "no_warnings": True,
    "outtmpl": "downloads/%(id)s.%(ext)s",
    "geo_bypass": True,
    "nocheckcertificate": True,
}

YDL_SEARCH_OPTS = {"quiet": True, "no_warnings": True, "extract_flat": "in_playlist", "default_search": "ytsearch5"}

def _is_url(q: str) -> bool:
    return bool(re.match(r"https?://", q))

async def search(query: str):
    def _do():
        with yt_dlp.YoutubeDL(YDL_SEARCH_OPTS) as ydl:
            if _is_url(query):
                info = ydl.extract_info(query, download=False)
                return [info]
            info = ydl.extract_info(f"ytsearch1:{query}", download=False)
            return info.get("entries", [])
    return await asyncio.to_thread(_do)

async def download_audio(video_url: str):
    os.makedirs("downloads", exist_ok=True)
    def _do():
        with yt_dlp.YoutubeDL(YDL_AUDIO_OPTS) as ydl:
            info = ydl.extract_info(video_url, download=True)
            path = ydl.prepare_filename(info)
            return path, info
    return await asyncio.to_thread(_do)
