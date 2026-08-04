import requests
from telegram import Update
from telegram.ext import ContextTypes

async def fact_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("🔎 Fetching a random fact...")

    try:
        response = requests.get(
            "https://uselessfacts.jsph.pl/api/v2/facts/random",
            timeout=10
        )
        response.raise_for_status()

        data = response.json()
        fact = data["text"]

        await msg.edit_text(
            f"""💡 Random Fact

━━━━━━━━━━━━━━

{fact}

━━━━━━━━━━━━━━

Powered By: MUFASER-X """
        )

    except Exception as e:
        await msg.edit_text(f"❌ Failed to fetch fact.\n\n{e}")