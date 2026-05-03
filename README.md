# 💎 Premium VC Music Bot

Telegram voice-chat music streaming bot — premium UI, blurred start image with reveal, mathematical sans-serif fonts everywhere, inline player controls, YouTube search & direct URL support. One-shot deploy on **Render** via Docker.

## ✨ Features

- 🎬 **Blurred start image** that reveals on tap (PIL-based)
- 🔤 **Premium font** (`𝖺𝖻𝖼…𝟢𝟣𝟤`) on every text & button
- 🎵 `/play` with YouTube search or direct URL
- 🎛 Inline controls — Play / Pause / Stop / Skip / Seek (±10s) / Queue
- 📜 Queue manager (per-chat)
- 🛰 Auto-detects "no live VC" → replies `Pls make VC live stream first`
- 🖼 Sends **YouTube thumbnail** with the now-playing message
- 🧠 Auto-skip on stream end
- 📦 One-click Render Docker deploy (`render.yaml`)

## 🚀 Deploy on Render (one shot)

1. Create a public/private GitHub repo and push these files.
2. Generate `SESSION_STRING` locally (assistant user account):
   ```bash
   pip install pyrogram tgcrypto
   python gen_session.py
   ```
3. Render → **New** → **Blueprint** → connect this repo. Render reads `render.yaml`.
4. Fill the env vars when prompted:
   - `API_ID` — from https://my.telegram.org
   - `API_HASH` — from https://my.telegram.org
   - `BOT_TOKEN` — from @BotFather
   - `SESSION_STRING` — output of `gen_session.py`
   - `OWNER_ID` — your Telegram user id
   - `LOG_GROUP_ID` *(optional)* — startup log group
5. Click **Apply**. The Docker worker installs FFmpeg + deps and launches.

## 📲 Group setup

1. Add the **bot** to your group → make it admin.
2. Add the **assistant account** (the one whose session you generated) to the same group.
3. Start a Voice Chat in the group.
4. Use `/play <song>`. Done.

## 📜 Commands

| Command | Description |
|---|---|
| `/start` | Premium blurred-reveal welcome |
| `/help` | List commands |
| `/play <q>` | Play song / queue |
| `/pause` `/resume` | Toggle playback |
| `/skip` | Next in queue |
| `/stop` | Stop & leave VC |
| `/queue` | Show queue |
| `/song <q>` | Fetch YouTube link |
| `/ping` | Latency check |

## 🛠 Local run (optional)

```bash
docker build -t vcmusic .
docker run --env-file .env vcmusic
```
