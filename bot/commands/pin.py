from telegram import Update
from telegram.ext import ContextTypes

async def pin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat or update.effective_chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("❌ This command only works in groups.")
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Reply to a message you want to pin.")
        return

    member = await context.bot.get_chat_member(
        update.effective_chat.id,
        update.effective_user.id
    )

    if member.status not in ["administrator", "creator"]:
        await update.message.reply_text("❌ Only admins can pin messages.")
        return

    try:
        await update.message.reply_to_message.pin(disable_notification=False)
        await update.message.reply_text("📌 Message pinned successfully.")
    except Exception as e:
        await update.message.reply_text(f"❌ {e}")