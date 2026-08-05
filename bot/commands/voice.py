import io
import logging

from gtts import gTTS
from pydub import AudioSegment


logger = logging.getLogger(__name__)


_MALE_PITCH_SEMITONES = 3


def pitch_shift(audio, semitones):

    factor = 2 ** (-semitones / 12)

    new_rate = int(
        audio.frame_rate * factor
    )

    shifted = audio._spawn(
        audio.raw_data,
        overrides={
            "frame_rate": new_rate
        }
    )

    return shifted.set_frame_rate(
        audio.frame_rate
    )


def text_to_voice(text):

    tts = gTTS(
        text=text,
        lang="en",
        slow=False
    )


    mp3 = io.BytesIO()

    tts.write_to_fp(mp3)

    mp3.seek(0)


    audio = AudioSegment.from_mp3(
        mp3
    )


    audio = pitch_shift(
        audio,
        _MALE_PITCH_SEMITONES
    )


    ogg = io.BytesIO()


    audio.export(
        ogg,
        format="ogg",
        codec="libopus"
    )


    ogg.seek(0)

    return ogg