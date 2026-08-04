import os
import replicate
import requests

from telegram import Update
from telegram.ext import ContextTypes


async def beach_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message.reply_to_message:
        await update.message.reply_text(
            "❌ Reply to a photo with /beach"
        )
        return

    if not update.message.reply_to_message.photo:
        await update.message.reply_text(
            "❌ The replied message must contain a photo."
        )
        return

    msg = await update.message.reply_text(
        "🏖️ Creating your beach version...\n⏳ Please wait..."
    )

    try:
        photo = update.message.reply_to_message.photo[-1]

        file = await context.bot.get_file(photo.file_id)

        image_path = "beach_input.jpg"

        await file.download_to_drive(image_path)


        with open(image_path, "rb") as image_file:

            upload = replicate.files.create(
                file=image_file,
                purpose="input"
            )

        image_url = upload.urls["get"]


        output = replicate.run(
            "black-forest-labs/flux-kontext-pro",
            input={
                "prompt": (
                    "Change the background to a beautiful tropical beach. "
                    "Keep the person exactly the same with the same face, "
                    "pose, clothes, and body position. "
                    "Add ocean waves, palm trees, golden sunlight, "
                    "realistic cinematic photography."
                ),
                "input_image": image_url,
                "aspect_ratio": "match_input_image",
                "output_format": "jpg",
                "safety_tolerance": 2
            }
        )


        result = requests.get(output.url)

        output_file = "beach_result.jpg"

        with open(output_file, "wb") as f:
            f.write(result.content)


        await msg.delete()


        await update.message.reply_photo(
            photo=open(output_file, "rb"),
            caption=f"""
🏖️ Beach Transformation Complete!

👤 Requested by:
{update.effective_user.first_name}

━━━━━━━━━━━━━━

🌊 Enjoy your virtual beach moment!

Powered By: MUFASER-X 
"""
        )


        os.remove(image_path)
        os.remove(output_file)


    except Exception as e:
        await msg.edit_text(
            f"❌ Beach generation failed:\n{e}"
        )