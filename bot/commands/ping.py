from telegram import Update
from telegram.ext import ContextTypes
import time
import platform
import psutil
from datetime import datetime
import pytz

# Set this when bot starts
start_time = time.time()
KAMPALA_TZ = pytz.timezone("Africa/Kampala")

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    start = time.time()
    msg = await update.message.reply_text("🏓 Pong! Checking...")
    end = time.time()
    
    latency = round((end - start) * 1000)
    uptime_seconds = time.time() - start_time
    days, remainder = divmod(int(uptime_seconds), 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    uptime_str = f"{days}d {hours}h {minutes}m {seconds}s"
    
    kampala_now = datetime.now(KAMPALA_TZ)
    load_avg = psutil.getloadavg()
    
    text = f"""✅𝙈𝙐𝙁𝘼𝙎𝙀𝙍-𝙓 𝙄𝙎 𝙊𝙉 𝙁𝙄𝙍𝙀🔥

🎾 *Pong!*
⚡ *Latency:* `{latency}ms`
🤖 *Uptime:* `{uptime_str}`
🖥️ *Platform:* `{platform.system()}`
📊 *CPU Load:* `{load_avg[0]:.2f}`
🕐 *Time:* `{kampala_now.strftime('%I:%M:%S %p')}`
📅 *Date:* `{kampala_now.strftime('%d/%m/%Y')}`"""

    await msg.edit_text(text, parse_mode="Markdown")