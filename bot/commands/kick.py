from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import BadRequest

async def kick_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Usage: /kick reply to a user
    chat = update.effective_chat
    user = update.effective_user
    
    # 1. Check if command user is admin
    admins = await chat.get_administrators()
    if user.id not in [admin.user.id for admin in admins]:
        await update.message.reply_text("❌ Only admins can use /kick")
        return
    
    # 2. Get target user - must reply to their message
    if not update.message.reply_to_message:
        await update.message.reply_text("Usage: Reply to the user's message with /kick")
        return
    
    target_user = update.message.reply_to_message.from_user
    
    # 3. Prevent kicking admins
    if target_user.id in [admin.user.id for admin in admins]:
        await update.message.reply_text("❌ Can't kick another admin")
        return
    
    # 4. Kick = ban then unban instantly
    try:
        await chat.ban_member(target_user.id)
        await chat.unban_member(target_user.id)  # This lets them rejoin
        await update.message.reply_text(f"👢 {target_user.full_name} has been kicked.")
    except BadRequest as e:
        await update.message.reply_text(f"Failed to kick: {e}")