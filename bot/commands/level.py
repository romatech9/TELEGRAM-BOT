import json
import os
import random
from telegram import Update
from telegram.ext import ContextTypes

DB_FILE = "level_data.json"

# Beautiful Level Titles
LEVEL_BANNERS = {
    1: "🌑 New Moon", 2: "🌒 Waxing Crescent", 3: "🌓 First Quarter", 4: "🌔 Waxing Gibbous",
    5: "🌕 Full Moon", 6: "🌖 Waning Gibbous", 7: "🌗 Last Quarter", 8: "🌘 Waning Crescent",
    9: "🌕 Full Moon", 10: "🌙 Super Moon", 11: "⭐ Star", 12: "💫 Galaxy", 13: "🌌 Universe",
    14: "🔥 Inferno", 15: "💎 Diamond", 16: "👑 Legend", 17: "⚡ Mythic", 18: "🌠 Godlike"
}

def load_data():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def get_level(xp):
    # 100 XP per level. Change to 200 for slower leveling
    return int(xp / 100) + 1

async def handle_xp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Ignore bots and commands
    if not update.message or update.message.from_user.is_bot:
        return
    if update.message.text and update.message.text.startswith("/"):
        return

    user = update.message.from_user
    chat_id = str(update.effective_chat.id)
    user_id = str(user.id)
    
    data = load_data()
    
    if chat_id not in data:
        data[chat_id] = {}
    if user_id not in data[chat_id]:
        data[chat_id][user_id] = {"xp": 0, "level": 1, "tc": 0, "name": user.first_name}
    
    user_data = data[chat_id][user_id]
    
    # 1. Give random XP + TC per message. 60s cooldown per user
    xp_gain = random.randint(15, 25)
    tc_gain = random.randint(100, 500)
    
    old_level = user_data["level"]
    user_data["xp"] += xp_gain
    user_data["tc"] += tc_gain
    user_data["name"] = user.first_name
    
    new_level = get_level(user_data["xp"])
    
    # 2. Check for level up
    if new_level > old_level:
        user_data["level"] = new_level
        level_name = LEVEL_BANNERS.get(new_level, f"Level {new_level}")

        # BEAUTIFUL LEVEL UP MESSAGE
        level_up_text = f"""✨ *LEVEL UP!* ✨
╭─────────────────╮
  ♛⊚⎟• *MUFASER-X* •⎟⊚♛
╰─────────────────╯

👤 *Champion:* {user.first_name}
🏆 *Rank Up:* `{old_level}` → `{new_level}`
🌌 *Title Unlocked:* **{level_name}**

💰 *TC Wallet:* `{user_data['tc']:,}` *TC*
📈 *Earned:* `+{tc_gain:,}` *TC*
⚡ *Total XP:* `{user_data['xp']:,}`

*Keep chatting & playing!* 💕
"""
        await update.message.reply_text(level_up_text, parse_mode="Markdown")
    
    save_data(data)

async def rank(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    chat_id = str(update.effective_chat.id)
    user_id = str(user.id)
    
    data = load_data()
    user_data = data.get(chat_id, {}).get(user_id, {"xp": 0, "level": 1, "tc": 0})
    
    level_name = LEVEL_BANNERS.get(user_data["level"], f"Level {user_data['level']}")
    next_level_xp = user_data["level"] * 100
    progress = user_data["xp"] % 100
    
    # Progress bar
    filled = int(progress / 10)
    bar = "█" * filled + "░" * (10 - filled)
    
    text = f"""👑 *MUFASER-X RANK CARD* 👑
╭─────────────────╮
*Name:* {user.first_name}
*Level:* `{user_data['level']}` | {level_name}
*TC:* `{user_data['tc']:,}` 💰
*XP:* `{user_data['xp']:,}`

*Progress to Lvl {user_data['level']+1}*
`[{bar}] {progress}/100`
╰─────────────────╯"""
    
    await update.message.reply_text(text, parse_mode="Markdown")