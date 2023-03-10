from func_timeout import func_timeout, FunctionTimedOut

from TTS.utils.manage import ModelManager
from TTS.utils.synthesizer import Synthesizer
from gtts import gTTS
from io import BytesIO
from db import BotUserClass
from config import PATH_TO_TTS_MODEL

import logging
import traceback
logger = logging.getLogger(__name__)


def text_to_speech_coqui(text: str) -> BytesIO:
    path = PATH_TO_TTS_MODEL
    model_manager = ModelManager(path)
    model_path, config_path, model_item = model_manager.download_model("tts_models/en/ljspeech/tacotron2-DDC")
    voc_path, voc_config_path, _ = model_manager.download_model(model_item["default_vocoder"])

    syn = Synthesizer(
        tts_checkpoint=model_path,
        tts_config_path=config_path,
        vocoder_checkpoint=voc_path,
        vocoder_config=voc_config_path
    )

    outputs = syn.tts(text)
    answer = BytesIO()
    syn.save_wav(outputs, answer)
    return answer


def text_to_speech_google(text: str) -> BytesIO:
    answer = BytesIO()
    print('into gtts')
    gTTS(text=text, lang='en').write_to_fp(answer)
    print('pass gtts')
    answer.seek(0)
    return answer


def tts_depending_user_settings(_user_settings: BotUserClass, text: str) -> BytesIO | str | None:
    if _user_settings.tts_engine == 1:
        tts_response = None
        try:
            tts_response = func_timeout(14, text_to_speech_google, kwargs=dict(text=text))
            return tts_response
        except FunctionTimedOut:
            pass
        except AssertionError:
            pass
        if not tts_response:
            try:
                tts_response = func_timeout(15, text_to_speech_coqui, kwargs=dict(text=text))
                return tts_response
            except FunctionTimedOut:
                tts_response = "The text-to-speech request timed out. Failed to convert text to speech."
                logger.warning('option 1 text_to_speech_coqui first time out!')
                return tts_response
            except Exception:
                tts_response = "Failed to convert text to speech."
                logger.warning(f'option 1 text_to_speech_coqui the second time out! {traceback.format_exc()}')
                return tts_response

    elif _user_settings.tts_engine == 2:
        tts_response = None
        try:
            tts_response = func_timeout(14, text_to_speech_coqui, kwargs=dict(text=text))
            return tts_response
        except FunctionTimedOut:
            pass
        if not tts_response:
            try:
                tts_response = func_timeout(14, text_to_speech_google, kwargs=dict(text=text))
                return tts_response
            except FunctionTimedOut:
                tts_response = "The text-to-speech request timed out. Failed to convert."
                logger.warning('option 3 text_to_speech_coqui first time out!')
                return tts_response
            except AssertionError:
                logger.warning('text_to_speech_google. No text to speak.')
                return tts_response

    elif _user_settings.tts_engine == 3:
        tts_response = None
        try:
            print(text)
            tts_response = func_timeout(14, text_to_speech_coqui, kwargs=dict(text=text))
            return tts_response
        except FunctionTimedOut:
            pass
        except Exception:
            pass
        if not tts_response:
            try:
                tts_response = func_timeout(14, text_to_speech_coqui, kwargs=dict(text=text))
                return tts_response
            except FunctionTimedOut:
                tts_response = "The text-to-speech request timed out. Failed to convert."
                logger.warning('text_to_speech_coqui second time out!')
                return tts_response
            except Exception:
                tts_response = "The text-to-speech request timed out. Failed to convert."
                logger.warning(f'option 3 text_to_speech_coqui the second time out! {traceback.format_exc()}')
                return tts_response

    elif _user_settings.tts_engine == 4:
        tts_response = None
        try:
            tts_response = func_timeout(14, text_to_speech_google, kwargs=dict(text=text))
            return tts_response
        except FunctionTimedOut:
            logger.warning('text_to_speech_google first time out!')
        except AssertionError:
            logger.warning('text_to_speech_google. No text to speak.')
            return tts_response
        if not tts_response:
            try:
                tts_response = func_timeout(14, text_to_speech_google, kwargs=dict(text=text))
                return tts_response
            except FunctionTimedOut:
                tts_response = "The text-to-speech request timed out. Failed to convert."
                logger.warning('text_to_speech_google second time out!')
                return tts_response
            except AssertionError:
                logger.warning('text_to_speech_google. No text to speak.')
                return tts_response

    else:
        tts_response = None
        return tts_response


