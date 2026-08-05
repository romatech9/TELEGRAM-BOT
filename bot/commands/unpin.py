from telegram import Update
from telegram.ext import ContextTypes

async def unpin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat or update.effective_chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("❌ This command only works in groups.")
        return

    member = await context.bot.get_chat_member(
        update.effective_chat.id,
        update.effective_user.id
    )

    if member.status not in ["administrator", "creator"]:
        await update.message.reply_text("❌ Only admins can unpin messages.")
        return

    try:
        await context.bot.unpin_all_chat_messages(update.effective_chat.id)
        await update.message.reply_text("📍 All pinned messages have been unpinned.")
    except Exception as e:
        await update.message.reply_text(f"❌ {e}")