from telegram import Update
from telegram.ext import ContextTypes


async def chatinfo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat

    chat_type = {
        "private": "Private Chat 👤",
        "group": "Group 👥",
        "supergroup": "Super Group 🌍",
        "channel": "Channel 📢"
    }.get(chat.type, chat.type)

    text = f"""
💬 CHAT INFORMATION

━━━━━━━━━━━━━━

🆔 Chat ID:
`{chat.id}`

📛 Chat Name:
{chat.title or update.effective_user.full_name}

📂 Chat Type:
{chat_type}

👤 Username:
@{chat.username if chat.username else 'None'}

━━━━━━━━━━━━━━

Powered By MUFASER-X
"""

    await update.message.reply_text(
        text,
        parse_mode="Markdown"
    )