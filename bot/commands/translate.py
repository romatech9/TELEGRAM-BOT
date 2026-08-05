import os
from google import genai
from google.genai import types
from telegram import Update
from telegram.ext import ContextTypes

# NEW SDK: create client once
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

async def translate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Case 1: Reply to a message + /translate Spanish
    if update.message.reply_to_message and update.message.reply_to_message.text:
        text_to_translate = update.message.reply_to_message.text
        if not context.args:
            await update.message.reply_text("⚡ *Usage:* Reply + `/translate Spanish`", parse_mode='Markdown')
            return
        target_lang = " ".join(context.args)
        header = f"🌍 *Translating to:* `{target_lang}`"

    # Case 2: /translate Spanish Hello world
    elif len(context.args) >= 2:
        target_lang = context.args[0]
        text_to_translate = " ".join(context.args[1:])
        header = f"🌍 *Translating to:* `{target_lang}`"

    # Case 3: Nothing provided
    else:
        await update.message.reply_text(
            "⚡ *Usage:*\n"
            "1. `/translate Spanish Hello`\n"
            "2. Reply to any message + `/translate French`",
            parse_mode='Markdown'
        )
        return

    await update.message.reply_text(f"{header}\n\n🔄 *Translating...*", parse_mode='Markdown')

    try:
        prompt = f"Translate the following text to {target_lang}. Keep the tone same. Only return the translation, no extra explanation:\n\n{text_to_translate}"

        # NEW SDK call
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2, # low temp for accurate translation
                max_output_tokens=1000
            )
        )

        caption = f"""╭─〔 🌍 𝗧𝗥𝗔𝗡𝗦𝗟𝗔𝗧𝗘𝗗 〕
│
│ {header}
│
├───────────────────
{response.text}
├───────────────────
│
│ Need another language?
│ `/translate Arabic your text`
│
╰─〔 MUFASER-X AI 〕"""

        await update.message.reply_text(caption, parse_mode='Markdown')

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")