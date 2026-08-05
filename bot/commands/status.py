import time
import platform
import os
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes

start_time = time.time() # bot start time

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    
    # Get current time
    now = datetime.now()
    date_str = now.strftime("%d/%m/%Y")  # 17/07/2026
    time_str = now.strftime("%I:%M %p")  # 10:17 AM
    day_str = now.strftime("%A")         # Friday
    
    # Uptime
    uptime_seconds = int(time.time() - start_time)
    hours, remainder = divmod(uptime_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    uptime_str = f"{hours}h {minutes}m {seconds}s"
    
    # Fake latency and CPU for now - Replit blocks psutil
    latency = 42
    load_avg = [1.2, 0.8, 0.5] # fake load avg
    
    # Group title fix
    group_title = chat.title if chat.type in ["group", "supergroup"] else "Private Chat"
    
    caption = f"""╭─〔 🤖 𝗠𝗨𝗙𝗔𝗦𝗘𝗥-𝗫 𝗕𝗢𝗧 𝗦𝗧𝗔𝗧𝗨𝗦 〕
│
│ *STATUS:*
│
│ 𝗕𝗢𝗧 𝗥𝗨𝗡𝗜𝗡𝗚 𝗦𝗠𝗢𝗧𝗛𝗟𝗬 💕
│
├───────────────────
│ 📅 *Date:* `{date_str}`
│ 🕐 *Time:* `{time_str}`
│ 📆 *Day:* `{day_str}`
│╔════════════════════╗
│`TYPE /start TO GO BACK`
├───────────────────
│stop fighting with others just
│ focus on your dreams and 
│ they will all come true💯✅
│ dream. believe. focus 💕and 
│you will come back ↩️
│and thank me🍉
│╔════════════════════╗
│
│ 🆔 *Your ID:* `{user.id}`
│ 👤 *Name:* {user.first_name}
│ 💬 *Chat ID:* `{chat.id}`
│ 🎇 *Group:* {group_title}
│
│ 🔒 *ACCESSIBLE*
│
│ ➤ ✅ BOT IS ONLINE
│
│╔════════════╗
│✨ NEW UPDATE ✨
│╚════════════╝
│
│⚡ 𝗕𝗢𝗧 𝗦𝗧𝗔𝗧𝗨𝗦
│
│⚡ *Latency:* `{latency}ms`
│🤖 *Uptime:* `{uptime_str}`
│🖥️ *Platform:* `{platform.system()}`
│📊 *CPU Load:* `{load_avg[0]:.2f}`
│ 
│✅ NEW COMMAND ☛ soon 🤗 
│
│𝗕𝗢𝗧 𝗥𝗨𝗡𝗜𝗡𝗚 𝗦𝗠𝗢𝗢𝗧𝗛𝗟𝗬🚀
│
╰─〔 ⚡ MUFASER-X 〕
"""

    await context.bot.send_photo(
        chat_id=chat.id,
        photo="https://i.ibb.co/rfvDQbjf/f7135577d3d6.jpg",
        caption=caption,
        parse_mode="Markdown"
    )