import os, asyncio, aiohttp, aiofiles
from PIL import Image, ImageFilter

ASSETS = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
os.makedirs(ASSETS, exist_ok=True)

async def download_image(url: str, path: str) -> str | None:
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(url, timeout=20) as r:
                if r.status != 200:
                    return None
                data = await r.read()
        async with aiofiles.open(path, "wb") as f:
            await f.write(data)
        return path
    except Exception:
        return None

def make_blur(src: str, dst: str, radius: int = 25) -> str:
    img = Image.open(src).convert("RGB")
    img = img.filter(ImageFilter.GaussianBlur(radius))
    img.save(dst, "JPEG", quality=85)
    return dst

async def ensure_start_images(start_url: str):
    clear_p = os.path.join(ASSETS, "start.jpg")
    blur_p = os.path.join(ASSETS, "start_blur.jpg")
    if not os.path.exists(clear_p):
        await download_image(start_url, clear_p)
    if os.path.exists(clear_p) and not os.path.exists(blur_p):
        make_blur(clear_p, blur_p)
    return clear_p, blur_p
