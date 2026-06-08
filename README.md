
# 🎵 THRINO MUSIC BOT

```
╔══════════════════════════════════════════╗
║      🎵  T H R I N O  M U S I C         ║
║         ════════════════════             ║
║   Your Ultimate Voice Chat DJ 🎧         ║
╚══════════════════════════════════════════╝
```

A powerful Telegram voice chat music bot built with **Pyrogram** + **PyTgCalls**.  
Plays YouTube music directly in Telegram group voice chats with a clean queue system.

---

## ✨ Features

| Feature | Details |
|---|---|
| 🎵 Play music | YouTube search or direct URL |
| 🔍 Search & pick | Interactive 5-result picker |
| 📋 Queue system | Auto-plays next song |
| ⏸ Controls | Pause / Resume / Skip / Stop |
| 🔊 Volume control | 1–200% range |
| 📋 Inline buttons | One-tap player controls |
| 🔒 Admin-only | Sensitive commands locked to admins |

---

## 📋 Commands

| Command | Description |
|---|---|
| `/play <song>` | Play a song by name or URL |
| `/search <query>` | Search and pick from 5 results |
| `/pause` | Pause current playback |
| `/resume` | Resume playback |
| `/skip` | Skip to next song |
| `/stop` | Stop and leave voice chat |
| `/queue` | View the current queue |
| `/np` | Show now playing info |
| `/volume <1-200>` | Set playback volume |
| `/help` | Show help menu |

---

## 🚀 Setup Guide

### Step 1 — Get Credentials

1. Go to **https://my.telegram.org/apps** → create an app → copy `API_ID` and `API_HASH`
2. Open **@BotFather** on Telegram → `/newbot` → copy the **Bot Token**
3. Get your **User ID** from **@userinfobot**

---

### 🟢 Option A — Deploy on Railway (Recommended for 24/7)

1. Fork or upload this project to GitHub
2. Go to **https://railway.app** → New Project → Deploy from GitHub repo
3. In the Railway dashboard, go to **Variables** tab and add:

```
API_ID          = your_api_id
API_HASH        = your_api_hash
BOT_TOKEN       = your_bot_token
BOT_USERNAME    = ThrinoMusicBot
OWNER_ID        = your_telegram_user_id
```

4. Railway will auto-detect `nixpacks.toml` and install ffmpeg + Python
5. Click **Deploy** — your bot goes live! ✅

> **Note:** Railway free tier gives 500 hours/month. Use the Hobby plan ($5/mo) for true 24/7.

---

### 🟡 Option B — Run on Termux (Android)

Open Termux and run these commands one by one:

```bash
# 1. Update packages
pkg update && pkg upgrade -y

# 2. Install dependencies
pkg install python ffmpeg git -y

# 3. Clone the bot
git clone https://github.com/yourusername/thrino-music-bot
cd thrino-music-bot

# 4. Install Python packages
pip install -r requirements.txt

# 5. Set your environment variables
export API_ID=your_api_id
export API_HASH=your_api_hash
export BOT_TOKEN=your_bot_token
export BOT_USERNAME=ThrinoMusicBot
export OWNER_ID=your_user_id

# 6. Run the bot
python bot.py
```

**To keep it running after closing Termux:**
```bash
# Install screen
pkg install screen -y

# Start a screen session
screen -S thrino

# Run the bot inside screen
python bot.py

# Detach with: Ctrl+A then D
# Reattach with: screen -r thrino
```

---

## 🔧 Project Structure

```
thrino-music-bot/
├── bot.py              ← Main bot file
├── config.py           ← Configuration & env vars
├── requirements.txt    ← Python dependencies
├── Procfile            ← Railway worker command
├── nixpacks.toml       ← Railway build config (includes ffmpeg)
├── .env.example        ← Environment variable template
├── helpers/
│   ├── __init__.py
│   ├── queue_manager.py ← Song queue logic
│   └── decorators.py    ← Admin permission checks
└── downloads/           ← Auto-created, temp audio files
```

---

## ⚙️ How It Works

1. User runs `/play <song>` in a group with an active voice chat
2. Bot searches YouTube via `yt-dlp`, downloads the audio as MP3
3. `PyTgCalls` streams the audio into the voice chat
4. When the song ends, the next queued track auto-plays
5. Controls (pause/skip/stop) work via commands or inline buttons

---

## 🛠 Troubleshooting

| Problem | Fix |
|---|---|
| `FloodWait` errors | Bot is rate-limited — wait and retry |
| Can't join voice chat | Make sure a voice chat is **active** in the group |
| `ffmpeg not found` | Install it: `pkg install ffmpeg` (Termux) |
| Download fails | Update yt-dlp: `pip install -U yt-dlp` |
| Bot not responding | Check your `BOT_TOKEN` in env vars |

---

## 📜 License

MIT — free to use, modify, and deploy.

---

*Made with ❤️ — Thrino Music Bot*
