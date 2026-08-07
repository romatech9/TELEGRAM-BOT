import aiohttp
import logging
import asyncio
from telegram import Update
from telegram.ext import ContextTypes

from voice import text_to_voice  # <-- YOUR voice.py

API_URL = "https://prexzyapis.com/ai/aiwriter-chat?prompt=Hy&model=gpt-4o-mini"

# ADDED: This stores chat history
conversation_history = {}

async def ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id # ADDED
    user_message = " ".join(context.args)
    
    if not user_message:
        await update.message.reply_text("Usage: /ai hello")
        return
    
    # ADDED: Save user message to memory
    if user_id not in conversation_history:
        conversation_history[user_id] = []
    conversation_history[user_id].append(f"You: {user_message}")
    
    await update.message.reply_text("Thinking... 🤖")
    
    try:
        logging.info(f"TESTING AI API WITH: {user_message}")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL, params={"prompt": user_message}, timeout=60) as resp:
                
                logging.info(f"Status Code: {resp.status}")
                raw_text = await resp.text()
                logging.info(f"RAW API Response: {raw_text}")
                
                if resp.status != 200:
                    await update.message.reply_text(f"API Error: Status {resp.status}")
                    return
                
                data = await resp.json()
                
                if data.get("status") is True:
                    reply = data.get("response")
                    
                    # ADDED: Save AI reply to memory
                    conversation_history[user_id].append(f"AI: {reply}")
                    
                    # 1. SEND TEXT FIRST
                    await update.message.reply_text(reply)
                    
                    # 2. SEND YOUR MALE VOICE NOTE RIGHT AFTER
                    try:
                        # run your sync function in thread so bot doesn't freeze
                        voice_buf = await asyncio.to_thread(text_to_voice, reply)
                        await context.bot.send_voice(
                            chat_id=update.effective_chat.id,
                            voice=voice_buf,
                            caption=""
                        )
                    except Exception as ve:
                        logging.error(f"VOICE FAILED: {ve}")
                        await update.message.reply_text("⚠️ Voice failed but here is text")
                        
                else:
                    await update.message.reply_text(f"API Error: {data}")
                    
    except Exception as e:
        logging.error(f"AI API FAILED: {e}")
        await update.message.reply_text(f"API Failed: {e}")