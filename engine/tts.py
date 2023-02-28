from func_timeout import func_timeout, FunctionTimedOut

from gtts import gTTS
from io import BytesIO
from db import BotUserClass

import logging
import traceback
logger = logging.getLogger(__name__)


def text_to_speech_google(text: str) -> BytesIO:
    answer = BytesIO()
    print('into gtts')
    gTTS(text=text, lang='en').write_to_fp(answer)
    print('pass gtts')
    answer.seek(0)
    return answer


def tts_depending_user_settings(_user_settings: BotUserClass, text: str) -> BytesIO | str | None:
    if _user_settings.tts_engine == 0:
        return
    else:
        timeout = _user_settings.tts_engine
        try:
            tts_response = func_timeout(timeout, text_to_speech_google, kwargs=dict(text=text))
            return tts_response
        except FunctionTimedOut:
            tts_response = f"The text-to-speech request timed out. Failed to convert text to speech. " \
                           f"You have set the time to wait for a response {timeout} - seconds."
            return tts_response
        except AssertionError:
            tts_response = "Failed to convert text to speech."
            logger.warning(f'option 1 text_to_speech_coqui the second time out! {traceback.format_exc()}')
            return tts_response
        except Exception:
            tts_response = "Failed to convert text to speech."
            logger.warning(f'option 1 text_to_speech_coqui the second time out! {traceback.format_exc()}')
            return tts_response




