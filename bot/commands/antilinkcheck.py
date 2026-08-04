import asyncio
import re
import logging

from telegram import Update, ChatPermissions
from telegram.ext import ContextTypes

from .antilinkdata import (
    is_enabled,
    get_mode,
    add_warning,
    warning_reached,
    reset_warning,
    mute_time
)

logger = logging.getLogger(__name__)

# ==========================================
# MUFASER-X LINK DETECTOR
# ==========================================

LINK_PATTERN = re.compile(
    r"(https?://|www\.|t\.me/|telegram\.me/|chat\.whatsapp\.com|"
    r"wa\.me/|discord\.gg|discord\.com|x\.com|twitter\.com|"
    r"facebook\.com|fb\.com|instagram\.com|youtube\.com|"
    r"youtu\.be|tiktok\.com)",
    re.IGNORECASE
)

# ==========================================
# CHECK LINKS
# ==========================================

async def anti_link_checker(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if not update.message:
        return

    chat_id = update.effective_chat.id
    user = update.effective_user
    text = update.message.text or ""

    # Anti-Link OFF
    if not is_enabled(chat_id):
        return

    # No link found - let XP run
    if not LINK_PATTERN.search(text):
        return

    # ==================================
    # IGNORE ADMINS AND OWNER
    # ==================================
    try:
        member = await context.bot.get_chat_member(chat_id, user.id)
    except:
        return

    if member.status in ["administrator", "creator"]:
        return
    if user.id == context.bot.id:
        return

    OWNER_ID = 8369264435   # CHANGE THIS TO YOUR TELEGRAM ID
    if user.id == OWNER_ID:
        return

    mode = get_mode(chat_id)

    # Delete message first
    deleted = False
    try:
        await update.message.delete()
        deleted = True
    except Exception as e:
        logger.error(f"MUFASER-X Can't delete message: {e}")
        await context.bot.send_message(chat_id, "⚠️ I don't have permission to delete messages. Make me admin!")

    # ==================================
    # DELETE MODE
    # ==================================
    if mode == "delete":
        if deleted:
            await context.bot.send_message(
                chat_id,
                "🗑 Link Deleted\nPlease avoid sending links.\n\nPowered By MUFASER-X"
            )

    # ==================================
    # WARN MODE
    # ==================================
    elif mode == "warn":
        warns = add_warning(chat_id, user.id)
        if warns < 3:
            await context.bot.send_message(
                chat_id,
                f"⚠️ Link Detected\n👤 User: {user.first_name}\n📊 Warning: {warns}/3\nPlease don't send links.\n\nPowered By MUFASER-X"
            )
        else:
            await context.bot.send_message(
                chat_id,
                f"🚫 Warning Limit Reached\n👤 {user.first_name}\n\nMuted for 20 minutes.\n\nPowered By MUFASER-X"
            )
            await context.bot.restrict_chat_member(
                chat_id, user.id,
                permissions=ChatPermissions(can_send_messages=False)
            )
            async def unmute_user():
                await asyncio.sleep(mute_time(chat_id) * 60)
                await context.bot.restrict_chat_member(
                    chat_id, user.id,
                    permissions=ChatPermissions(
                        can_send_messages=True,
                        can_send_media_messages=True,
                        can_send_polls=True,
                        can_send_other_messages=True
                    )
                )
                reset_warning(chat_id, user.id)
                await context.bot.send_message(
                    chat_id,
                    f"✅ {user.first_name} has been automatically unmuted.\n\nPowered By MUFASER-X"
                )
            asyncio.create_task(unmute_user())

    # ==================================
    # KICK MODE
    # ==================================
    elif mode == "kick":
        await context.bot.ban_chat_member(chat_id, user.id)
        await context.bot.unban_chat_member(chat_id, user.id)
        await context.bot.send_message(
            chat_id,
            f"🚪 Forbidden Link Detected\n👤 {user.first_name}\n\nUser removed from the group.\n\nPowered By MUFASER-X"
        )

    # ==================================
    # BAN MODE
    # ==================================
    elif mode == "ban":
        await context.bot.ban_chat_member(chat_id, user.id)
        await context.bot.send_message(
            chat_id,
            f"🚫 Forbidden Link Detected\n👤 {user.first_name}\n\nUser has been permanently banned.\n\nPowered By MUFASER-X"
        )

    return -1  # <--- THIS STOPS XP AND AUTO_CHAT