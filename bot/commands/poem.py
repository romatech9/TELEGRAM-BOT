from google import genai
import os
from telegram import Update
from telegram.ext import ContextTypes

# Create Gemini client once
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Gemini model
GEMINI_MODEL = "gemini-2.5-flash"


async def poem_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topic = " ".join(context.args) if context.args else "life"

    msg = await update.message.reply_text(
        f"🎭 Writing a poem about *{topic}*...",
        parse_mode="Markdown"
    )

    try:
        prompt = (
            f"Write a beautiful, simple 4-line poem about '{topic}'. "
            f"Make it emotional and easy to understand."
        )

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
        )

        poem = response.text.strip()

        await msg.delete()

        await update.message.reply_text(
            f"🎭 *Poem: {topic.title()}*\n\n{poem}",
            parse_mode="Markdown"
        )

    except Exception as e:
        await msg.edit_text(f"❌ Error:\n{e}")