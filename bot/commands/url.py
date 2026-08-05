import os
import cloudinary
import cloudinary.uploader

from telegram import Update
from telegram.ext import ContextTypes


cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)


async def url_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    reply = update.message.reply_to_message

    if not reply:
        await update.message.reply_text("❌ Reply to an image, video, audio or file with /url")
        return

    msg = await update.message.reply_text("⏳ Uploading...")
    file_path = None

    try:
        tmp_dir = "/tmp"
        os.makedirs(tmp_dir, exist_ok=True)

        if reply.photo:
            file = await reply.photo[-1].get_file()
            file_path = f"{tmp_dir}/upload_{file.file_id}.jpg"
            await file.download_to_drive(file_path)

        elif reply.video:
            file = await reply.video.get_file()
            file_path = f"{tmp_dir}/upload_{file.file_id}.mp4"
            await file.download_to_drive(file_path)

        elif reply.audio:
            file = await reply.audio.get_file()
            file_path = f"{tmp_dir}/upload_{file.file_id}.mp3"
            await file.download_to_drive(file_path)
            
        elif reply.voice:
            file = await reply.voice.get_file()
            file_path = f"{tmp_dir}/upload_{file.file_id}.ogg"
            await file.download_to_drive(file_path)

        elif reply.document:
            file = await reply.document.get_file()
            file_path = f"{tmp_dir}/{reply.document.file_name or file.file_id}"
            await file.download_to_drive(file_path)

        else:
            await msg.edit_text("❌ Unsupported file type.")
            return

        # Upload to Cloudinary
        result = cloudinary.uploader.upload(file_path, resource_type="auto")
        url = result.get("secure_url")

        await msg.edit_text(
            f"✅ Upload complete\n🔗 Link:\n{url}\n\n Powered: By\n MUFASER-X"
        )

    except Exception as e:
        await msg.edit_text(f"❌ Upload error:\n{e}")

    finally:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)