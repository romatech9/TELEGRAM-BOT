from telegram import Update
from telegram.ext import ContextTypes


async def promote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat

    # Check if command user is admin
    member = await chat.get_member(user.id)
    if member.status not in ["administrator", "creator"]:
        await update.message.reply_text(
            "❌ Only admins can use this command."
        )
        return

    # Must reply to someone
    if not update.message.reply_to_message:
        await update.message.reply_text(
            "❌ Reply to a user to promote them.\n\nExample:\n/promote"
        )
        return

    target = update.message.reply_to_message.from_user

    try:
        await context.bot.promote_chat_member(
            chat_id=chat.id,
            user_id=target.id,
            can_manage_chat=True,
            can_delete_messages=True,
            can_manage_video_chats=True,
            can_restrict_members=True,
            can_promote_members=False,
            can_change_info=True,
            can_invite_users=True,
            can_pin_messages=True,
            can_post_messages=False,
            can_edit_messages=False,
            can_post_stories=False,
            can_edit_stories=False,
            can_delete_stories=False,
            is_anonymous=False,
        )

        await update.message.reply_text(
            f"👑 {target.first_name} has been promoted to Admin."
        )

    except Exception as e:
        await update.message.reply_text(
            f"❌ Failed to promote.\n\nError:\n{e}"
        )


async def demote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat

    # Check if command user is admin
    member = await chat.get_member(user.id)
    if member.status not in ["administrator", "creator"]:
        await update.message.reply_text(
            "❌ Only admins can use this command."
        )
        return

    # Must reply to an admin
    if not update.message.reply_to_message:
        await update.message.reply_text(
            "❌ Reply to the admin you want to demote."
        )
        return

    target = update.message.reply_to_message.from_user

    try:
        await context.bot.promote_chat_member(
            chat_id=chat.id,
            user_id=target.id,
            can_manage_chat=False,
            can_delete_messages=False,
            can_manage_video_chats=False,
            can_restrict_members=False,
            can_promote_members=False,
            can_change_info=False,
            can_invite_users=False,
            can_pin_messages=False,
            can_post_messages=False,
            can_edit_messages=False,
            can_post_stories=False,
            can_edit_stories=False,
            can_delete_stories=False,
            is_anonymous=False,
        )

        await update.message.reply_text(
            f"⬇️ {target.first_name} has been demoted successfully."
        )

    except Exception as e:
        await update.message.reply_text(
            f"❌ Failed to demote.\n\nError:\n{e}"
        )