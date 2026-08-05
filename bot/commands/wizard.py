import os
import replicate
import requests

from telegram import Update
from telegram.ext import ContextTypes


async def wizard_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message.reply_to_message:
        await update.message.reply_text(
            "❌ Reply to a photo with /wizard"
        )
        return

    if not update.message.reply_to_message.photo:
        await update.message.reply_text(
            "❌ The replied message must contain a photo."
        )
        return

    msg = await update.message.reply_text(
        "🧙 Creating your wizard version...\n⏳ Please wait..."
    )

    try:
        photo = update.message.reply_to_message.photo[-1]

        file = await context.bot.get_file(photo.file_id)

        image_path = "wizard_input.jpg"

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
                    "Transform this person into a powerful fantasy wizard. "
                    "Keep the same face and identity. "
                    "Add a magical robe, wizard staff, glowing magic effects, "
                    "ancient fantasy background, cinematic lighting, "
                    "high quality realistic fantasy art."
                ),
                "input_image": image_url,
                "aspect_ratio": "match_input_image",
                "output_format": "jpg",
                "safety_tolerance": 2
            }
        )


        result = requests.get(output.url)

        output_file = "wizard_result.jpg"

        with open(output_file, "wb") as f:
            f.write(result.content)


        await msg.delete()


        await update.message.reply_photo(
            photo=open(output_file, "rb"),
            caption=f"""
🧙 Wizard Transformation Complete!

👤 Requested by:
{update.effective_user.first_name}

━━━━━━━━━━━━━━

✨ Enter the world of magic!

Powered By: MUFASER-X 
"""
        )


        os.remove(image_path)
        os.remove(output_file)


    except Exception as e:
        await msg.edit_text(
            f"❌ Wizard generation failed:\n{e}"
        )