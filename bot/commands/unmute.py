from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import BadRequest

async def unmute_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    
    # 1. Check admin
    try:
        chat_member = await chat.get_member(user.id)
        if chat_member.status not in ['administrator', 'creator']:
            await update.message.reply_text("❌ Only admins can use /unmute")
            return
    except:
        await update.message.reply_text("❌ Can't check admin status")
        return
    
    # 2. Must reply to user
    if not update.message.reply_to_message:
        await update.message.reply_text("Usage: Reply to the muted person's message with `/unmute`", parse_mode='Markdown')
        return
    
    target_user = update.message.reply_to_message.from_user
    
    # 3. Unmute - KEY FIX FOR v20
    try:
        await chat.restrict_member(
            user_id=target_user.id,
            permissions={
                "can_send_messages": True,
                "can_send_media_messages": True,
                "can_send_other_messages": True,
                "can_add_web_page_previews": True
            }
        )
        await update.message.reply_text(f"🔊 {target_user.full_name} has been unmuted.")
    except BadRequest as e:
        await update.message.reply_text(f"❌ Failed: {e}\n\nCheck: 1. Bot is admin 2. Bot has 'Restrict Members' permission")