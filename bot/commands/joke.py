from google import genai
import os
from telegram import Update
from telegram.ext import ContextTypes

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

async def joke_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text(
        "🤣 Creating a fresh joke... Please wait."
    )

    try:
        prompt = (
            "Create ONE original, funny, family-friendly joke. "
            "Do not copy famous jokes. "
            "Keep it short (under 80 words). "
            "Add a few emojis."
        )

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        joke = response.text.strip()

        await msg.edit_text(
            f"🤣 **MUFASER-X AI Joke**\n\n{joke}",
            parse_mode="Markdown"
        )

    except Exception as e:
        await msg.edit_text(
            f"❌ Failed to generate a joke.\n\n{str(e)}"
        )