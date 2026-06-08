import os

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#         🎵 THRINO MUSIC BOT — Configuration
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class Config:
    # ── Telegram API ───────────────────────────────
    # Get from https://my.telegram.org/apps
    API_ID       = int(os.environ.get("API_ID", 0))
    API_HASH     = os.environ.get("API_HASH", "")

    # ── Bot Token ──────────────────────────────────
    # Get from @BotFather on Telegram
    BOT_TOKEN    = os.environ.get("BOT_TOKEN", "")

    # ── Bot Info ───────────────────────────────────
    BOT_USERNAME = os.environ.get("BOT_USERNAME", "ThrinoMusicBot")

    # ── Support Chat ───────────────────────────────
    SUPPORT_CHAT = os.environ.get("SUPPORT_CHAT", "https://t.me/yoursupportchat")

    # ── Owner / Sudo Users ─────────────────────────
    # Comma-separated Telegram user IDs
    OWNER_ID     = int(os.environ.get("OWNER_ID", 0))
    SUDO_USERS   = [
        int(x) for x in os.environ.get("SUDO_USERS", "").split(",") if x.strip().isdigit()
    ]

    # ── Download Settings ──────────────────────────
    DOWNLOADS_DIR   = "downloads"
    MAX_QUALITY     = "high"   # low / medium / high
    MAX_DURATION    = 7200     # seconds (2 hours)

    # ── Feature Flags ─────────────────────────────
    LOG_CHANNEL     = int(os.environ.get("LOG_CHANNEL", 0))  # 0 = disabled
