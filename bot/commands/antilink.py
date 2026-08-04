from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ChatMemberStatus

from .antilinkdata import (
    set_mode,
    disable_antilink,
    get_mode,
    is_enabled
)


async def antilink(update: Update, context: ContextTypes.DEFAULT_TYPE):

    chat_id = update.effective_chat.id

    member = await context.bot.get_chat_member(
        chat_id,
        update.effective_user.id
    )

    if member.status not in [
        ChatMemberStatus.ADMINISTRATOR,
        ChatMemberStatus.OWNER
    ]:
        await update.message.reply_text(
            "❌ Only group admins can use Anti-Link settings."
        )
        return

    if not context.args:
        await update.message.reply_text(
            "🛡 MUFASER-X Anti-Link\n\n"
            "Commands:\n\n"
            "/antilink warn on\n"
            "/antilink warn off\n\n"
            "/antilink ban on\n"
            "/antilink ban off\n\n"
            "/antilink kick on\n"
            "/antilink kick off\n\n"
            "/antilink delete on\n"
            "/antilink delete off\n\n"
            "/antilink status\n\n"
            "Powered By MUFASER-X"
        )
        return


    mode = context.args[0].lower()


    # STATUS
    if mode == "status":

        if not is_enabled(chat_id):

            await update.message.reply_text(
                "🛡 MUFASER-X Anti-Link\n\n"
                "Status: OFF\n\n"
                "Powered By MUFASER-X"
            )

        else:

            current = get_mode(chat_id).upper()

            await update.message.reply_text(
                "🛡 MUFASER-X Anti-Link\n\n"
                "Status: ON\n\n"
                f"Current Mode:\n{current}\n\n"
                "Warnings: 3\n"
                "Punishment: 20 Minute Mute\n\n"
                "Powered By MUFASER-X"
            )

        return



    # NEED ON/OFF
    if len(context.args) < 2:

        await update.message.reply_text(
            "❌ Use:\n"
            "/antilink <mode> on/off"
        )
        return


    action = context.args[1].lower()


    if mode not in [
        "warn",
        "ban",
        "kick",
        "delete"
    ]:

        await update.message.reply_text(
            "❌ Invalid mode"
        )
        return



    if action == "on":

        old_mode = get_mode(chat_id)

        set_mode(chat_id, mode)


        if old_mode and old_mode != mode:

            await update.message.reply_text(
                "✅ Anti-Link Updated\n\n"
                f"❌ {old_mode.upper()} Disabled\n"
                f"✅ {mode.upper()} Enabled\n\n"
                "Powered By MUFASER-X"
            )

        else:

            await update.message.reply_text(
                "✅ Anti-Link Mode Enabled\n\n"
                f"Mode: {mode.upper()}\n\n"
                "Powered By MUFASER-X"
            )



    elif action == "off":

        if get_mode(chat_id) == mode:

            disable_antilink(chat_id)


        await update.message.reply_text(
            f"❌ {mode.upper()} Disabled\n\n"
            "Powered By MUFASER-X"
        )


    else:

        await update.message.reply_text(
            "❌ Use only ON or OFF"
        )