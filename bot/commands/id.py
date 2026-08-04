from telegram import Update
from telegram.ext import ContextTypes

async def id_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    
    text = f"""
**🆔 ID INFO**

**Your User ID:** `{user.id}`
**Your Username:** @{user.username if user.username else 'None'}
**Your Name:** {user.first_name}

**This Chat ID:** `{chat.id}`
**Chat Type:** {chat.type}
    """
    await update.message.reply_text(text, parse_mode='Markdown')