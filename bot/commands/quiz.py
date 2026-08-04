import os
import re
from google import genai
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

# Create Gemini client once
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
GEMINI_MODEL = "gemini-2.5-flash"


async def quiz_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topic = " ".join(context.args) if context.args else "general knowledge"
    user_id = update.effective_user.id

    msg = await update.message.reply_text("🧠 Generating quiz...")

    try:
        prompt = f"""
Create ONE multiple choice question about {topic}.

Return EXACTLY in this format:

Question: What is ...?
A) Option A
B) Option B
C) Option C
D) Option D
Answer: A
"""

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
        )

        text = response.text.strip()

        question = re.search(r"Question:\s*(.*)", text)
        a = re.search(r"A\)\s*(.*)", text)
        b = re.search(r"B\)\s*(.*)", text)
        c = re.search(r"C\)\s*(.*)", text)
        d = re.search(r"D\)\s*(.*)", text)
        answer = re.search(r"Answer:\s*([ABCD])", text)

        if not all([question, a, b, c, d, answer]):
            await msg.edit_text("❌ Failed to generate quiz. Try again.")
            return

        # Save answer with user_id so multiple people can play
        context.user_data[f"quiz_{user_id}"] = answer.group(1)

        # IMPORTANT: callback_data starts with quiz_
        keyboard = [
            [InlineKeyboardButton(f"A) {a.group(1)}", callback_data="quiz_A")],
            [InlineKeyboardButton(f"B) {b.group(1)}", callback_data="quiz_B")],
            [InlineKeyboardButton(f"C) {c.group(1)}", callback_data="quiz_C")],
            [InlineKeyboardButton(f"D) {d.group(1)}", callback_data="quiz_D")],
        ]

        await msg.delete()

        await update.message.reply_text(
            f"🧠 *{question.group(1)}*\n\nA) {a.group(1)}\nB) {b.group(1)}\nC) {c.group(1)}\nD) {d.group(1)}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    except Exception as e:
        await msg.edit_text(f"❌ Error:\n{e}")


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    correct = context.user_data.get(f"quiz_{user_id}")

    if not correct:
        await query.edit_message_text("⌛ Quiz expired. Use /quiz again")
        return

    user_answer = query.data.replace("quiz_", "") # remove quiz_ from quiz_A

    if user_answer == correct:
        result = "✅ Correct! 🎉"
    else:
        result = f"❌ Wrong!\n\n✅ Correct Answer: {correct}"

    await query.edit_message_text(f"{query.message.text}\n\n{result}")
    context.user_data.pop(f"quiz_{user_id}", None) # clear it