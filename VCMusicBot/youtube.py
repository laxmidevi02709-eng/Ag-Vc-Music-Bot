import asyncio, os, re
import yt_dlp

YDL_OPTS = {
    "format": "bestaudio/best",
    "noplaylist": True,
    "quiet": True,
    "no_warnings": True,
    "geo_bypass": True,
    "nocheckcertificate": True,
    "default_search": "ytsearch",
    "source_address": "0.0.0.0",
}

def _is_url(q: str) -> bool:
    return bool(re.match(r"^https?://", q))

async def search(query: str) -> dict | None:
    loop = asyncio.get_event_loop()
    def _run():
        with yt_dlp.YoutubeDL({**YDL_OPTS, "extract_flat": False}) as ydl:
            try:
                if _is_url(query):
                    info = ydl.extract_info(query, download=False)
                else:
                    info = ydl.extract_info(f"ytsearch1:{query}", download=False)
                    if "entries" in info:
                        info = info["entries"][0]
                return info
            except Exception:
                return None
    return await loop.run_in_executor(None, _run)

async def get_stream_url(query_or_url: str):
    info = await search(query_or_url)
    if not info:
        return None
    return {
        "title": info.get("title", "Unknown"),
        "duration": info.get("duration", 0),
        "url": info.get("webpage_url") or info.get("url"),
        "thumb": (info.get("thumbnail") or
                  (info.get("thumbnails", [{}])[-1].get("url") if info.get("thumbnails") else None)),
        "stream": info.get("url"),
        "uploader": info.get("uploader", ""),
        "id": info.get("id"),
    }

def fmt_duration(sec):
    try:
        sec = int(sec or 0)
    except Exception:
        return "Live"
    h, r = divmod(sec, 3600)
    m, s = divmod(r, 60)
    return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"
