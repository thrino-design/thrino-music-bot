from functools import wraps
from pyrogram import Client
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus
from config import Config

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#         🎵 THRINO MUSIC BOT — Decorators
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def admin_only(func):
    """Allow only group admins, sudo users, and owner to use this command."""
    @wraps(func)
    async def wrapper(client: Client, message: Message, *args, **kwargs):
        user_id = message.from_user.id

        # Owner or sudo always pass
        if user_id == Config.OWNER_ID or user_id in Config.SUDO_USERS:
            return await func(client, message, *args, **kwargs)

        # Check group admin status
        try:
            member = await client.get_chat_member(message.chat.id, user_id)
            if member.status in (
                ChatMemberStatus.ADMINISTRATOR,
                ChatMemberStatus.OWNER
            ):
                return await func(client, message, *args, **kwargs)
        except Exception:
            pass

        await message.reply("🔒 **Only group admins can use this command.**")

    return wrapper
