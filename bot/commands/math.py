import os
from google import genai
from google.genai import types
from telegram import Update
from telegram.ext import ContextTypes

# NEW SDK: create client once
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

async def math_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Case 1: Reply to a message
    if update.message.reply_to_message and update.message.reply_to_message.text:
        problem = update.message.reply_to_message.text
        header = "🧮 *Solving replied problem*"
    
    # Case 2: /math 2x + 5 = 15
    elif context.args:
        problem = " ".join(context.args)
        header = f"🧮 *Problem:* `{problem}`"
    
    else:
        await update.message.reply_text(
            "⚡ *Usage:*\n"
            "1. `/math 2x + 5 = 15`\n"
            "2. Reply to any math question + `/math`",
            parse_mode='Markdown'
        )
        return

    await update.message.reply_text(f"{header}\n\n📊 *Calculating...*", parse_mode='Markdown')

    try:
        prompt = f"""You are a math tutor. Solve this step by step and explain clearly:
        
        Problem: {problem}
        
        Format: 
        1. Final Answer
        2. Step by step solution
        Keep it simple for students."""

        # NEW SDK call
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.3,  # lower for math
                max_output_tokens=1000
            )
        )

        caption = f"""╭─〔 🧮 𝗠𝗔𝗧𝗛 𝗦𝗢𝗟𝗩𝗘𝗥 〕
│
│ {header}
│
├───────────────────
{response.text}
├───────────────────
│
│ Need help with algebra/geometry?
│ Just send the question
│
╰─〔 MUFASER-X AI 〕"""

        await update.message.reply_text(caption, parse_mode='Markdown')

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")