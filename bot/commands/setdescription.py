from telegram import Update
from telegram.ext import ContextTypes

async def setdescription_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("❌ This command only works in groups.")
        return

    member = await context.bot.get_chat_member(
        update.effective_chat.id,
        update.effective_user.id
    )

    if member.status not in ["administrator", "creator"]:
        await update.message.reply_text("❌ Only group admins can change the group description.")
        return

    if not context.args:
        await update.message.reply_text(
            "❌ Usage:\n/setdescription <new group description>"
        )
        return

    description = " ".join(context.args)

    try:
        await context.bot.set_chat_description(
            chat_id=update.effective_chat.id,
            description=description
        )

        await update.message.reply_text(
            f"✅ Group description updated successfully.\n\n📝 New description:\n{description}"
        )

    except Exception as e:
        await update.message.reply_text(f"❌ Failed to update description.\n{e}")