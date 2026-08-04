import asyncio
from telegram import Message


async def progress_message(
    message: Message,
    text: str,
    delay: float = 0.4
):
    """
    Updates a Telegram message safely.
    """

    try:
        await asyncio.sleep(delay)
        await message.edit_text(text)

    except Exception:
        pass


async def upload_animation(message: Message):
    """
    Nice uploading animation.
    """

    frames = [
        "📤 Uploading.",
        "📤 Uploading..",
        "📤 Uploading...",
        "📤 Uploading...."
    ]

    try:
        for frame in frames:
            await message.edit_text(frame)
            await asyncio.sleep(0.35)

    except Exception:
        pass


async def download_animation(message: Message):
    """
    Nice downloading animation.
    """

    frames = [
        "📥 Downloading.",
        "📥 Downloading..",
        "📥 Downloading...",
        "📥 Downloading...."
    ]

    try:
        for frame in frames:
            await message.edit_text(frame)
            await asyncio.sleep(0.35)

    except Exception:
        pass


async def search_animation(message: Message):
    """
    Searching animation.
    """

    frames = [
        "🔎 Searching.",
        "🔎 Searching..",
        "🔎 Searching...",
        "🔎 Searching...."
    ]

    try:
        for frame in frames:
            await message.edit_text(frame)
            await asyncio.sleep(0.35)

    except Exception:
        pass