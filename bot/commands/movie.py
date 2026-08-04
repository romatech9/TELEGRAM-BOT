import asyncio
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

def format_duration(seconds):
    if seconds is None: return "Unknown"
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h: return f"{h}:{m:02}:{s:02}"
    return f"{m}:{s:02}"

async def search_youtube(query):
    loop = asyncio.get_event_loop()
    ydl_opts = {
        "noplaylist": True,
        "quiet": True,
        "default_search": "ytsearch1",
        "extractor_args": {"youtube": {"player_client": ["android", "web"]}},
        "http_headers": {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
        "extractor_retries": 3,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = await loop.run_in_executor(None, lambda: ydl.extract_info(query, download=False))
        if "entries" in info:
            info = info["entries"][0]
        return info

async def movie_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("🎬 Usage: /movie <movie name>\n\nExample: /movie John Wick 4")
        return

    query = " ".join(context.args) + " full movie" # <-- THIS MAKES IT SEARCH FULL MOVIE
    msg = await update.message.reply_text(f"🎬 Searching for: `{query}`...")

    try:
        info = await search_youtube(query)

        title = info.get("title", "Unknown Movie")
        uploader = info.get("uploader", "Unknown Channel")
        duration = info.get("duration", 0)
        views = info.get("view_count", 0)
        video_id = info.get("id")
        thumbnail = info.get("thumbnail")
        url = f"https://youtube.com/watch?v={video_id}"

        caption = f"""
🎬 **{title}**
👤 **{uploader}**

━━━━━━━━━━━━━━

🎞 Type: Full Movie

⏱ Duration: {format_duration(duration)}

👀 Views: {f"{views:,}" if views else "Unknown"}

👤 Requested by:
{update.effective_user.first_name}

⚠️ Watch on YouTube

━━━━━━━━━━━━━━

Powered By: MUFASER-X
        """

        keyboard = [[InlineKeyboardButton("▶️ Watch Full Movie", url=url)]] # <-- BUTTON
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Send thumbnail + caption + button. No download = no block
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=thumbnail,
            caption=caption,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        await msg.delete()

    except Exception as e:
        await msg.edit_text(f"❌ Movie not found. Try different words.\nError: {str(e)[:200]}")