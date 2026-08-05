from google import genai
import os
from telegram import Update
from telegram.ext import ContextTypes

# Create Gemini client once
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Gemini model
GEMINI_MODEL = "gemini-2.5-flash"


async def story_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topic = " ".join(context.args) if context.args else "an unexpected adventure"

    msg = await update.message.reply_text(
        f"📖 Writing a story about *{topic}*...",
        parse_mode="Markdown"
    )

    try:
        prompt = (
            f"Write a fun, engaging story about '{topic}'. "
            f"Use exactly 3 short paragraphs with a clear ending."
        )

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
        )

        story = response.text.strip()

        await msg.delete()

        await update.message.reply_text(
            f"📖 *{topic.title()}*\n\n{story}",
            parse_mode="Markdown"
        )

    except Exception as e:
        await msg.edit_text(f"❌ Error:\n{e}")