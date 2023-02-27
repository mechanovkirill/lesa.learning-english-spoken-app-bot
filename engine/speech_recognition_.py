import traceback
from func_timeout import func_timeout, FunctionTimedOut
import speech_recognition as sr
from pydub import AudioSegment
from io import BytesIO
from vosk import Model, KaldiRecognizer
import wave
import soundfile as sf
import json
from db import BotUserClass
from config import PATH_TO_VOSK_MODEL

import logging

logger = logging.getLogger(__name__)


def pydub_ogg_convert_to_wav(ogg_file: BytesIO) -> BytesIO:
    """convert ogg audio stream to"""
    voice_data = AudioSegment.from_file(ogg_file)
    wav_voice = BytesIO()
    voice_data.set_channels(1).export(out_f=wav_voice, format="wav")
    wav_voice.seek(0)
    return wav_voice


def speech_recognition_google(speech: BytesIO) -> str:
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
        recognized_text = func_timeout(timeout=15, func=recognition, kwargs=dict(audio=audio_text, recognizer=r))
        return recognized_text
    except FunctionTimedOut:
        logger.warning('The recognition timeout')
    except sr.UnknownValueError:
        logger.warning(f"Speech recognition failed{traceback.format_exc()}")
    except Exception:
        logger.warning(f'Speech recognition failed{traceback.format_exc()}')

    return recognized_text


def sf_ogg_convert_to_wav(speech: BytesIO) -> BytesIO:
    audio_data, sample_rate = sf.read(speech)

    # # Convert audio data to mono if necessary
    # if len(audio_data.shape) > 1 and audio_data.shape[1] > 1:
    #     audio_data = audio_data[:, 0]

    wav_bytesio = BytesIO()

    sf.write(wav_bytesio, audio_data, sample_rate, format='wav', subtype='PCM_16', endian='little')
    wav_bytesio.seek(0)

    return wav_bytesio


def speech_recognition_vosk(speech: BytesIO) -> str | None:
    wf = wave.open(speech)
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
        logger.warning(F"Audio file must be WAV format mono PCM. SoundFile")
        return

    model = Model(f'{PATH_TO_VOSK_MODEL}')
    rec = KaldiRecognizer(model, 48000)
    rec.SetMaxAlternatives(10)
    rec.SetWords(True)

    while True:
        data = wf.readframes(12000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            pass

    result = json.loads(rec.FinalResult())
    text = result['alternatives'][0]['text']

    return text


def convert(_voice):
    try:
        res = sf_ogg_convert_to_wav(_voice)
        logger.info('pass sf converting')
        return res
    except Exception:
        try:
            _voice.seek(0)
            f = pydub_ogg_convert_to_wav(_voice)
            res = sf_ogg_convert_to_wav(f)
            logger.info('pass duble converting:(')
            return res
        except Exception:
            logger.warning(f'convert filed{traceback.format_exc()}')


def speech_recognition_depending_set(_user_settings: BotUserClass, voice: BytesIO) -> str | None:
    recognized_text = None
    if _user_settings.stt_engine == 1:
        audio = convert(voice)
        try:
            recognized_text = speech_recognition_vosk(audio)
            return recognized_text
        except Exception:
            logger.warning(f'Speech recognition failed{traceback.format_exc()}')
            return

    elif _user_settings.stt_engine == 0:
        audio = pydub_ogg_convert_to_wav(voice)

        recognized_text = speech_recognition_google(audio)

        if not recognized_text:
            voice.seek(0)
            audio = convert(voice)
            try:
                recognized_text = speech_recognition_vosk(audio)
                return recognized_text
            except Exception:
                logger.warning(f'Speech recognition failed{traceback.format_exc()}')
                return

        return recognized_text

    elif _user_settings.stt_engine == 2:
        audio = convert(voice)
        try:
            recognized_text = speech_recognition_vosk(audio)
            return recognized_text
        except Exception:
            logger.warning(f'Speech recognition failed{traceback.format_exc()}')
            if not recognized_text:
                audio.seek(0)
                recognized_text = speech_recognition_google(audio)
                return recognized_text













