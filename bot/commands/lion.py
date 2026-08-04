import os
import tempfile
import shutil
import requests
import replicate

from telegram import Update
from telegram.ext import ContextTypes


async def lion_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message.reply_to_message:
        await update.message.reply_text(
            "❌ Reply to a photo with /lion"
        )
        return

    if not update.message.reply_to_message.photo:
        await update.message.reply_text(
            "❌ Please reply to a photo."
        )
        return

    temp_dir = tempfile.mkdtemp()

    try:
        msg = await update.message.reply_text(
            "🦁 Creating your Lion King version...\n"
            "⏳ Please wait..."
        )

        photo = update.message.reply_to_message.photo[-1]

        telegram_file = await context.bot.get_file(photo.file_id)

        input_image = os.path.join(temp_dir, "input.jpg")

        await telegram_file.download_to_drive(input_image)

        with open(input_image, "rb") as image:

            upload = replicate.files.create(
                file=image,
                purpose="input"
            )

        output = replicate.run(
            "black-forest-labs/flux-kontext-pro",
            input={
                "prompt": (
                    "Transform this person into a majestic Lion King warrior. "
                    "Keep the same face and identity. "
                    "Give them golden lion armor, a royal lion crown, "
                    "a powerful lion beside them, glowing golden eyes, "
                    "cinematic lighting, epic African sunset, "
                    "ultra realistic fantasy artwork."
                ),
                "input_image": upload.urls["get"],
                "aspect_ratio": "match_input_image",
                "output_format": "jpg",
                "safety_tolerance": 2
            }
        )

        result = requests.get(output.url)

        output_file = os.path.join(temp_dir, "lion.jpg")

        with open(output_file, "wb") as f:
            f.write(result.content)

        await msg.delete()

        with open(output_file, "rb") as photo:
            await update.message.reply_photo(
                photo=photo,
                caption=f"""
🦁 Lion Transformation Complete!

👤 Requested by:
{update.effective_user.first_name}

━━━━━━━━━━━━━━

👑 Become the King of the Jungle!

Powered By: MUFASER-X 
"""
            )

    except Exception as e:
        await update.message.reply_text(
            f"❌ Error:\n{e}"
        )

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)