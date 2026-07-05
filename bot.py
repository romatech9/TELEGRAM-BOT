import asyncio
import logging
import os
import time
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from io import BytesIO

from google import genai
from google.genai import types
from dotenv import load_dotenv
from gtts import gTTS
from telegram import Update
from telegram.constants import ChatAction, ChatMemberStatus
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# Load.env locally. On Render we use Environment Variables
load_dotenv()

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"] # Still needed for the API
MUFASER_MODEL = "gemini-2.5-flash" # The actual model we use
MAX_HISTORY = 20
GEMINI_TIMEOUT = 60.0

KAMPALA_TZ = timezone(timedelta(hours=3)) # East Africa Time (UTC+3)

SYSTEM_INSTRUCTION = (
    "You are MUFASER-X, a helpful, friendly, and concise assistant inside a Telegram chat. "
    "Keep responses clear and to the point. Use plain text. Be accurate and helpful."
)

HELP_TEXT = (
    "🤖 *MUFASER-X Commands*\n\n"
    "/start – welcome message\n"
    "/help – show this list\n"
    "/ping – check latency and Kampala time\n"
    "/ban – ban a user (reply to their message; admins only)\n"
    "/ai \\<question\\> – ask MUFASER-X a question \\(text \\+ voice note\\)\n"
    "/voice \\<text\\> – convert text to a voice note\n"
    "/reset – clear your MUFASER-X conversation history\n"
    "💬 You can also just send any text message and I'll reply with MUFASER-X\\."
)

# ---------------------------------------------------------------------------
# MUFASER-X client - initialised in main()
# ---------------------------------------------------------------------------
client: genai.Client | None = None

# In-memory conversation history: {user_id: [Content,...]}
conversation_history: dict[int, list[types.Content]] = defaultdict(list)

# ---------------------------------------------------------------------------
# AI helpers
# ---------------------------------------------------------------------------
def _trim_history(history: list[types.Content]) -> list[types.Content]:
    if len(history) <= MAX_HISTORY:
        return history
    trimmed = history[-MAX_HISTORY:]
    while trimmed and trimmed[0].role!= "user":
        trimmed = trimmed[1:]
    return trimmed

async def _ask_mufaser(user_id: int, user_text: str) -> str:
    if client is None:
        raise RuntimeError("MUFASER-X API KEY not set")

    history = list(conversation_history[user_id])
    new_user_turn = types.Content(role="user", parts=[types.Part(text=user_text)])

    if not history:
        system_turn = types.Content(
            role="user", parts=[types.Part(text=f"[System] {SYSTEM_INSTRUCTION}")]
        )
        model_ack = types.Content(
            role="model", parts=[types.Part(text="Understood. I am MUFASER-X and I'll follow those instructions.")]
        )
        contents = [system_turn, model_ack, new_user_turn]
    else:
        contents = history + [new_user_turn]

    response = await asyncio.wait_for(
        client.aio.models.generate_content(
            model=MUFASER_MODEL,
            contents=contents,
            config=types.GenerateContentConfig(max_output_tokens=8192),
        ),
        timeout=GEMINI_TIMEOUT,
    )

    reply_text = response.text or "(no response)"
    new_model_turn = types.Content(role="model", parts=[types.Part(text=reply_text)])
    conversation_history[user_id] = _trim_history(history + [new_user_turn, new_model_turn])
    return reply_text

async def _reply_with_ai(update: Update, text: str, send_voice: bool = False) -> None:
    user_id = update.effective_user.id
    await update.message.chat.send_action(ChatAction.TYPING)

    try:
        reply = await _ask_mufaser(user_id, text)
        await update.message.reply_text(reply)
    except RuntimeError as exc:
        if "API KEY not set" in str(exc):
            logger.error("MUFASER-X API KEY missing — cannot serve user %d", user_id)
            await update.message.reply_text("⚠️ MUFASER-X API Key missing in Render Environment.")
        else:
            logger.error("MUFASER-X runtime error for user %d: %s", user_id, exc)
            await update.message.reply_text("⚠️ MUFASER-X is down. Try again in 1 minute.")
        return
    except Exception as exc:
        logger.error("MUFASER-X error for user %d — %s: %s", user_id, type(exc).__name__, exc)
        await update.message.reply_text("⚠️ MUFASER-X is down. Try again in 1 minute.")
        return

    if send_voice:
        await _send_voice_note(update, reply)

async def _send_voice_note(update: Update, text: str) -> None:
    await update.message.chat.send_action(ChatAction.RECORD_VOICE)
    try:
        tts = gTTS(text=text, lang='en', slow=False)
        audio_file = BytesIO()
        tts.write_to_fp(audio_file)
        audio_file.seek(0)
        await update.message.reply_voice(ogg_buf=audio_file)
    except Exception as exc:
        logger.exception("Voice generation error: %s", exc)
        await update.message.reply_text("⚠️ Could not generate voice note.")

# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    name = user.first_name if user else "there"
    await update.message.reply_text(
        f"Yo {name}! 🔥 I'm MUFASER-X powered by AI.\n\n"
        "Send me any message and I'll reply. Use /help to see all commands."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(HELP_TEXT, parse_mode="MarkdownV2")

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg_time_utc = update.message.date
    now_utc = datetime.now(timezone.utc)
    latency_ms = max(0, int((now_utc - msg_time_utc).total_seconds() * 1000))
    kampala_now = now_utc.astimezone(KAMPALA_TZ)
    time_str = kampala_now.strftime("%I:%M:%S %p")
    date_str = kampala_now.strftime("%A, %d %B %Y")
    await update.message.reply_text(
        f"🏓 Pong!\n⚡ Latency: {latency_ms} ms\n🕐 Kampala time: {time_str}\n📅 {date_str}"
    )

ADMIN_STATUSES = {ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER}
async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    from telegram.error import BadRequest, Forbidden
    chat = update.effective_chat
    sender = update.effective_user
    if chat.type not in ("group", "supergroup"):
        await update.message.reply_text("❌ /ban only works in groups."); return
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Reply to the message of the user you want to ban."); return
    sender_member = await context.bot.get_chat_member(chat.id, sender.id)
    if sender_member.status not in ADMIN_STATUSES:
        await update.message.reply_text("🚫 Only admins can use /ban."); return
    me = await context.bot.get_me()
    bot_member = await context.bot.get_chat_member(chat.id, me.id)
    if bot_member.status not in ADMIN_STATUSES or not getattr(bot_member, "can_restrict_members", False):
        await update.message.reply_text("⚠️ I need to be an admin with 'Ban users' permission."); return
    target_user = update.message.reply_to_message.from_user
    if target_user.id == me.id: await update.message.reply_text("😅 I can't ban myself."); return
    target_member = await context.bot.get_chat_member(chat.id, target_user.id)
    if target_member.status in ADMIN_STATUSES: await update.message.reply_text("❌ Cannot ban an admin."); return
    try:
        await context.bot.ban_chat_member(chat.id, target_user.id)
        await update.message.reply_text(f"🚫 {target_user.full_name} has been banned.")
    except Forbidden: await update.message.reply_text("❌ I don't have permission to ban that user.")
    except BadRequest as exc: await update.message.reply_text(f"❌ Could not ban user: {exc.message}")

async def ai_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = " ".join(context.args).strip() if context.args else ""
    if not text: await update.message.reply_text("Usage: /ai <your question>"); return
    await _reply_with_ai(update, text, send_voice=True)

async def voice_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = " ".join(context.args).strip() if context.args else ""
    if not text: await update.message.reply_text("Usage: /voice <text>"); return
    await update.message.chat.send_action(ChatAction.TYPING)
    await _send_voice_note(update, text)

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    conversation_history[user_id] = []
    await update.message.reply_text("🔄 MUFASER-X memory cleared. Starting fresh!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_text = (update.message.text or "").strip()
    if not user_text: return
    await _reply_with_ai(update, user_text)

async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    group_name = update.effective_chat.title or "the group"
    for member in update.message.new_chat_members:
        if member.is_bot: continue
        username = f"@{member.username}" if member.username else member.first_name
        await update.message.reply_text(f"Hello {username}! Welcome to {group_name} 🎉\nI'm MUFASER-X. Ask me anything!")

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    global client
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        print(f"[STARTUP] MUFASER-X API KEY loaded — first 8 chars: {api_key[:8]}...", flush=True)
        client = genai.Client(api_key=api_key, http_options={"api_version": "v1"})
        logger.info("MUFASER-X client initialised (model: %s)", MUFASER_MODEL)
    else:
        client = None
        logger.error("MUFASER-X API KEY missing — AI replies disabled.")

    logger.info("Starting MUFASER-X bot")
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("ban", ban))
    app.add_handler(CommandHandler("ai", ai_command))
    app.add_handler(CommandHandler("voice", voice_command))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("MUFASER-X is polling for updates...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()