"""
Voice helper: converts text to OGG OPUS bytes for Telegram voice notes.

Pipeline:
  gTTS (lang='en', slow=False) → MP3
  → pitch-shift down 4 semitones (male voice simulation via pydub)
  → OGG OPUS  (required for Telegram voice bubbles)

gTTS uses Google's TTS engine which is female by default. Lowering the
frame rate by 4 semitones shifts the fundamental frequency down ~20%,
producing a natural-sounding male voice without external ML models.
"""

import io
import logging

from gtts import gTTS
from pydub import AudioSegment

logger = logging.getLogger(__name__)

# Semitones to shift down for a male-sounding voice.
# 4 semitones ≈ multiplying frequency by 2^(-4/12) ≈ 0.794
_MALE_PITCH_SEMITONES = 2


def _pitch_shift_down(audio: AudioSegment, semitones: int) -> AudioSegment:
    """
    Lower pitch by `semitones` without external DSP libraries.

    Technique: resample to a lower virtual frame rate, then restore the
    original frame rate. This stretches the waveform in time *and* lowers
    the pitch. The slight speed reduction (~10 % for 2 semitones) makes
    the voice sound calm and deliberate — a good fit for a male assistant.
    """
    factor = 2 ** (-semitones / 12.0)
    new_frame_rate = int(audio.frame_rate * factor)
    shifted = audio._spawn(audio.raw_data, overrides={"frame_rate": new_frame_rate})
    # Restore original sample rate so the audio plays at correct speed in players
    return shifted.set_frame_rate(audio.frame_rate)


def text_to_voice(text: str) -> io.BytesIO:
    """
    Convert text to a male-pitched OGG OPUS BytesIO buffer.

    Returns:
        BytesIO positioned at 0, ready for bot.send_voice().
    """
    # 1. Generate speech (Google TTS → MP3)
    tts = gTTS(text=text, lang="en", slow=False)
    mp3_buf = io.BytesIO()
    tts.write_to_fp(mp3_buf)
    mp3_buf.seek(0)

    # 2. Load and pitch-shift to male voice
    audio = AudioSegment.from_mp3(mp3_buf)
    male_audio = _pitch_shift_down(audio, _MALE_PITCH_SEMITONES)

    # 3. Export as OGG OPUS (Telegram requires this for voice bubbles)
    ogg_buf = io.BytesIO()
    male_audio.export(ogg_buf, format="ogg", codec="libopus")
    ogg_buf.seek(0)

    logger.debug(
        "Voice note: %d chars → %d bytes OGG OPUS (pitch −%d st)",
        len(text), ogg_buf.getbuffer().nbytes, _MALE_PITCH_SEMITONES,
    )
    return ogg_buf
