"""
Lightweight Flask health server.
Runs in a background daemon thread alongside the Telegram bot.
External uptime monitors (e.g. UptimeRobot) ping / or /health to prevent
the process from sleeping.
"""

import logging
import os
import threading

from flask import Flask, jsonify

logger = logging.getLogger(__name__)

app = Flask(__name__)

_start_time: float = 0.0


@app.route("/")
def home():
    return jsonify({"status": "ok", "service": "telegram-bot"})


@app.route("/health")
def health():
    import time

    uptime = round(time.time() - _start_time, 1) if _start_time else 0
    return jsonify({"status": "healthy", "uptime_seconds": uptime})


def start_server() -> None:
    """Start Flask in a daemon thread so it does not block the bot."""
    global _start_time
    import time

    _start_time = time.time()

    port = int(os.environ.get("PORT", 8000))

    thread = threading.Thread(
        target=lambda: app.run(host="0.0.0.0", port=port, use_reloader=False),
        daemon=True,
        name="flask-health-server",
    )
    thread.start()
    logger.info("Health server started on port %d", port)
    