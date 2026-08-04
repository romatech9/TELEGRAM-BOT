import os
from google import genai
from google.genai import types
from telegram import Update
from telegram.ext import ContextTypes

# NEW SDK: create client once
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

async def explain_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Case 1: Reply to a message
    if update.message.reply_to_message and update.message.reply_to_message.text:
        topic = update.message.reply_to_message.text
        header = "📎 *Explaining this message for you*"
    
    # Case 2: /explain topic here
    elif context.args:
        topic = " ".join(context.args)
        header = f"💡 *Topic:* `{topic}`"
    
    # Case 3: Nothing provided
    else:
        await update.message.reply_text(
            "⚡ *Usage:*\n"
            "1. `/explain quantum physics`\n"
            "2. Reply to any message + `/explain`", 
            parse_mode='Markdown'
        )
        return
    
    await update.message.reply_text(f"{header}\n\n🧠 *Thinking...* 2 sec", parse_mode='Markdown')
    
    try:
        prompt = f"Explain this in a simple, clear way with examples and emojis. Make it easy for a 12 year old to understand. Keep it under 400 words. Be friendly:\n\n{topic}"
        
        # NEW SDK call
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.8, # higher for creative explanations
                max_output_tokens=1000
            )
        )
        
        caption = f"""╭─〔 💡 𝗘𝗫𝗣𝗟𝗔𝗜𝗡𝗘𝗗 𝗕𝗬 𝗠𝗨𝗙𝗔𝗦𝗘𝗥-𝗫 〕
│
{response.text}
├───────────────────
│ Need another explanation? 
│ Reply to a message + `/explain`
│
╰─〔 ⚡ MUFASER-X AI〕"""
        
        await update.message.reply_text(caption, parse_mode='Markdown')
        
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")