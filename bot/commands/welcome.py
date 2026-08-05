import datetime
from telegram import Update
from telegram.ext import ContextTypes

# Stores welcome settings per group. Resets on restart
group_settings = {}

async def is_admin(update, context):
    member = await context.bot.get_chat_member(update.effective_chat.id, update.effective_user.id)
    return member.status in ['administrator', 'creator']

async def welcome_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        return await update.message.reply_text("❌ Only admins can use this")

    chat_id = update.effective_chat.id

    # Default to ON if first time
    if chat_id not in group_settings:
        group_settings[chat_id] = {"welcome": True}

    # Check if user typed /welcome on or /welcome off
    if context.args:
        arg = context.args[0].lower()
        if arg == "on":
            group_settings[chat_id]["welcome"] = True
            return await update.message.reply_text("✅ Welcome messages turned: ON")
        elif arg == "off":
            group_settings[chat_id]["welcome"] = False
            return await update.message.reply_text("❌ Welcome messages turned : OFF")

    # If no argument, just toggle
    group_settings[chat_id]["welcome"] = not group_settings[chat_id]["welcome"]
    status = "ON" if group_settings[chat_id]["welcome"] else "OFF"
    await update.message.reply_text(f"Welcome messages: {status}")

async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # KEY FIX: Use message.new_chat_members instead of chat_member
    chat_id = update.effective_chat.id

    # Check if welcome is ON for this group
    if chat_id not in group_settings:
        group_settings[chat_id] = {"welcome": True} # default ON
    if not group_settings[chat_id]["welcome"]:
        return

    # Loop through all new members
    for user in update.message.new_chat_members:
        # Don't welcome bots
        if user.is_bot:
            continue

        chat = update.effective_chat

        now = datetime.datetime.now()
        date_str = now.strftime("%d/%m/%Y")
        time_str = now.strftime("%I:%M %p")
        day_str = now.strftime("%A")

        name = user.first_name
        username = f"@{user.username}" if user.username else "No username"
        user_id = user.id
        member_count = await context.bot.get_chat_member_count(chat.id)

        photos = await context.bot.get_user_profile_photos(user_id, limit=1)
        has_photo = photos.total_count > 0

        text = f"╭─〔 🤖 𝗠𝗨𝗙𝗔𝗦𝗘𝗥-𝗫 𝗪𝗘𝗟𝗖𝗢𝗠𝗘 〕\n│\n│ 🌐 𝑪𝑶𝑵𝑮𝑹𝑨𝑻𝑼𝑳𝑨𝑻𝑰𝑶𝑵𝑺🎉\n│\n│✨ 𝗡𝗘𝗪 𝗠𝗘𝗠𝗕𝗘𝗥✨\n│\n│ 🎇 *Group:* {chat.title}\n├───────────────────\n│👤 *Name:* {name}\n│🆔 *Username:* {username}\n│🪪 *User ID:* `{user_id}`\n│👥 *Member #:* {member_count}\n├───────────────────\n│ 📅 *Date:* `{date_str}`\n│ 🕐 *Time:* `{time_str}`\n│ 📆 *Day:* `{day_str}`\n├───────────────────\n│ 📜 *Read the pinned rules please*\n│ 🚀 *𝙈𝙐𝙁𝘼𝙎𝙀𝙍-𝙓 𝘽𝙊𝙏*\n│Type /start to unlock all my power\n╰─〔 ⚡ MUFASER-X 〕"

        # REMOVED BUTTONS HERE
        # keyboard = [[InlineKeyboardButton("📜 Rules", callback_data="rules")]]
        # reply_markup = InlineKeyboardMarkup(keyboard)

        if has_photo:
            photo_file = photos.photos[0][0].file_id
            await context.bot.send_photo(chat_id=chat.id, photo=photo_file, caption=text, parse_mode="Markdown")
        else:
            await context.bot.send_message(chat_id=chat.id, text=text, parse_mode="Markdown")