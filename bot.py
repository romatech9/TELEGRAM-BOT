import os
import asyncio
import logging
from io import BytesIO
from dotenv import load_dotenv
import google.generativeai as genai
from gtts import gTTS
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.constants import ChatAction, ChatMemberStatus
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

load_dotenv()
app = Flask('')

# Keep alive server for UptimeRobot
@app.route('/')
def home(): return "MUFASER-X is alive"
def run(): app.run(host='0.0.0.0', port=8080)
def start_server(): Thread(target=run).start()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MUFASER_MODEL = 'gemini-2.5-flash'

logging.basicConfig(level=logging.INFO)
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(MUFASER_MODEL)

async def ai_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = " ".join(context.args)
    if not user_msg: await update.message.reply_text("Use: /ai your question"); return
    await update.message.reply_chat_action(action="typing")
    try:
        response = await model.generate_content_async(user_msg)
        text_reply = response.text
        await update.message.reply_text(text_reply)
        tts = gTTS(text=text_reply, lang='en', slow=False)
        audio_file = BytesIO()
        tts.write_to_fp(audio_file)
        audio_file.seek(0)
        await update.message.reply_voice(voice=audio_file)
    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text("⚠️ MUFASER-X is down. Try again later.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Yo, MUFASER-X is live 🔥 Send /ai your question")

def main():
    start_server()
    app_tg = Application.builder().token(TELEGRAM_TOKEN).build()
    app_tg.add_handler(CommandHandler("start", start))
    app_tg.add_handler(CommandHandler("ai", ai_handler))
    print("MUFASER-X is running...")
    app_tg.run_polling()

if __name__ == "__main__":
    main()