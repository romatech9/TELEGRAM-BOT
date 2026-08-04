from telegram import Update
from telegram.ext import ContextTypes

# This will be linked to ai.py's conversation_history in main.py
conversation_history = {}

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Clear AI memory
    if user_id in conversation_history:
        conversation_history[user_id] = []
        context.user_data.clear()
    
    text = f"""╭─〔 🧹 𝗥𝗘𝗦𝗘𝗧 𝗗𝗢𝗡𝗘 〕
│
│ ✅ *Your chat history is cleared*
│ 🤖 *AI has forgotten everything*
│
│ Start fresh with `/ai your message`
│
╰─〔 MUFASER-X 〕"""
    
    await update.message.reply_text(text, parse_mode='Markdown')