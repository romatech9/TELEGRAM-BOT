from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import BadRequest

async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Usage: /ban reply to a user OR /ban @username
    chat = update.effective_chat
    user = update.effective_user
    
    # 1. Check if command user is admin
    admins = await chat.get_administrators()
    if user.id not in [admin.user.id for admin in admins]:
        await update.message.reply_text("❌ Only admins can use /ban")
        return
    
    # 2. Get target user - either by reply or mention
    target_user = None
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
    elif context.args:
        await update.message.reply_text("Reply to the user's message with /ban. Can't ban by username alone.")
        return
    else:
        await update.message.reply_text("Usage: Reply to a user's message with /ban")
        return
    
    # 3. Prevent banning admins
    if target_user.id in [admin.user.id for admin in admins]:
        await update.message.reply_text("❌ Can't ban another admin")
        return
    
    # 4. Ban the user
    try:
        await chat.ban_member(target_user.id)
        await update.message.reply_text(f" {target_user.full_name} ✅ band successfully.")
    except BadRequest as e:
        await update.message.reply_text(f"Failed to ban: {e}")