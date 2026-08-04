import os
import json
import time
import asyncio
import subprocess
import sys

OWNER_ID = 8369264435

UPDATE_FILE = "last_ytdlp_update.json"

# Check every 12 hours
CHECK_INTERVAL = 12 * 60 * 60


async def check_ytdlp_update(bot):
    now = int(time.time())

    # Read last check time
    if os.path.exists(UPDATE_FILE):
        try:
            with open(UPDATE_FILE, "r") as f:
                data = json.load(f)
                last_check = data.get("last_check", 0)
        except Exception:
            last_check = 0
    else:
        last_check = 0

    # Skip if 12 hours haven't passed
    if now - last_check < CHECK_INTERVAL:
        return

    try:
        process = await asyncio.create_subprocess_exec(
            sys.executable,
            "-m",
            "pip",
            "install",
            "-U",
            "yt-dlp",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        output = stdout.decode() + stderr.decode()

        if process.returncode == 0:
            if "Requirement already satisfied" in output:
                message = "ℹ️ yt-dlp is already up to date."
            else:
                message = "✅ yt-dlp updated successfully."
        else:
            message = f"❌ yt-dlp update failed.\n\n{output[:3500]}"

    except Exception as e:
        message = f"❌ yt-dlp update failed.\n\n{e}"

    # Save current check time
    with open(UPDATE_FILE, "w") as f:
        json.dump({"last_check": now}, f)

    # Notify owner
    try:
        await bot.send_message(
            chat_id=OWNER_ID,
            text=message
        )
    except Exception:
        pass