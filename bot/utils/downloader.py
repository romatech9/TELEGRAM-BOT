import os
import math
import yt_dlp
import requests


def format_size(size):
    """Convert bytes to KB/MB/GB"""

    if size is None:
        return "Unknown"

    power = 1024
    units = ["B", "KB", "MB", "GB", "TB"]

    n = 0

    while size > power:
        size /= power
        n += 1

    return f"{size:.2f} {units[n]}"


def format_duration(seconds):
    """Convert seconds to HH:MM:SS"""

    if seconds is None:
        return "Unknown"

    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60

    if h:
        return f"{h}:{m:02}:{s:02}"

    return f"{m}:{s:02}"


def search_and_download_song(query, download_folder):

    os.makedirs(download_folder, exist_ok=True)

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": f"{download_folder}/%(title)s.%(ext)s",
        "noplaylist": True,
        "quiet": True,
        "default_search": "ytsearch1",
        "writethumbnail": False,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:

        info = ydl.extract_info(query, download=True)

        if "entries" in info:
            info = info["entries"][0]

        title = info.get("title", "Unknown Song")

        artist = info.get(
            "uploader",
            "Unknown Artist"
        )

        duration = info.get("duration", 0)

        thumbnail_url = info.get("thumbnail")

        audio_path = os.path.join(
            download_folder,
            f"{title}.mp3"
        )

        thumbnail_path = os.path.join(
            download_folder,
            f"{title}.jpg"
        )

        if thumbnail_url:
            response = requests.get(
                thumbnail_url,
                timeout=30
            )

            with open(thumbnail_path, "wb") as img:
                img.write(response.content)

        size = (
            format_size(
                os.path.getsize(audio_path)
            )
            if os.path.exists(audio_path)
            else "Unknown"
        )

        return {
            "title": title,
            "artist": artist,
            "duration": duration,
            "audio": audio_path,
            "thumbnail": thumbnail_path,
            "size": size,
        }