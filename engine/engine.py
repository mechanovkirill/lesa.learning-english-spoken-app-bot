import threading
import traceback
from queue import Queue
from engine.speech_recognition_ import speech_recognition_depending_set
from engine.request_openai import request_to_openai, send_msg_depending_user_settg
from engine.tts import tts_depending_user_settings
from engine.sending import send_via_bot

from io import BytesIO
from db import BotUserClass
from templates.messages import HAVENOT_RECOGNIZED_TEXT


import logging
logger = logging.getLogger(__name__)


hand_over_queue = Queue()


def engine() -> None:
    logger.info('Into engine')

    while True:
        # get data
        message__user_settings = hand_over_queue.get()

        user_settings: BotUserClass = message__user_settings[1]
        user_id: int = user_settings.telegram_id
        message: BytesIO | str = message__user_settings[0]

        #  check data
        if isinstance(message, BytesIO):
            #  recognition
            recognized_text = speech_recognition_depending_set(user_settings, message)
            if not recognized_text:
                send_via_bot(user_id, (HAVENOT_RECOGNIZED_TEXT,))
                continue
            logger.info('recognized_text passed')

            # request to and response from OpenAI API
            response_text = request_to_openai(
                _text=recognized_text, _user_settings=user_settings
            )
            logger.info('Got response')

            #  prepare answer text
            text_answer = send_msg_depending_user_settg(
                _user_settings=user_settings,
                _response_text=response_text,
                _recognized_text=recognized_text)

            # tts if it in settings
            tts_response = tts_depending_user_settings(_user_settings=user_settings, text=response_text)
            logger.info('TTS is passed')

            #  send
            send_via_bot(user_id, (text_answer, tts_response))

        if isinstance(message, str):
            # request to and response from OpenAI API
            response_text = request_to_openai(
                _text=message, _user_settings=user_settings
            )
            logger.info(f'Got response: {response_text}')

            #  prepare answer text
            text_answer = send_msg_depending_user_settg(
                _user_settings=user_settings,
                _response_text=response_text,
                _recognized_text=None)

            # tts if it in settings
            tts_response = tts_depending_user_settings(_user_settings=user_settings, text=response_text)
            logger.info('TTS is passed')

            #  send
            send_via_bot(user_id, (text_answer, tts_response))


def run_engine():
    while True:
        try:
            engine()
        except Exception:
            logger.error(f"engine() was stopped! {traceback.format_exc()}")


engine_thread = threading.Thread(target=run_engine, daemon=True, name='engine_thread').start()


def run_engine2():
    while True:
        try:
            engine()
        except Exception:
            logger.error(f"engine() was stopped! {traceback.format_exc()}")


engine_thread2 = threading.Thread(target=run_engine2, daemon=True, name='engine_thread2').start()


