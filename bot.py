import os
import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import FloodWait, UserAlreadyParticipant
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped, AudioVideoPiped
from pytgcalls.types.input_stream import AudioParameters
from yt_dlp import YoutubeDL
import re
from config import Config
from helpers.decorators import admin_only
from helpers.queue_manager import QueueManager
from config import Config
COOKIES_FILE = os.environ.get("COOKIES_FILE", "cookies.txt")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#         🎵 THRINO MUSIC BOT — Core Engine
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# Initialize clients
app = Client(
    "thrino_music_bot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN
)

call_py = PyTgCalls(app)
queue = QueueManager()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#              YouTube / Search Engine
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

YDL_OPTS = {
    "format": "bestaudio/best",
    "outtmpl": "downloads/%(id)s.%(ext)s",
    "quiet": True,
    "no_warnings": True,
    "default_search": "ytsearch",
    "cookiefile": COOKIES_FILE,
    "postprocessors": [{
        "key": "FFmpegExtractAudio",
        "preferredcodec": "mp3",
        "preferredquality": "192",
    }],
}

def search_youtube(query: str):
    with YoutubeDL({
        "quiet": True,
        "default_search": "ytsearch1",
        "skip_download": True,
        "cookiefile": COOKIES_FILE
    }) as ydl:
        info = ydl.extract_info(f"ytsearch1:{query}", download=False)

        if info and "entries" in info and info["entries"]:
            entry = info["entries"][0]

            return {
                "title": entry.get("title", "Unknown"),
                "url": entry.get("webpage_url"),
                "duration": entry.get("duration", 0),
                "thumbnail": entry.get("thumbnail", ""),
                "channel": entry.get("channel", "Unknown"),
            }
    return None

def download_audio(url: str) -> str | None:
    os.makedirs("downloads", exist_ok=True)
    with YoutubeDL(YDL_OPTS) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info).rsplit(".", 1)[0] + ".mp3"
        return filename if os.path.exists(filename) else None

def format_duration(seconds: int) -> str:
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#                  Inline Keyboards
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def player_keyboard(chat_id: int):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⏸ Pause", callback_data=f"pause_{chat_id}"),
            InlineKeyboardButton("▶️ Resume", callback_data=f"resume_{chat_id}"),
            InlineKeyboardButton("⏭ Skip", callback_data=f"skip_{chat_id}"),
        ],
        [
            InlineKeyboardButton("⏹ Stop", callback_data=f"stop_{chat_id}"),
            InlineKeyboardButton("📋 Queue", callback_data=f"queue_{chat_id}"),
        ]
    ])

def search_keyboard(results: list, query: str):
    buttons = []
    for i, r in enumerate(results[:5]):
        duration = format_duration(r.get("duration", 0))
        title = r["title"][:35] + "…" if len(r["title"]) > 35 else r["title"]
        buttons.append([InlineKeyboardButton(f"🎵 {title} [{duration}]", callback_data=f"play_search_{i}")])
    buttons.append([InlineKeyboardButton("❌ Cancel", callback_data="cancel_search")])
    return InlineKeyboardMarkup(buttons)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#                   Bot Commands
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.on_message(filters.command("start"))
async def start_cmd(client: Client, message: Message):
    banner = """
╔══════════════════════════════════════╗
║      🎵  T H R I N O  M U S I C     ║
║         ═══════════════════          ║
║   Your Ultimate Voice Chat DJ 🎧     ║
╚══════════════════════════════════════╝

**Commands:**
• `/play <song>` — Play a song 🎵
• `/search <query>` — Search & pick 🔍
• `/pause` — Pause playback ⏸
• `/resume` — Resume playback ▶️
• `/skip` — Skip current song ⏭
• `/stop` — Stop & leave ⏹
• `/queue` — View queue 📋
• `/np` — Now playing 🎶
• `/volume <1-200>` — Set volume 🔊
• `/lyrics <song>` — Get lyrics 📝
• `/help` — Show this menu ❓

_Powered by Thrino Music Bot_ ⚡
"""
    await message.reply_text(
        banner,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Add to Group", url=f"https://t.me/{Config.BOT_USERNAME}?startgroup=true")],
            [InlineKeyboardButton("📢 Support", url=Config.SUPPORT_CHAT)],
        ])
    )

@app.on_message(filters.command("help"))
async def help_cmd(client: Client, message: Message):
    await start_cmd(client, message)

@app.on_message(filters.command(["play", "p"]) & filters.group)
async def play_cmd(client: Client, message: Message):
    chat_id = message.chat.id

    if len(message.command) < 2:
        return await message.reply("🎵 Usage: `/play <song name or URL>`")

    query = " ".join(message.command[1:])
    status_msg = await message.reply("🔍 **Searching...** Please wait.")

    # URL or search
    is_url = re.match(r"https?://", query)
    if is_url:
        info = {"url": query, "title": query, "duration": 0, "channel": "Direct URL"}
    else:
        info = search_youtube(query)

    if not info:
        return await status_msg.edit("❌ **No results found.** Try a different search.")

    title = info["title"]
    duration = format_duration(info.get("duration", 0))
    channel = info.get("channel", "Unknown")

    if queue.is_active(chat_id):
        queue.add(chat_id, info)
        pos = queue.length(chat_id)
        return await status_msg.edit(
            f"📋 **Added to Queue #{pos}**\n\n"
            f"🎵 **{title}**\n"
            f"👤 {channel} | ⏱ {duration}"
        )

    await status_msg.edit(f"⬇️ **Downloading:** `{title}`...")

    filepath = download_audio(info["url"])
    if not filepath:
        return await status_msg.edit("❌ **Download failed.** Try another song.")

    try:
        await call_py.join_group_call(
            chat_id,
            AudioPiped(filepath, AudioParameters.from_quality("high")),
            stream_type="local_stream"
        )
        queue.set_active(chat_id, info)
        await status_msg.edit(
            f"🎵 **Now Playing**\n\n"
            f"**{title}**\n"
            f"👤 {channel}  |  ⏱ {duration}\n\n"
            f"_Thrino Music Bot_ 🎧",
            reply_markup=player_keyboard(chat_id)
        )
    except Exception as e:
        logger.error(f"Play error: {e}")
        await status_msg.edit(f"❌ **Error joining voice chat.**\nMake sure a voice chat is active.\n\n`{e}`")

@app.on_message(filters.command("search") & filters.group)
async def search_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply("🔍 Usage: `/search <song name>`")

    query = " ".join(message.command[1:])
    msg = await message.reply("🔍 **Searching YouTube...**")

    try:
        with YoutubeDL({"quiet": True, "default_search": "ytsearch5", "skip_download": True}) as ydl:
            info = ydl.extract_info(f"ytsearch5:{query}", download=False)
            results = info.get("entries", [])[:5] if info else []
    except Exception as e:
        return await msg.edit(f"❌ Search error: `{e}`")

    if not results:
        return await msg.edit("❌ **No results found.**")

    # Store results temporarily in queue manager
    queue.set_search_cache(message.from_user.id, results)

    text = "🔍 **Search Results:**\n\n"
    for i, r in enumerate(results, 1):
        dur = format_duration(r.get("duration", 0))
        text += f"`{i}.` **{r['title'][:50]}**\n   ⏱ {dur}  |  👤 {r.get('channel', 'Unknown')}\n\n"

    await msg.edit(text, reply_markup=search_keyboard(results, query))

@app.on_message(filters.command("pause") & filters.group)
@admin_only
async def pause_cmd(client: Client, message: Message):
    try:
        await call_py.pause_stream(message.chat.id)
        await message.reply("⏸ **Paused.**")
    except Exception as e:
        await message.reply(f"❌ `{e}`")

@app.on_message(filters.command("resume") & filters.group)
@admin_only
async def resume_cmd(client: Client, message: Message):
    try:
        await call_py.resume_stream(message.chat.id)
        await message.reply("▶️ **Resumed.**")
    except Exception as e:
        await message.reply(f"❌ `{e}`")

@app.on_message(filters.command("skip") & filters.group)
@admin_only
async def skip_cmd(client: Client, message: Message):
    chat_id = message.chat.id
    next_track = queue.next(chat_id)
    if not next_track:
        await call_py.leave_group_call(chat_id)
        queue.clear(chat_id)
        return await message.reply("⏹ **Queue ended. Left voice chat.**")

    filepath = download_audio(next_track["url"])
    if not filepath:
        return await message.reply("❌ **Failed to download next track.**")

    await call_py.change_stream(chat_id, AudioPiped(filepath))
    await message.reply(
        f"⏭ **Skipped!**\n\n🎵 Now playing: **{next_track['title']}**",
        reply_markup=player_keyboard(chat_id)
    )

@app.on_message(filters.command("stop") & filters.group)
@admin_only
async def stop_cmd(client: Client, message: Message):
    chat_id = message.chat.id
    try:
        await call_py.leave_group_call(chat_id)
        queue.clear(chat_id)
        await message.reply("⏹ **Stopped and left voice chat.**")
    except Exception as e:
        await message.reply(f"❌ `{e}`")

@app.on_message(filters.command("queue") & filters.group)
async def queue_cmd(client: Client, message: Message):
    chat_id = message.chat.id
    current = queue.get_current(chat_id)
    upcoming = queue.get_queue(chat_id)

    if not current and not upcoming:
        return await message.reply("📋 **Queue is empty.**")

    text = "📋 **Current Queue:**\n\n"
    if current:
        text += f"🎵 **Now Playing:**\n`→` {current['title']}\n\n"

    if upcoming:
        text += "**Up Next:**\n"
        for i, track in enumerate(upcoming[:10], 1):
            text += f"`{i}.` {track['title'][:45]}\n"
        if len(upcoming) > 10:
            text += f"\n_...and {len(upcoming) - 10} more_"

    await message.reply(text)

@app.on_message(filters.command("np") & filters.group)
async def nowplaying_cmd(client: Client, message: Message):
    current = queue.get_current(message.chat.id)
    if not current:
        return await message.reply("🔇 **Nothing is playing right now.**")

    dur = format_duration(current.get("duration", 0))
    await message.reply(
        f"🎶 **Now Playing**\n\n"
        f"**{current['title']}**\n"
        f"👤 {current.get('channel', 'Unknown')}  |  ⏱ {dur}",
        reply_markup=player_keyboard(message.chat.id)
    )

@app.on_message(filters.command("volume") & filters.group)
@admin_only
async def volume_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply("🔊 Usage: `/volume <1-200>`")
    try:
        vol = int(message.command[1])
        vol = max(1, min(200, vol))
        await call_py.change_volume_call(message.chat.id, vol)
        await message.reply(f"🔊 **Volume set to {vol}%**")
    except ValueError:
        await message.reply("❌ Provide a number between 1 and 200.")
    except Exception as e:
        await message.reply(f"❌ `{e}`")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#                Callback Handlers
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.on_callback_query()
async def callback_handler(client: Client, cb: CallbackQuery):
    data = cb.data
    user_id = cb.from_user.id

    if data.startswith("pause_"):
        chat_id = int(data.split("_")[1])
        await call_py.pause_stream(chat_id)
        await cb.answer("⏸ Paused!", show_alert=False)

    elif data.startswith("resume_"):
        chat_id = int(data.split("_")[1])
        await call_py.resume_stream(chat_id)
        await cb.answer("▶️ Resumed!", show_alert=False)

    elif data.startswith("skip_"):
        chat_id = int(data.split("_")[1])
        next_track = queue.next(chat_id)
        if not next_track:
            await call_py.leave_group_call(chat_id)
            queue.clear(chat_id)
            await cb.answer("⏹ Queue ended!", show_alert=True)
            return
        filepath = download_audio(next_track["url"])
        if filepath:
            await call_py.change_stream(chat_id, AudioPiped(filepath))
            await cb.answer(f"⏭ Now playing: {next_track['title'][:30]}", show_alert=False)

    elif data.startswith("stop_"):
        chat_id = int(data.split("_")[1])
        await call_py.leave_group_call(chat_id)
        queue.clear(chat_id)
        await cb.answer("⏹ Stopped!", show_alert=True)

    elif data.startswith("queue_"):
        chat_id = int(data.split("_")[1])
        upcoming = queue.get_queue(chat_id)
        current = queue.get_current(chat_id)
        text = "📋 Queue is empty."
        if current or upcoming:
            text = f"🎵 Now: {current['title'][:40]}\n" if current else ""
            for i, t in enumerate(upcoming[:5], 1):
                text += f"{i}. {t['title'][:40]}\n"
        await cb.answer(text, show_alert=True)

    elif data.startswith("play_search_"):
        idx = int(data.split("_")[2])
        results = queue.get_search_cache(user_id)
        if not results or idx >= len(results):
            return await cb.answer("❌ Search expired.", show_alert=True)

        track = results[idx]
        chat_id = cb.message.chat.id

        await cb.message.edit(f"⬇️ **Downloading:** `{track['title']}`...")
        filepath = download_audio(track["url"])
        if not filepath:
            return await cb.message.edit("❌ Download failed.")

        if queue.is_active(chat_id):
            queue.add(chat_id, track)
            pos = queue.length(chat_id)
            await cb.message.edit(f"📋 Added to queue #{pos}: **{track['title']}**")
        else:
            await call_py.join_group_call(
                chat_id,
                AudioPiped(filepath, AudioParameters.from_quality("high"))
            )
            queue.set_active(chat_id, track)
            dur = format_duration(track.get("duration", 0))
            await cb.message.edit(
                f"🎵 **Now Playing**\n\n**{track['title']}**\n⏱ {dur}",
                reply_markup=player_keyboard(chat_id)
            )

    elif data == "cancel_search":
        await cb.message.delete()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#              PyTgCalls Event Handlers
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@call_py.on_stream_end()
async def stream_ended(client, update):
    chat_id = update.chat_id
    next_track = queue.next(chat_id)
    if next_track:
        filepath = download_audio(next_track["url"])
        if filepath:
            await call_py.change_stream(chat_id, AudioPiped(filepath))
            await app.send_message(
                chat_id,
                f"⏭ **Auto-playing next:**\n🎵 **{next_track['title']}**",
                reply_markup=player_keyboard(chat_id)
            )
    else:
        queue.clear(chat_id)
        await call_py.leave_group_call(chat_id)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#                    Startup
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def main():
    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    logger.info("  🎵  Thrino Music Bot — Starting Up")
    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    await app.start()
    await call_py.start()
    me = await app.get_me()
    logger.info(f"  ✅  Logged in as @{me.username}")
    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
