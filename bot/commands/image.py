import os
import time
import requests
from collections import defaultdict
from io import BytesIO
from telegram import Update, InputFile
from telegram.ext import ContextTypes

os.makedirs("bot/images", exist_ok=True)

# ===== RATE LIMIT SYSTEM =====
user_requests = defaultdict(list)
MAX_REQUESTS = 5 # 5 images
TIME_WINDOW = 60 # per 60 seconds

def check_rate_limit(user_id):
    now = time.time()
    user_requests[user_id] = [t for t in user_requests[user_id] if now - t < TIME_WINDOW]

    if len(user_requests[user_id]) >= MAX_REQUESTS:
        time_left = int(TIME_WINDOW - (now - user_requests[user_id][0]))
        return False, time_left

    user_requests[user_id].append(now)
    return True, 0
# ===== END RATE LIMIT =====

async def image_command(update: Update, context: ContextTypes.DEFAULT_TYPE): # <-- CHANGED NAME
    allowed, wait = check_rate_limit(update.effective_user.id)
    if not allowed:
        return await update.message.reply_text(f"⏰ Chill bro 😂 Slow down!\nTry again in *{wait}* seconds", parse_mode="Markdown")
        
    if not context.args:
        return await update.message.reply_text("🖼️ Usage:\n`/image girl with sword cherry blossoms`", parse_mode="Markdown") # <-- CHANGED TEXT

    prompt = " ".join(context.args)
    status = await update.message.reply_text("🎨 Generating image...")

    try:
        url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?width=512&height=512"
        response = requests.get(url, timeout=60)

        if response.status_code!= 200:
            await status.edit_text("❌ Image generation failed.")
            return

        filename = f"img_{update.effective_user.id}_{int(time.time())}.png"
        filepath = os.path.join("bot/images", filename)

        with open(filepath, "wb") as f:
            f.write(response.content)

        await status.delete()
        with open(filepath, "rb") as photo:
            await update.message.reply_photo(photo=InputFile(photo), caption=f"🖼️ Prompt:\n{prompt}")
        os.remove(filepath)

    except Exception as e:
        await status.edit_text(f"❌ Error:\n{str(e)}")


async def wallpaper_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    allowed, wait = check_rate_limit(update.effective_user.id)
    if not allowed:
        return await update.message.reply_text(f"⏰ Chill bro 😂 Slow down!\nTry again in *{wait}* seconds", parse_mode="Markdown")
    
    if not context.args:
        await update.message.reply_text("📱 Usage:\n`/wallpaper aesthetic sunset`", parse_mode="Markdown")
        return

    prompt = " ".join(context.args)
    full_prompt = f"{prompt}, phone wallpaper, vertical, 4k, highly detailed, no text, no watermark"
    status = await update.message.reply_text(f"🎨 Generating wallpaper: *{prompt}*", parse_mode="Markdown")

    try:
        url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(full_prompt)}?width=1080&height=1920"
        response = requests.get(url, timeout=60)
        filename = f"wall_{update.effective_user.id}_{int(time.time())}.png"
        filepath = os.path.join("bot/images", filename)
        with open(filepath, "wb") as f: f.write(response.content)
        await status.delete()
        with open(filepath, "rb") as photo: await update.message.reply_photo(photo=InputFile(photo), caption=f"📱 HD Wallpaper: {prompt}")
        os.remove(filepath)
    except Exception as e: await status.edit_text(f"❌ Error:\n{str(e)}")


async def logo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    allowed, wait = check_rate_limit(update.effective_user.id)
    if not allowed:
        return await update.message.reply_text(f"⏰ Chill bro 😂 Slow down!\nTry again in *{wait}* seconds", parse_mode="Markdown")
    
    if not context.args:
        await update.message.reply_text("🎨 Usage:\n`/logo MUFASER-X bot logo`", parse_mode="Markdown")
        return

    prompt = " ".join(context.args)
    full_prompt = f"{prompt}, logo design, vector, clean background, professional"
    status = await update.message.reply_text(f"🎨 Designing logo: *{prompt}*", parse_mode="Markdown")

    try:
        url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(full_prompt)}?width=1024&height=1024"
        response = requests.get(url, timeout=60)
        filename = f"logo_{update.effective_user.id}_{int(time.time())}.png"
        filepath = os.path.join("bot/images", filename)
        with open(filepath, "wb") as f: f.write(response.content)
        await status.delete()
        with open(filepath, "rb") as photo: await update.message.reply_photo(photo=InputFile(photo), caption=f"🎨 Logo: {prompt}")
        os.remove(filepath)
    except Exception as e: await status.edit_text(f"❌ Error:\n{str(e)}")


async def avatar_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    allowed, wait = check_rate_limit(update.effective_user.id)
    if not allowed:
        return await update.message.reply_text(f"⏰ Chill bro 😂 Slow down!\nTry again in *{wait}* seconds", parse_mode="Markdown")
    
    if not context.args:
        await update.message.reply_text("👤 Usage:\n`/avatar anime boy with blue hair`", parse_mode="Markdown")
        return

    prompt = " ".join(context.args)
    full_prompt = f"{prompt}, avatar profile picture, 1:1 square, portrait, highly detailed"
    status = await update.message.reply_text(f"🎨 Making avatar: *{prompt}*", parse_mode="Markdown")

    try:
        url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(full_prompt)}?width=1024&height=1024"
        response = requests.get(url, timeout=60)
        filename = f"avatar_{update.effective_user.id}_{int(time.time())}.png"
        filepath = os.path.join("bot/images", filename)
        with open(filepath, "wb") as f: f.write(response.content)
        await status.delete()
        with open(filepath, "rb") as photo: await update.message.reply_photo(photo=InputFile(photo), caption=f"👤 Avatar: {prompt}")
        os.remove(filepath)
    except Exception as e: await status.edit_text(f"❌ Error:\n{str(e)}")