from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import BadRequest
import io
from PIL import Image

async def sticker_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Usage: Reply to a photo with /sticker
    if not update.message.reply_to_message or not update.message.reply_to_message.photo:
        await update.message.reply_text("Reply to a photo with /sticker and I'll convert it")
        return
    
    # Download the photo
    photo_file = await update.message.reply_to_message.photo[-1].get_file()
    photo_bytes = await photo_file.download_as_bytearray()
    
    # Resize to 512x512 for telegram sticker
    img = Image.open(io.BytesIO(photo_bytes))
    img.thumbnail((512, 512))
    
    buf = io.BytesIO()
    img.save(buf, 'PNG')
    buf.seek(0)
    
    try:
        await update.message.reply_sticker(sticker=buf)
    except BadRequest as e:
        await update.message.reply_text(f"Failed to send sticker: {e}")