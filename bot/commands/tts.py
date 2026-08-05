from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes

from gtts import gTTS
from pydub import AudioSegment

import io

# ==============================
# MUFASER-X Text To Speech
# ==============================

_MALE_PITCH_SEMITONES = 2

def _pitch_shift_down(audio: AudioSegment, semitones: int) -> AudioSegment:
    factor = 2 ** (-semitones / 12)
    new_frame_rate = int(audio.frame_rate * factor)
    shifted = audio._spawn(audio.raw_data, overrides={"frame_rate": new_frame_rate})
    return shifted.set_frame_rate(audio.frame_rate)

async def tts(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # Get text
    if update.message.reply_to_message and update.message.reply_to_message.text:
        text = update.message.reply_to_message.text
    elif context.args:
        text = " ".join(context.args)
    else:
        await update.message.reply_text(
            """
🎙️ <b>Text To Speech</b>

<b>Usage:</b>

• <code>/tts Hello World</code>

OR

• Reply to any text with:

<code>/tts</code>

━━━━━━━━━━━━━━
Male English
━━━━━━━━━━━━━━
Powered By MUFASER-X
""",
            parse_mode="HTML"
        )
        return

    if not text.strip():
        await update.message.reply_text("❌ Please provide some text.")
        return

    generating_msg = None # to store the message so we can delete it
    try:
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.RECORD_VOICE)

        # 1. Send "Generating..." and save the message object
        generating_msg = await update.message.reply_text("🎙️ Generating your voice...\n")

        # Generate MP3
        tts_engine = gTTS(text=text, lang="en", slow=False)
        mp3_buffer = io.BytesIO()
        tts_engine.write_to_fp(mp3_buffer)
        mp3_buffer.seek(0)

        # Convert to male voice
        audio = AudioSegment.from_mp3(mp3_buffer)
        male_voice = _pitch_shift_down(audio, _MALE_PITCH_SEMITONES)

        # Export Telegram voice
        ogg_buffer = io.BytesIO()
        male_voice.export(ogg_buffer, format="ogg", codec="libopus")
        ogg_buffer.seek(0)

        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_VOICE)

        # 2. Send the voice
        await update.message.reply_voice(
            voice=ogg_buffer,
            caption="""

━━━━━━━━━━━━━━
Powered By MUFASER-X
"""
        )
        
        # 3. Delete the "Generating..." message
        if generating_msg:
            await generating_msg.delete()

    except Exception as e:
        # If error, also delete generating msg and show error
        if generating_msg:
            await generating_msg.delete()
        await update.message.reply_text(f"❌ <b>Voice Generation Failed</b>\n\n<code>{e}</code>", parse_mode="HTML")