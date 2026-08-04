from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    name = update.effective_user.first_name
    bot_name = context.bot.username
    
    text = f"👋 *Hello {name}!*\n\n" \
           f"*MUFASER-X* is the most advanced AI Bot\n" \
           f"to help you *manage* your groups easily\n" \
           f"and *safely*!\n\n" \
           f"✨ *Features:*\n" \
           f"☛ 💬 AI Chat with Gemini 2.5 Flash\n" \
           f"☛ 🎨 Generate Images & Stickers\n" \
           f"☛ 🛡️ Group Management Tools\n" \
           f"☛ 🌐 Translate 100+ Languages\n" \
           f"❓ Press /help to see all commands\n" \
           f"🥰 I'm here to be your assistant!"
    
    keyboard = [
        [InlineKeyboardButton("➕ Add me to a Group ➕", url=f"https://t.me/{bot_name}?startgroup=true")],
        [InlineKeyboardButton("🧑‍💻 OWNER", url="https://t.me/ROMATECH6")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        text, 
        reply_markup=reply_markup, 
        parse_mode="Markdown")