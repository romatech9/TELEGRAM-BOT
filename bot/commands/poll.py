from telegram import Update
from telegram.ext import ContextTypes

async def poll_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("❌ This command only works in groups.")
        return

    member = await context.bot.get_chat_member(
        update.effective_chat.id,
        update.effective_user.id
    )

    if member.status not in ["administrator", "creator"]:
        await update.message.reply_text("❌ Only group admins can create polls.")
        return

    text = " ".join(context.args)

    if "|" not in text:
        await update.message.reply_text(
            "❌ Usage:\n"
            "/poll Question | Option 1 | Option 2 | Option 3"
        )
        return

    parts = [x.strip() for x in text.split("|")]

    question = parts[0]
    options = parts[1:]

    if len(options) < 2:
        await update.message.reply_text("❌ A poll must have at least 2 options.")
        return

    if len(options) > 10:
        await update.message.reply_text("❌ A poll can have a maximum of 10 options.")
        return

    await context.bot.send_poll(
        chat_id=update.effective_chat.id,
        question=question,
        options=options,
        is_anonymous=False,
        allows_multiple_answers=False,
    )