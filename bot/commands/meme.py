import requests
from telegram import Update
from telegram.ext import ContextTypes


async def meme_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("😂 Fetching a meme...")

    try:
        response = requests.get(
            "https://meme-api.com/gimme",
            timeout=20
        )

        data = response.json()

        if "url" not in data:
            await msg.edit_text("❌ Couldn't fetch a meme.")
            return

        await msg.delete()

        await update.message.reply_photo(
            photo=data["url"],
            caption=f"😂 {data.get('title', 'Random Meme')}"
        )

    except Exception as e:
        await msg.edit_text(f"❌ Error:\n{e}")