import os
import time
import requests
from collections import defaultdict
from telegram import Update, InputFile
from telegram.ext import ContextTypes

os.makedirs("bot/images", exist_ok=True)

# ===== RATE LIMIT SYSTEM =====
user_requests = defaultdict(list)
MAX_REQUESTS = 5 # 5 images
TIME_WINDOW = 60 # per 60 seconds

def check_rate_limit(user_id):
    now = time.time()
    # Remove old requests
    user_requests[user_id] = [t for t in user_requests[user_id] if now - t < TIME_WINDOW]

    if len(user_requests[user_id]) >= MAX_REQUESTS:
        time_left = int(TIME_WINDOW - (now - user_requests[user_id][0]))
        return False, time_left

    user_requests[user_id].append(now)
    return True, 0
# ===== END RATE LIMIT =====

async def anime_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    allowed, wait = check_rate_limit(update.effective_user.id)
    if not allowed:
        return await update.message.reply_text(f"⏰ Chill bro 😂 Slow down!\nTry again in *{wait}* seconds", parse_mode="Markdown")
        
    if not context.args:
        return await update.message.reply_text("🌸 Usage:\n`/anime girl with sword cherry blossoms`", parse_mode="Markdown")
    
    prompt = " ".join(context.args)
    full_prompt = f"{prompt}, anime style, highly detailed, digital art, vibrant colors"
    status = await update.message.reply_text(f"🌸 Generating anime: *{prompt}*", parse_mode="Markdown")
    
    url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(full_prompt)}?width=1024&height=1024"
    response = requests.get(url, timeout=60)
    
    filename = f"anime_{update.effective_user.id}_{int(time.time())}.png"
    filepath = os.path.join("bot/images", filename)
    with open(filepath, "wb") as f:
        f.write(response.content)
    
    await status.delete()
    with open(filepath, "rb") as photo:
        await update.message.reply_photo(photo=InputFile(photo), caption=f"🌸 Anime: {prompt}")
    os.remove(filepath)


async def remix_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ADDED RATE LIMIT
    allowed, wait = check_rate_limit(update.effective_user.id)
    if not allowed:
        return await update.message.reply_text(f"⏰ Chill bro 😂 Slow down!\nTry again in *{wait}* seconds", parse_mode="Markdown")
    
    message = update.message.reply_to_message
    style = " ".join(context.args) if context.args else "anime"
    
    if not message or not message.photo:
        # No photo replied, just generate a new image in that style
        status = await update.message.reply_text(f"🖌️ Generating new *{style}* image...", parse_mode="Markdown")
        prompt = f"beautiful {style} style artwork, highly detailed, digital art, trending on artstation"
    else:
        # Photo was replied to - true remix
        status = await update.message.reply_text(f"🖌️ Remixing photo to *{style}* style...", parse_mode="Markdown")
        prompt = f"remix this photo into {style} style, highly detailed, digital art"

    try:
        url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?width=1024&height=1024"
        response = requests.get(url, timeout=60)
        
        filename = f"remix_{update.effective_user.id}_{int(time.time())}.png"
        filepath = os.path.join("bot/images", filename)
        with open(filepath, "wb") as f:
            f.write(response.content)

        await status.delete()
        with open(filepath, "rb") as photo:
            await update.message.reply_photo(photo=InputFile(photo), caption=f"🖌️ Style: {style}")
        os.remove(filepath)

    except Exception as e:
        await status.edit_text(f"❌ Error:\n{str(e)}")