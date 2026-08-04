import os
import asyncio
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

def format_duration(seconds):
    if not seconds:
        return "0:00"
    seconds = int(seconds)
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    if h:
        return f"{h}:{m:02}:{s:02}"
    return f"{m}:{s:02}"

async def search_youtube(query):
    loop = asyncio.get_event_loop()
    options = {
        "default_search": "ytsearch1",
        "noplaylist": True,
        "quiet": True,
        "retries": 3,
        "extractor_args": {"youtube": {"player_client": ["android", "web"]}},
        "http_headers": {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
    }
    with yt_dlp.YoutubeDL(options) as ydl:
        info = await loop.run_in_executor(None, lambda: ydl.extract_info(query, download=False))
        if "entries" in info:
            info = info["entries"][0]
        return info

async def song_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("🎵 Usage:\n/song song name")
        return

    query = " ".join(context.args)
    msg = await update.message.reply_text(f"🔎 Searching: `{query}`...")

    try:
        info = await search_youtube(query)

        title = info.get("title", "Unknown")
        artist = info.get("uploader", "Unknown")
        duration = info.get("duration", 0)
        views = info.get("view_count", 0)
        likes = info.get("like_count", 0)
        video_id = info.get("id")
        thumbnail = info.get("thumbnail")
        url = f"https://youtube.com/watch?v={video_id}"

        caption = f"""
🎵 **{title}**
👤 Artist: {artist}

━━━━━━━━━━━━━━

🎧 Quality: Stream on YouTube

⏱ Duration: {format_duration(duration)}

👀 Views: {f"{views:,}" if views else "Unknown"}

❤️ Likes: {f"{likes:,}" if likes else "Unknown"}

📥 Get MP3: Forward this to @YTMp3Bot or @SongDownloaderRobot

👤 Requested by:
{update.effective_user.first_name}

━━━━━━━━━━━━━━

 Powered By: MUFASER-X
"""

        buttons = [[InlineKeyboardButton("▶️ Listen on YouTube", url=url)]]
        markup = InlineKeyboardMarkup(buttons)

        # Send thumbnail + info. No download = no block
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=thumbnail,
            caption=caption,
            parse_mode="Markdown",
            reply_markup=markup
        )
        await msg.delete()

    except Exception as e:
        await msg.edit_text(f"❌ Search failed\nYouTube blocked it. Try again in 5 sec.\nError: {str(e)[:200]}")