from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """🚀 *MUFASER-X-BOT* 🤖

The most advanced AI bot for Telegram
powered by Gemini 2.5 Flash + 100 API keys.

🌐 *BOT INFORMATION*
➥ Hello see what I can do
➥ Translator(100+ languages)
➥ Teach you coding
➥ Group Management e.t.c

💅 *DOWNLOADS MENU*
➥ Media downloads
➥ Chat with AI chat
➥ Generate images
➥ web coding
➥ TikTok videos
➥ Creative writing
➥ YouTube videos
➥ Download Music

🎯 *GAMES MENU*
➥ Truth or Dare
➥ Be My Date

🙏 *FATHER COMMANDS*
➥ /gm Good Morning
➥ /bless Blessing message

*𝐍𝐎𝐓𝐄*࿐
➥ *𝐁𝐎𝐓 𝐌𝐔𝐒𝐓 𝐁𝐄 𝐀𝐃𝐌𝐈𝐍*
𖣐 *COMMANDS 100+📒*
"""
    keyboard = [
        [
            InlineKeyboardButton("📢 GROUP", url="https://t.me/+pHixjzGHsGg2MzU0"),
            InlineKeyboardButton("🤗 ABOUT US", url="romatech9.github.io")
        ],
        [
            InlineKeyboardButton("🧑‍💻 ALL COMMANDS", callback_data="all_cmd")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo="https://i.ibb.co/Rkg7Xg3Z/f32cdd6b4969.jpg",
        caption=help_text,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def all_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
🚀 *MUFASER-X-BOT* 🤖

🌐 *INFO & AI*
/start /help /ping /id /ai /reset /status /explain /translate /math /quiz /story /poem /summarize  /weather /currency /url 

💅 *MEDIA & FUN*
/joke /fact /tts /image /meme /sticker /wallpaper  /song /video /lyrics /logo /avatar /anime 
/remix /play 

🎯 *GROUP MANAGEMENT*
/ban /kick /mute /unmute /warn /warns /purge /tagall /rank /promote /demote /setwelcome /setrules /setwarns /setwarnmode /setwarnlimit /setwarntext /setwarnmedia /setwarnsticker /setwarnphoto /setwarnvideo /setwarnvoice /goodbye 
/settings /setdescription /poll /userinfo /chatinfo /welcome /antilink   etc.

*NOTE*~ BOT MUST BE ADMIN
"""
    if update.callback_query:
        await update.callback_query.message.reply_text(help_text, parse_mode="Markdown")
    else:
        await update.message.reply_text(help_text, parse_mode="Markdown")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "all_cmd":
        await all_command(update, context)