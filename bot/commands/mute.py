from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import BadRequest
from datetime import datetime, timedelta

async def mute_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    
    # 1. Check admin
    try:
        chat_member = await chat.get_member(user.id)
        if chat_member.status not in ['administrator', 'creator']:
            await update.message.reply_text("❌ Only admins can use /mute")
            return
    except:
        await update.message.reply_text("❌ Can't check admin status")
        return
    
    # 2. Must reply to user
    if not update.message.reply_to_message:
        await update.message.reply_text("Usage: Reply to someone's message with `/mute 30m`", parse_mode='Markdown')
        return
    
    target_user = update.message.reply_to_message.from_user
    
    # 3. Parse time
    duration_str = context.args[0] if context.args else "1h"
    minutes = 60
    try:
        if duration_str.endswith("m"):
            minutes = int(duration_str[:-1])
        elif duration_str.endswith("h"):
            minutes = int(duration_str[:-1]) * 60
        elif duration_str.endswith("d"):
            minutes = int(duration_str[:-1]) * 60 * 24
    except:
        minutes = 60
    
    until_date = datetime.now() + timedelta(minutes=minutes)
    
    # 4. Mute - THIS IS THE KEY FIX FOR v20
    try:
        await chat.restrict_member(
            user_id=target_user.id,
            until_date=until_date,
            permissions={"can_send_messages": False}
        )
        await update.message.reply_text(f"🔇 {target_user.full_name} muted for {duration_str}")
    except BadRequest as e:
        await update.message.reply_text(f"❌ Failed: {e}\n\nCheck: 1. Bot is admin 2. Bot has 'Restrict Members' permission")