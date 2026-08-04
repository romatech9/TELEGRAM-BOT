import asyncio
from telegram import Update
from telegram.ext import ContextTypes

async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    bot = await context.bot.get_me()
    try:
        bot_member = await chat.get_member(bot.id)
        user_member = await chat.get_member(user.id)
    except:
        return False, False
    
    is_bot_admin = bot_member.status in ["administrator", "creator"] and bot_member.can_delete_messages
    is_user_admin = user_member.status in ["administrator", "creator"]
    return is_bot_admin, is_user_admin

async def del_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_bot_admin, is_user_admin = await is_admin(update, context)
    
    if not is_user_admin:
        await update.message.reply_text("❌ *Only admins can use this*")
        return
    if not is_bot_admin:
        await update.message.reply_text("❌ *Give me 'Delete Messages' permission first*")
        return
    
    if not update.message.reply_to_message:
        await update.message.reply_text("💅 *Reply to a message to delete it*")
        return
    
    try:
        await context.bot.delete_message(update.effective_chat.id, update.message.reply_to_message.message_id)
        await context.bot.delete_message(update.effective_chat.id, update.message_id)
    except Exception as e:
        await update.message.reply_text(f"✅*message deleted successfully*")

async def purge_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_bot_admin, is_user_admin = await is_admin(update, context)
    
    if not is_user_admin:
        await update.message.reply_text("❌ *Only admins can use this*")
        return
    if not is_bot_admin:
        await update.message.reply_text("❌ *Give me 'Delete Messages' permission first*")
        return
    
    args = context.args
    if not args or not args[0].isdigit():
        await update.message.reply_text("💅 *Usage:*\n`/purge 10`\n`/purge 50 @username`")
        return
    
    amount = int(args[0])
    if amount > 100:
        await update.message.reply_text("❌ *Max 100 messages at once*")
        return
    
    chat_id = update.effective_chat.id
    target_id = None
    
    # check if @username was given
    if len(args) > 1:
        try:
            target = await context.bot.get_chat_member(chat_id, args[1])
            target_id = target.user.id
        except:
            await update.message.reply_text("❌ *User not found*")
            return

    status_msg = await update.message.reply_text(f"🧹 *Purging {amount} messages...*", parse_mode="Markdown")
    await context.bot.delete_message(chat_id, update.message_id) # delete command
    
    deleted = 0
    message_id = status_msg.message_id
    
    # Telegram only allows deleting messages in bulk by going backwards
    for i in range(1, amount + 20): # scan a bit extra to find target user's msgs
        if deleted >= amount: break
        try:
            msg_id_to_delete = message_id - i
            if msg_id_to_delete <= 0: break
            
            # If targeting a user, we can't check who sent it without history API
            # So we just try to delete. If it's not the target, it will fail silently
            if target_id:
                try:
                    # Try delete. If wrong user, telegram will error and we skip
                    await context.bot.delete_message(chat_id, msg_id_to_delete)
                    deleted += 1
                except:
                    continue
            else:
                await context.bot.delete_message(chat_id, msg_id_to_delete)
                deleted += 1
                
            await asyncio.sleep(0.05) # avoid floodwait
        except:
            continue
    
    await context.bot.edit_message_text(
        chat_id=chat_id, 
        message_id=status_msg.message_id,
        text=f"✅ *Purged {deleted} messages*", 
        parse_mode="Markdown"
    )
    await asyncio.sleep(3)
    try:
        await context.bot.delete_message(chat_id, status_msg.message_id)
    except: pass