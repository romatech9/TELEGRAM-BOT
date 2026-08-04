from telegram import Update, ChatPermissions
from telegram.ext import ContextTypes, CommandHandler

LOCK_TYPES = {
    "msg": "Text Messages",
    "media": "Media",
    "sticker": "Stickers/GIFs",
    "link": "Links/Web Previews",
    "poll": "Polls",
    "voice": "Voice Notes",
    "video": "Videos",
    "photo": "Photos",
    "all": "Everything"
}

def get_current_perms(context, chat_id):
    default = {
        "can_send_messages": True,
        "can_send_audios": True,
        "can_send_documents": True,
        "can_send_photos": True,
        "can_send_videos": True,
        "can_send_video_notes": True,
        "can_send_voice_notes": True,
        "can_send_polls": True,
        "can_send_other_messages": True,
        "can_add_web_page_previews": True,
    }
    return context.bot_data.setdefault(f"perms_{chat_id}", default.copy())

async def check_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    bot = await context.bot.get_me()

    bot_member = await chat.get_member(bot.id)
    if not bot_member.can_restrict_members:
        await update.message.reply_text("❌ *Give me 'Restrict Members' permission first*")
        return False

    user_member = await chat.get_member(user.id)
    if user_member.status not in ["administrator", "creator"]:
        await update.message.reply_text("❌ *Only admins can use this*")
        return False
    return True

def apply_lock(perms_dict, lock_type, value):
    if lock_type == "all":
        for k in perms_dict: perms_dict[k] = value
    elif lock_type == "msg":
        perms_dict["can_send_messages"] = value
    elif lock_type == "media":
        perms_dict["can_send_audios"] = value; perms_dict["can_send_documents"] = value
        perms_dict["can_send_photos"] = value; perms_dict["can_send_videos"] = value
    elif lock_type == "sticker":
        perms_dict["can_send_other_messages"] = value
    elif lock_type == "link":
        perms_dict["can_add_web_page_previews"] = value
    elif lock_type == "poll":
        perms_dict["can_send_polls"] = value
    elif lock_type == "voice":
        perms_dict["can_send_voice_notes"] = value
    elif lock_type == "video":
        perms_dict["can_send_videos"] = value; perms_dict["can_send_video_notes"] = value
    elif lock_type == "photo":
        perms_dict["can_send_photos"] = value

async def lock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_admin(update, context): return

    args = context.args
    if not args:
        await update.message.reply_text(
            "💅 *Usage:* `/lock <type>`\n\n*Types:* `msg, media, sticker, link, poll, voice, video, photo, all`\n*Ex:* `/lock sticker`",
            parse_mode="Markdown"
        )
        return

    lock_type = args[0].lower()
    if lock_type not in LOCK_TYPES:
        await update.message.reply_text("❌ *Invalid type. Use:* `msg, media, sticker, link, poll, voice, video, photo, all`")
        return

    chat_id = update.effective_chat.id
    perms_dict = get_current_perms(context, chat_id)
    apply_lock(perms_dict, lock_type, False)

    try:
        await context.bot.set_chat_permissions(chat_id=chat_id, permissions=ChatPermissions(**perms_dict))
        await update.message.reply_text(f"🔒 *Locked:* {LOCK_TYPES[lock_type]}")
    except Exception as e:
        await update.message.reply_text(f"❌ *Error:* `{e}`")

async def unlock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_admin(update, context): return

    args = context.args
    if not args:
        await update.message.reply_text(
            "💅 *Usage:* `/unlock <type>`\n\n*Types:* `msg, media, sticker, link, poll, voice, video, photo, all`\n*Ex:* `/unlock link`",
            parse_mode="Markdown"
        )
        return

    unlock_type = args[0].lower()
    if unlock_type not in LOCK_TYPES:
        await update.message.reply_text("❌ *Invalid type*")
        return

    chat_id = update.effective_chat.id
    perms_dict = get_current_perms(context, chat_id)
    apply_lock(perms_dict, unlock_type, True)

    try:
        await context.bot.set_chat_permissions(chat_id=chat_id, permissions=ChatPermissions(**perms_dict))
        await update.message.reply_text(f"🔓 *Unlocked:* {LOCK_TYPES[unlock_type]}")
    except Exception as e:
        await update.message.reply_text(f"❌ *Error:* `{e}`")

async def locks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    perms_dict = get_current_perms(context, chat_id)

    locked = []
    unlocked = []

    checks = {
        "msg": not perms_dict["can_send_messages"],
        "media": not (perms_dict["can_send_audios"] and perms_dict["can_send_documents"] and perms_dict["can_send_photos"] and perms_dict["can_send_videos"]),
        "sticker": not perms_dict["can_send_other_messages"],
        "link": not perms_dict["can_add_web_page_previews"],
        "poll": not perms_dict["can_send_polls"],
        "voice": not perms_dict["can_send_voice_notes"],
        "video": not (perms_dict["can_send_videos"] and perms_dict["can_send_video_notes"]),
        "photo": not perms_dict["can_send_photos"],
    }

    for key, is_locked in checks.items():
        if is_locked:
            locked.append(f"🔒 {LOCK_TYPES[key]}")
        else:
            unlocked.append(f"🔓 {LOCK_TYPES[key]}")

    text = "*Current Group Locks*\n\n"
    text += "*Locked:*\n" + ("\n".join(locked) if locked else "None") + "\n\n"
    text += "*Unlocked:*\n" + ("\n".join(unlocked) if unlocked else "None")

    await update.message.reply_text(text, parse_mode="Markdown")