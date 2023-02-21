from func_timeout import func_timeout, FunctionTimedOut
import speech_recognition as sr
from pydub import AudioSegment
from io import BytesIO

import logging

logger = logging.getLogger(__name__)


def take_and_convert_to_wav(ogg_file: BytesIO) -> BytesIO:
    """convert ogg audio stream to"""
    voice_data = AudioSegment.from_file(ogg_file)
    wav_voice = BytesIO()
    voice_data.export(out_f=wav_voice, format="wav")
    wav_voice.seek(0)
    return wav_voice


def speech_recognition(speech: BytesIO) -> str:
    """Receive a BytesIO audio and return recognition text or raise FunctionTimedOut exception"""
    # Initialize recognizer class (for recognizing the speech)
    r = sr.Recognizer()
    with sr.AudioFile(speech) as source:
        audio_text = r.record(source)
    logger.info('Converted to flac')

    # using google speech recognition
    def recognition(audio, recognizer):
        text = recognizer.recognize_google(audio_data=audio)
        logger.info(f"Speech Recognition Text: {text}")
        return text

    recognized_text = None
    try:
        recognized_text = func_timeout(timeout=20, func=recognition, kwargs=dict(audio=audio_text, recognizer=r))
        return recognized_text
    except FunctionTimedOut:
        logger.warning('The recognition timeout')
    except sr.UnknownValueError:
        logger.warning("Speech recognition failed")

    return recognized_text

