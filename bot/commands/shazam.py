import os
import uuid
import shutil
import tempfile
import subprocess
import requests

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes

AUDD_API_TOKEN = os.getenv("AUDD_API_TOKEN")

TEMP_DIR = tempfile.mkdtemp(prefix="shazam_")

def cleanup(path):
    try:
        if os.path.isfile(path):
            os.remove(path)
    except Exception:
        pass

def run_ffmpeg(input_file, output_file):
    command = [
        "ffmpeg",
        "-y",
        "-i",
        input_file,
        "-vn",
        "-acodec",
        "mp3",
        "-ar",
        "44100",
        "-ac",
        "2",
        "-b:a",
        "192k",
        output_file,
    ]

    process = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    return process.returncode == 0

async def download_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Downloads replied audio, voice or video.
    Returns local file path.
    """

    if not update.message.reply_to_message:
        await update.message.reply_text(
            "❌ Reply to a voice, audio or video with /shazam"
        )
        return None

    reply = update.message.reply_to_message

    media = None
    extension = ".dat"

    if reply.voice:
        media = reply.voice
        extension = ".ogg"

    elif reply.audio:
        media = reply.audio
        extension = ".mp3"

    elif reply.video:
        media = reply.video
        extension = ".mp4"

    elif reply.video_note:
        media = reply.video_note
        extension = ".mp4"

    else:
        await update.message.reply_text(
            "❌ Reply to a supported media file."
        )
        return None

    await context.bot.send_chat_action(
        update.effective_chat.id,
        ChatAction.UPLOAD_DOCUMENT,
    )

    file = await media.get_file()

    filename = os.path.join(
        TEMP_DIR,
        f"{uuid.uuid4()}{extension}"
    )

    await file.download_to_drive(filename)

    return filename

def prepare_audio(input_file):
    """
    Converts media into MP3 for AudD.
    """

    if input_file.endswith(".mp3"):
        return input_file

    output = input_file.rsplit(".", 1)[0] + ".mp3"

    success = run_ffmpeg(input_file, output)

    if not success:
        return None

    cleanup(input_file)

    return output

def recognize_song(audio_file):
    """
    Sends audio to AudD API.
    """

    url = "https://api.audd.io/"

    with open(audio_file, "rb") as song:

        response = requests.post(
            url,
            data={
                "api_token": AUDD_API_TOKEN,
                "return": "spotify,apple_music,deezer",
            },
            files={
                "file": song,
            },
            timeout=120,
        )

    return response.json()

async def shazam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not AUDD_API_TOKEN:
        await update.message.reply_text(
            "❌ API_TOKEN is missing from environment variables."
        )
        return

    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action=ChatAction.TYPING
    )

    media_file = await download_media(update, context)

    if not media_file:
        return

    audio_file = prepare_audio(media_file)

    if not audio_file:
        cleanup(media_file)
        await update.message.reply_text(
            "❌ Failed to process the audio."
        )
        return

    try:
        data = recognize_song(audio_file)

        if data.get("status")!= "success":
            await update.message.reply_text(
                "❌ Failed to contact the music recognition service."
            )
            return

        result = data.get("result")

        if not result:
         await update.message.reply_text(
        f"❌ No song found.\n\n response:\n{data}"
    )
         return

        title = result.get("title", "Unknown")
        artist = result.get("artist", "Unknown")
        album = result.get("album", "Unknown")
        release = result.get("release_date", "Unknown")
        genre = result.get("genre", "Unknown")

        spotify = ""
        apple = ""
        deezer = ""

        if result.get("spotify"):
            spotify = result["spotify"].get("external_urls", {}).get("spotify", "")

        if result.get("apple_music"):
            apple = result["apple_music"].get("url", "")

        if result.get("deezer"):
            deezer = result["deezer"].get("link", "")

        text = f"""🎵 <b>Song Identified</b>

🎶 <b>Title:</b> {title}

🎤 <b>Artist:</b> {artist}

💿 <b>Album:</b> {album}

📅 <b>Release:</b> {release}

🎼 <b>Genre:</b> {genre}
"""

        if spotify:
            text += f"\n🟢 <b>Spotify:</b>\n{spotify}\n"

        if apple:
            text += f"\n🍎 <b>Apple Music:</b>\n{apple}\n"

        if deezer:
            text += f"\n🎧 <b>Deezer:</b>\n{deezer}\n"

        text += "\n━━━━━━━━━━━━━━\n\nPowered By MUFASER-X"

        await update.message.reply_text(
            text,
            parse_mode="HTML",
            disable_web_page_preview=True
        )

    except Exception as e:
        await update.message.reply_text(
            f"❌ Error:\n<code>{e}</code>",
            parse_mode="HTML"
        )

    finally:
        cleanup(audio_file)