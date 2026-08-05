from google import genai
from google.genai import types
import os
from telegram import Update
from telegram.ext import ContextTypes

# NEW SDK: create client instead of configure
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

async def summarize_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    # Must reply to a message
    if not update.message.reply_to_message or not update.message.reply_to_message.text:
        await update.message.reply_text(
            "⚡ *Usage:* Reply to any long text with `/summarize`\n\n"
            "Example: Forward a news article → reply `/summarize`",
            parse_mode='Markdown'
        )
        return
    
    long_text = update.message.reply_to_message.text
    
    if len(long_text) < 50:
        await update.message.reply_text("❌ Text too short to summarize bro. Send something longer.")
        return

    await update.message.reply_text("📄 *MUFASER-X is reading and summarizing...*", parse_mode='Markdown')

    try:
        prompt = f"""Summarize the following text in 3-5 bullet points. 
        Keep it clear, simple, and in the same language as the text.
        Highlight key facts only.
        
        Text: {long_text}"""

        # NEW SDK call
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=1000
            )
        )

        caption = f"""╭─〔 📄 𝗦𝗨𝗠𝗔𝗥𝗬 𝗗𝗢𝗡𝗘 〕
│
│ *Original length:* {len(long_text)} characters
│
├───────────────────
{response.text}
├───────────────────
│
│ Pro tip: Reply to any article/news
│ and use `/summarize` 
│
╰─〔 MUFASER-X AI 〕"""

        await update.message.reply_text(caption, parse_mode='Markdown')

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")