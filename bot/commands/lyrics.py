from google import genai
import os
from telegram import Update
from telegram.ext import ContextTypes

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

async def lyrics_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topic = " ".join(context.args) if context.args else "love"

    msg = await update.message.reply_text(
        f"🎵 Writing original lyrics about '{topic}'..."
    )

    try:
        prompt = (
            f"Write original song lyrics about '{topic}'. "
            "Include 1 verse and 1 chorus. "
            "Keep it short, catchy, and clean."
        )

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        lyrics = response.text if response.text else "No lyrics were generated."

        await msg.edit_text(
            f"🎤 Original Lyrics: {topic.title()}\n\n{lyrics}"
        )

    except Exception as e:
        await msg.edit_text(f"❌ Error:\n{e}")