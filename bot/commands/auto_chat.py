import asyncio
import requests

from telegram import Update
from telegram.constants import ChatAction, ChatType
from telegram.ext import ContextTypes

from voice import text_to_voice

API_URL = "https://prexzyapis.com/ai/aichat"

SYSTEM_PROMPT = """
You are MUFASER-X, a friendly Telegram AI assistant.

You were created by ROMA-TECH from Uganda.

IMPORTANT:

Only mention your name MUFASER-X if the user asks your name.

Only mention ROMA-TECH if the user asks who created you.

Do not introduce yourself randomly.

Do not say "My name is MUFASER-X" in normal conversations.

Example:
User: wow
Good reply: "That's impressive! 😄"

Bad reply:
"My name is MUFASER-X."

You can:

Chat naturally

Answer questions

Tell jokes

Write stories

Translate languages

Help users

Rules:

Never start replies with "MUFASER-X:"

Never start replies with "Assistant:"

Reply like a normal helpful person.

Use emojis naturally.
"""

chat_memory = {}
MAX_HISTORY = 50

async def typing_indicator(context, chat_id):
    """Keep sending typing every 3 seconds"""
    try:
        while True:
            await context.bot.send_chat_action(
                chat_id=chat_id,
                action=ChatAction.TYPING
            )
            await asyncio.sleep(3)
    except asyncio.CancelledError:
        pass

async def auto_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    if update.effective_user.is_bot:
        return

    if not update.message.text:
        return

    message = update.message.text.strip()
    chat_id = update.effective_chat.id
    chat_type = update.effective_chat.type
    bot_username = context.bot.username.lower()
    username = update.effective_user.first_name or "User"

    # NEW LOGIC: Only reply in groups if tagged/mentioned
    if chat_type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        # Check if bot is mentioned with @username or replied to
        is_mentioned = f"@{bot_username}" in message.lower()
        is_reply = update.message.reply_to_message and update.message.reply_to_message.from_user.id == context.bot.id
        
        if not is_mentioned and not is_reply:
            return  # ignore normal group messages
        
        # Remove the @mention from the message before sending to AI
        message = message.replace(f"@{bot_username}", "").strip()
        
        # If message becomes empty after removing mention, ignore
        if not message:
            return

    # In DMs and channels: reply to everything
    if message.startswith("/"):
        return

    if chat_id not in chat_memory:
        chat_memory[chat_id] = []

    chat_memory[chat_id].append(f"{username}: {message}")
    chat_memory[chat_id] = chat_memory[chat_id][-MAX_HISTORY:]

    history = "\n".join(chat_memory[chat_id])

    prompt = f"""
{SYSTEM_PROMPT}

Conversation:
{history}

Reply to the last user message naturally.
"""

    # SEND TYPING ONCE IMMEDIATELY SO DOTS SHOW
    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    
    typing_task = asyncio.create_task(typing_indicator(context, chat_id))

    try:
        response = requests.get(
            API_URL,
            params={"prompt": prompt},
            timeout=60
        )

        data = response.json()

        if data.get("status"):
            reply = data.get("response", "I don't know.").strip()

            # Remove unwanted prefixes
            for prefix in ["MUFASER-X:", "Assistant:", "AI:", "Bot:"]:
                if reply.startswith(prefix):
                    reply = reply[len(prefix):].strip()

            chat_memory[chat_id].append(f"MUFASER-X: {reply}")

            # Check if user wants voice
            voice_words = [
                "send voice", "voice note", "send a voice", 
                "talk to me", "speak", "say it", "read it"
            ]

            want_voice = any(word in message.lower() for word in voice_words)

            if want_voice:
                voice_reply = text_to_voice(reply)
                await context.bot.send_voice(chat_id=chat_id, voice=voice_reply)
            else:
                await update.message.reply_text(reply)

        else:
            await update.message.reply_text("❌ AI service error.")

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

    finally:
        typing_task.cancel()