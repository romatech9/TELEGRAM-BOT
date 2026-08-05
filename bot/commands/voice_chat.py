import os
import requests
import speech_recognition as sr

from pydub import AudioSegment

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes

from voice import text_to_voice


API_URL = "https://prexzyapis.com/ai/aichat"


SYSTEM_PROMPT = """
You are MUFASER-X.

You were created by ROMA-TECH from Uganda.

If someone asks who created you:
"I was created by ROMA-TECH, a developer from Uganda."

Your name is MUFASER-X.

You are a friendly AI assistant.

Rules:
- Do not start replies with MUFASER-X:
- Do not say you are ChatGPT.
- Reply naturally.
- Be helpful.
- Use emojis when suitable.
"""


async def voice_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message or not update.message.voice:
        return


    chat_id = update.effective_chat.id

    status = await update.message.reply_text(
        "🎤 Listening to your voice..."
    )


    ogg_file = f"voice_{chat_id}.ogg"
    wav_file = f"voice_{chat_id}.wav"


    try:

        await context.bot.send_chat_action(
            chat_id=chat_id,
            action=ChatAction.RECORD_VOICE
        )


        # Download Telegram voice note

        voice = await update.message.voice.get_file()

        await voice.download_to_drive(
            ogg_file
        )


        # Convert OGG to WAV

        audio = AudioSegment.from_file(
            ogg_file,
            format="ogg"
        )

        audio.export(
            wav_file,
            format="wav"
        )


        # Speech to text

        recognizer = sr.Recognizer()


        with sr.AudioFile(wav_file) as source:

            recorded_audio = recognizer.record(source)


        text = recognizer.recognize_google(
            recorded_audio,
            language="en-US"
        )


        await status.edit_text(
            "🤖 Thinking..."
        )


        # Ask AI

        prompt = f"""
{SYSTEM_PROMPT}

User voice message:
{text}

Answer:
"""


        await context.bot.send_chat_action(
            chat_id=chat_id,
            action=ChatAction.TYPING
        )


        response = requests.get(
            API_URL,
            params={
                "prompt": prompt
            },
            timeout=60
        )


        data = response.json()


        if not data.get("status"):

            await status.edit_text(
                "❌ AI service error."
            )
            return



        reply = data.get(
            "response",
            "I don't know how to answer."
        ).strip()



        # Remove unwanted AI labels

        for prefix in [
            "MUFASER-X:",
            "Assistant:",
            "AI:",
            "Bot:"
        ]:

            if reply.startswith(prefix):

                reply = reply[len(prefix):].strip()



        # Send text reply

        await status.delete()

        await update.message.reply_text(
            reply
        )


        # Send voice reply

        await context.bot.send_chat_action(
            chat_id=chat_id,
            action=ChatAction.RECORD_VOICE
        )


        voice_reply = text_to_voice(
            reply
        )


        await context.bot.send_voice(
            chat_id=chat_id,
            voice=voice_reply
        )


    except sr.UnknownValueError:

        await status.edit_text(
            "❌ I could not understand your voice."
        )


    except Exception as e:

        await status.edit_text(
            f"❌ Error: {e}"
        )


    finally:

        # Delete temporary files

        for file in [
            ogg_file,
            wav_file
        ]:

            if os.path.exists(file):

                os.remove(file)