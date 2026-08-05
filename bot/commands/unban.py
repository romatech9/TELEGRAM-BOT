from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import BadRequest

async def unban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Usage: /unban 123456789
    chat = update.effective_chat
    user = update.effective_user
    
    # 1. Check if command user is admin
    admins = await chat.get_administrators()
    if user.id not in [admin.user.id for admin in admins]:
        await update.message.reply_text("❌ Only admins can use /unban")
        return
    
    # 2. Get user ID to unban
    if not context.args:
        await update.message.reply_text("Usage: `/unban USER_ID`\n\nGet the ID from @userinfobot or logs.", parse_mode='Markdown')
        return
    
    try:
        target_user_id = int(context.args[0])
        
        # 3. Unban the user
        await chat.unban_member(target_user_id)
        await update.message.reply_text(f"✅ User {target_user_id} has been unbanned. They can join again.")
        
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID. Must be numbers only.")
    except BadRequest as e:
        await update.message.reply_text(f"Failed to unban: {e}")