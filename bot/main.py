import asyncio # must be first

# ====== FLASK KEEP ALIVE ======
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "MUFASER-X Bot is running"

def keep_alive():
    app.run(host='0.0.0.0', port=10000)

Thread(target=keep_alive, daemon=True).start()
# ====== END FLASK CODE ======

from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from telegram import Update
import logging
import os
import time
from collections import defaultdict
from datetime import timedelta, timezone

# IMPORT ALL COMMANDS FROM FILES - NO AI, NO BOT_ADDED
from commands.start import start
from commands.ping import ping
from commands.reset import reset
import commands.reset
from commands.shazam import shazam
from zombies import zombies, restore_zombie_jobs
from commands.auto_chat import auto_chat
from ytdlp_updater import check_ytdlp_update
from commands.antilinkcheck import anti_link_checker
from commands.antilink import antilink 
from commands.chatinfo import chatinfo_command
from commands.movie import movie_command
from commands.lion import lion_command
from commands.beach import beach_command
from commands.wizard import wizard_command
from commands.fact import fact_command
from commands.poll import poll_command
from commands.setdescription import setdescription_command
from commands.pin import pin_command
from commands.unpin import unpin_command
from commands.url import url_command
from commands.joke import joke_command
from commands.video import video_command 
from commands.song import song_command
from commands.image import image_command, wallpaper_command, avatar_command, logo_command
from commands.style import anime_command, remix_command
from commands.meme import meme_command
from commands.clean import del_command, purge_command
from commands.warn import warn_command, warns_command, delwarn_command, resetwarns_command
from commands.lock import lock, unlock, locks
from commands.level import handle_xp, rank
from commands.link import grouplink
from commands.admin import promote, demote
from commands.sticker import sticker_command
from commands.unmute import unmute_command
from commands.mute import mute_command
from commands.kick import kick_command
from commands.unban import unban_command
from commands.ban import ban_command
from commands.lyrics import lyrics_command
from commands.story import story_command
from commands.poem import poem_command
from commands.currency import currency_command
from commands.weather import weather_command
from commands.quiz import quiz_command, button_handler as quiz_button_handler
from commands.help import help_command, button_handler as help_button_handler, all_command
from commands.summarize import summarize_command
from commands.math import math_command
from commands.translate import translate_command
from commands.status import status_command
from commands.id import id_command
from commands.explain import explain_command
from commands.welcome import welcome_new_member, welcome_toggle

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
KAMPALA_TZ = timezone(timedelta(hours=3))
start_time = time.time()

group_settings = defaultdict(lambda: {"welcome": True, "antilink": False})
warns = defaultdict(dict)
conversation_history = defaultdict(list)

async def is_admin(update, context):
    chat = await context.bot.get_chat_administrators(update.effective_chat.id)
    return any(admin.user.id == update.effective_user.id for admin in chat)

def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    commands.reset.conversation_history = conversation_history 
    
    application.bot_data['group_settings'] = group_settings
    application.bot_data['warns'] = warns
    application.bot_data['conversation_history'] = conversation_history
    application.bot_data['client'] = None
    application.bot_data['is_admin'] = is_admin
    application.bot_data['start_time'] = start_time
    application.bot_data['KAMPALA_TZ'] = KAMPALA_TZ
    
    # ALL COMMAND HANDLERS
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("zombies", zombies))
    application.add_handler(CommandHandler("poll", poll_command))
    application.add_handler(CommandHandler("reset", reset))
    application.add_handler(CommandHandler("ping", ping))
    application.add_handler(CommandHandler("fact", fact_command))
    application.add_handler(CommandHandler("chatinfo",chatinfo_command))
    application.add_handler(CommandHandler("sticker", sticker_command))
    application.add_handler(CommandHandler("mute", mute_command))
    application.add_handler(CommandHandler("kick", kick_command))
    application.add_handler(CommandHandler("antilink",antilink))
    application.add_handler(CommandHandler("unban", unban_command))
    application.add_handler(CommandHandler("ban", ban_command))
    application.add_handler(CommandHandler("unmute", unmute_command))
    application.add_handler(CommandHandler("lyrics", lyrics_command))
    application.add_handler(CommandHandler("id", id_command))
    application.add_handler(CommandHandler("movie",movie_command))
    application.add_handler(CommandHandler("translate", translate_command))
    application.add_handler(CommandHandler("joke", joke_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("currency", currency_command))
    application.add_handler(CommandHandler("math", math_command))
    application.add_handler(CommandHandler("link", grouplink))
    application.add_handler(CommandHandler("video", video_command)) 
    application.add_handler(CommandHandler("weather", weather_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("promote", promote))
    application.add_handler(CommandHandler("play", song_command))
    application.add_handler(CommandHandler("demote", demote))
    application.add_handler(CommandHandler("del", del_command))
    application.add_handler(CommandHandler("purge", purge_command))
    application.add_handler(CommandHandler("story", story_command))
    application.add_handler(CommandHandler("lock", lock))
    application.add_handler(CommandHandler("shazam", shazam))
    application.add_handler(CommandHandler("warn", warn_command))
    application.add_handler(CommandHandler("song", song_command))
    application.add_handler(CommandHandler("warns", warns_command))
    application.add_handler(CommandHandler("delwarn", delwarn_command))
    application.add_handler(CommandHandler("resetwarns", resetwarns_command))
    application.add_handler(CommandHandler("unlock", unlock))
    application.add_handler(CommandHandler("locks", locks))
    application.add_handler(CommandHandler("quiz", quiz_command))
    application.add_handler(CommandHandler("rank", rank))
    application.add_handler(CommandHandler("setdescription", setdescription_command))
    application.add_handler(CommandHandler("pin", pin_command))
    application.add_handler(CommandHandler("lion", lion_command))
    application.add_handler(CommandHandler("unpin", unpin_command))
    application.add_handler(CommandHandler("poem", poem_command))
    application.add_handler(CommandHandler("image", image_command))
    application.add_handler(CommandHandler("wallpaper", wallpaper_command))
    application.add_handler(CommandHandler("wizard", wizard_command))
    application.add_handler(CommandHandler("avatar", avatar_command))
    application.add_handler(CommandHandler("url",url_command))
    application.add_handler(CommandHandler("beach", beach_command))
    application.add_handler(CommandHandler("logo", logo_command))
    application.add_handler(CommandHandler("anime", anime_command))
    application.add_handler(CommandHandler("remix", remix_command))
    application.add_handler(CommandHandler("meme", meme_command))
    application.add_handler(CommandHandler("explain", explain_command))
    application.add_handler(CommandHandler("summarize",summarize_command))
    application.add_handler(CommandHandler("welcome", welcome_toggle))
    
    # REMOVED: ChatMemberHandler for bot_added
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, anti_link_checker), group=0)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_xp), group=1)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, auto_chat), group=2)
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))
    application.add_handler(CallbackQueryHandler(quiz_button_handler, pattern="^quiz_"))
    application.add_handler(CallbackQueryHandler(help_button_handler))

    application.post_init = combined_post_init
    logger.info("MUFASER-X Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True, poll_interval=1.0)

async def post_init(app):
    asyncio.create_task(check_ytdlp_update(app.bot))

async def combined_post_init(application):
    await restore_zombie_jobs(application)
    await post_init(application)

if __name__ == "__main__":
    main()