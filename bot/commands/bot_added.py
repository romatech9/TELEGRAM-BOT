from telegram import Update
from telegram.ext import ContextTypes
from voice import text_to_voice


async def bot_added(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.my_chat_member:
        return

    old_status = update.my_chat_member.old_chat_member.status
    new_status = update.my_chat_member.new_chat_member.status

    # Bot has been added to a group
    if old_status in ("left", "kicked") and new_status in ("member", "administrator"):

        welcome_text = (
            "Hello everyone. 👋 "
            "My name is MUFASER-X, your intelligent Telegram assistant. "
            "Thank you so much for adding me to this wonderful group. "
            "I am here to help manage your group, protect it from spam, "
            "remove unwanted links, answer your questions using artificial intelligence, "
            "create images, write stories, write poems, translate languages, "
            "download music, and much more. "
            "To see everything I can do, simply type slash help. "
            "Thank you once again for choosing MUFASER-X. "
            "I wish everyone a wonderful day."
        )

        try:
            # text_to_voice returns a BytesIO object
            voice = text_to_voice(welcome_text)

            await context.bot.send_voice(
                chat_id=update.effective_chat.id,
                voice=voice,
                filename="welcome.ogg",
                caption="🎙️ Welcome from MUFASER-X"
            )

            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=(
                    "🤖 *MUFASER-X has joined the group!*\n\n"
                    "🎤 I have sent a welcome voice note.\n"
                    "📚 Type /help to see all my commands.\n\n"
                    "✨ Let's make this group amazing together!"
                ),
                parse_mode="Markdown"
            )

        except Exception as e:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"❌ Failed to send welcome voice.\n\n{e}"
            )