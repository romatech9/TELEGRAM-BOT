import asyncio
import json
import logging
import os

from telegram import Update
from telegram.constants import ChatType, ChatMemberStatus
from telegram.error import BadRequest
from telegram.ext import ContextTypes, Application

STATE_FILE = "zombie_state.json"


def _job_name(chat_id):
    return f"zombies_{chat_id}"


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {"active_chats": []}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


async def _clean_zombies(context: ContextTypes.DEFAULT_TYPE):
    """Automatically removes deleted accounts every 24 hours."""
    chat_id = context.job.data["chat_id"]
    bot = context.bot

    removed = 0
    already_removed = 0

    try:
        chat = await bot.get_chat(chat_id)

        async for member in chat.get_members():

            if not member.user.is_deleted:
                continue

            if member.status in (
                ChatMemberStatus.ADMINISTRATOR,
                ChatMemberStatus.OWNER,
            ):
                continue

            try:
                await bot.ban_chat_member(chat.id, member.user.id)
                await bot.unban_chat_member(chat.id, member.user.id)

                removed += 1
                await asyncio.sleep(0.1)

            except BadRequest:
                already_removed += 1

        await bot.send_message(
            chat.id,
            f"""
🧟 *Auto Zombie Cleanup Complete*

━━━━━━━━━━━━━━

✅ Removed: *{removed}*
📦 Already Gone: *{already_removed}*

━━━━━━━━━━━━━━

Powered By MUFASER-X
""",
            parse_mode="Markdown",
        )

    except Exception as e:
        logging.exception(f"Zombie cleanup failed in {chat_id}: {e}")


async def zombies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/zombies on | off"""

    chat = update.effective_chat
    user = update.effective_user

    # Group only
    if chat.type == ChatType.PRIVATE:
        await update.message.reply_text(
            """
❌ *Group Command Only*

This command was created for groups.

Please add me to a group and use this command there.

Powered By MUFASER-X
""",
            parse_mode="Markdown",
        )
        return

    # User admin check
    user_member = await chat.get_member(user.id)

    if user_member.status not in (
        ChatMemberStatus.ADMINISTRATOR,
        ChatMemberStatus.OWNER,
    ):
        await update.message.reply_text(
            f"""
🚫 *Access Denied*

Sorry {user.first_name},

You don't have enough power to use this command.

🙏 You're not an admin of this group.

Only group admins can enable or disable the Auto Zombie Cleaner.

Powered By MUFASER-X
""",
            parse_mode="Markdown",
        )
        return

    # Bot admin check
    bot_member = await chat.get_member(context.bot.id)

    if bot_member.status not in (
        ChatMemberStatus.ADMINISTRATOR,
        ChatMemberStatus.OWNER,
    ):
        await update.message.reply_text(
            """
❌ *I Need More Power!*

I can't manage zombie accounts because I'm not an admin.

Please promote me to *Administrator* and enable:

✅ Ban Users

Then try again.

Powered By MUFASER-X
""",
            parse_mode="Markdown",
        )
        return

    # Ban permission check
    if not bot_member.can_restrict_members:
        await update.message.reply_text(
            """
⚠️ *Missing Permission*

I'm an admin, but I can't remove zombie accounts.

Please give me the following permission:

✅ Ban Users

Powered By MUFASER-X
""",
            parse_mode="Markdown",
        )
        return

    # No arguments
    if not context.args:
        await update.message.reply_text(
            """
🧟 *Zombie Cleaner*

Usage:

`/zombies on`
Enable automatic cleanup every 24 hours.

`/zombies off`
Disable automatic cleanup.

Powered By MUFASER-X
""",
            parse_mode="Markdown",
        )
        return

    action = context.args[0].lower()

    state = load_state()
    job_name = _job_name(chat.id)

    # Remove old jobs
    for job in context.job_queue.get_jobs_by_name(job_name):
        job.schedule_removal()

    if action == "on":

        context.job_queue.run_repeating(
            _clean_zombies,
            interval=86400,
            first=10,
            name=job_name,
            data={"chat_id": chat.id},
        )

        if chat.id not in state["active_chats"]:
            state["active_chats"].append(chat.id)

        save_state(state)

        await update.message.reply_text(
            """
✅ *Auto Zombie Cleaner Enabled*

The bot will automatically scan this group every *24 hours* and remove deleted Telegram accounts.

Powered By MUFASER-X
""",
            parse_mode="Markdown",
        )

    elif action == "off":

        if chat.id in state["active_chats"]:
            state["active_chats"].remove(chat.id)

        save_state(state)

        await update.message.reply_text(
            """
❌ *Auto Zombie Cleaner Disabled*

Automatic zombie cleanup has been turned off.

Powered By MUFASER-X
""",
            parse_mode="Markdown",
        )

    else:
        await update.message.reply_text(
            """
❌ Invalid option.

Use:

`/zombies on`

or

`/zombies off`

Powered By MUFASER-X
""",
            parse_mode="Markdown",
        )


async def restore_zombie_jobs(application: Application):
    """Restore jobs after bot restart."""

    state = load_state()

    for chat_id in state["active_chats"]:
        application.job_queue.run_repeating(
            _clean_zombies,
            interval=86400,
            first=10,
            name=_job_name(chat_id),
            data={"chat_id": chat_id},
        )

    if state["active_chats"]:
        logging.info(
            f"Restored zombie cleaner in {len(state['active_chats'])} groups."
        )