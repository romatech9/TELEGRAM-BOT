from telegram import Update
from telegram.ext import ContextTypes

async def grouplink(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    
    # Only works in groups
    if chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("❌ *This command only works in groups*")
        return
    
    # Bot must be admin
    bot_member = await chat.get_member(context.bot.id)
    if bot_member.status not in ["administrator", "creator"]:
        await update.message.reply_text("❌ *Make me admin with 'Invite Users' permission first*")
        return
    
    try:
        invite_link = await context.bot.export_chat_invite_link(chat.id)
        await update.message.reply_text(
            f"🔗 *Group Invite Link*\n\n`{invite_link}`\n\nTap to copy and share",
            parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ *Failed to get link*\n`{e}`")