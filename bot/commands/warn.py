import json
import os
from telegram import Update
from telegram.ext import ContextTypes

WARN_FILE = "warns.json"
WARN_LIMIT = 3  # auto ban after 3 warns

def load_warns():
    if not os.path.exists(WARN_FILE):
        return {}
    with open(WARN_FILE, "r") as f:
        return json.load(f)

def save_warns(data):
    with open(WARN_FILE, "w") as f:
        json.dump(data, f, indent=4)

async def check_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    bot = await context.bot.get_me()
    bot_member = await chat.get_member(bot.id)
    if not bot_member.can_restrict_members:
        await update.message.reply_text("❌ *Give me 'Ban Users' permission first*")
        return False
    user_member = await chat.get_member(user.id)
    if user_member.status not in ["administrator", "creator"]:
        await update.message.reply_text("❌ *Only admins can use this*")
        return False
    return True

async def warn_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_admin(update, context): return
    
    if not update.message.reply_to_message:
        await update.message.reply_text("💅 *Reply to a user's message to warn them*\n*Ex:* `/warn spamming`", parse_mode="Markdown")
        return

    reason = " ".join(context.args) if context.args else "No reason given"
    target = update.message.reply_to_message.from_user
    chat_id = str(update.effective_chat.id)

    warns = load_warns()
    warns.setdefault(chat_id, {})
    warns[chat_id].setdefault(str(target.id), {"count": 0, "reasons": []})
    
    warns[chat_id][str(target.id)]["count"] += 1
    warns[chat_id][str(target.id)]["reasons"].append(reason)
    count = warns[chat_id][str(target.id)]["count"]
    
    save_warns(warns)

    text = f"⚠️ *Warned:* {target.mention_html()}\n*Reason:* {reason}\n*Warns:* {count}/{WARN_LIMIT}"

    if count >= WARN_LIMIT:
        try:
            await context.bot.ban_chat_member(update.effective_chat.id, target.id)
            text += f"\n\n🚫 *Auto Banned:* Reached {WARN_LIMIT} warns"
            del warns[chat_id][str(target.id)]
            save_warns(warns)
        except:
            text += "\n\n❌ *Couldn't ban user*"

    await update.message.reply_html(text)

async def warns_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    warns = load_warns()
    
    if update.message.reply_to_message:
        target = update.message.reply_to_message.from_user
        user_data = warns.get(chat_id, {}).get(str(target.id))
        if not user_data:
            await update.message.reply_text(f"✅ {target.first_name} has *0 warns*", parse_mode="Markdown")
            return
        text = f"*Warns for {target.mention_html()}:* {user_data['count']}/{WARN_LIMIT}\n\n"
        for i, r in enumerate(user_data['reasons'], 1):
            text += f"{i}. {r}\n"
        await update.message.reply_html(text)
    else:
        chat_warns = warns.get(chat_id, {})
        if not chat_warns:
            await update.message.reply_text("✅ *No one has warns in this group*", parse_mode="Markdown")
            return
        text = "*Group Warn List:*\n\n"
        for uid, data in chat_warns.items():
            try:
                user = await context.bot.get_chat_member(chat_id, uid)
                name = user.user.first_name
                text += f"• {name}: {data['count']}/{WARN_LIMIT}\n"
            except: pass
        await update.message.reply_text(text, parse_mode="Markdown")

async def delwarn_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_admin(update, context): return
    if not update.message.reply_to_message:
        await update.message.reply_text("💅 *Reply to a user's message to remove 1 warn*", parse_mode="Markdown")
        return
    target = update.message.reply_to_message.from_user
    chat_id = str(update.effective_chat.id)
    warns = load_warns()
    user_data = warns.get(chat_id, {}).get(str(target.id))
    if not user_data or user_data['count'] <= 0:
        await update.message.reply_text("✅ *This user has no warns*", parse_mode="Markdown")
        return
    user_data['count'] -= 1
    if user_data['reasons']: user_data['reasons'].pop()
    if user_data['count'] == 0: del warns[chat_id][str(target.id)]
    save_warns(warns)
    await update.message.reply_html(f"🗑️ *Removed 1 warn from:* {target.mention_html()}\n*Now:* {user_data['count']}/{WARN_LIMIT}")

async def resetwarns_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_admin(update, context): return
    if not update.message.reply_to_message:
        await update.message.reply_text("💅 *Reply to a user's message to reset all their warns*", parse_mode="Markdown")
        return
    target = update.message.reply_to_message.from_user
    chat_id = str(update.effective_chat.id)
    warns = load_warns()
    if str(target.id) in warns.get(chat_id, {}):
        del warns[chat_id][str(target.id)]
        save_warns(warns)
    await update.message.reply_html(f"✅ *Reset all warns for:* {target.mention_html()}")