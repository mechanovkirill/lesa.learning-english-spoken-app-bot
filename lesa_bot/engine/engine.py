import asyncio
import threading
import time
from queue import Queue

import telegram
from func_timeout import func_timeout, FunctionTimedOut

import requests
import speech_recognition as sr
from pydub import AudioSegment
from TTS.utils.manage import ModelManager
from TTS.utils.synthesizer import Synthesizer
from gtts import gTTS
from io import BytesIO
from lesa_bot.db import BotUserClass
from lesa_bot.config import TELEGRAM_BOT_TOKEN

import logging

logger = logging.getLogger(__name__)


#  -------------------------------------------------------------------------------------------------------------------
def take_and_convert_to_wav(ogg_file: BytesIO) -> BytesIO:
    """convert ogg audio stream to"""
    voice_data = AudioSegment.from_file(ogg_file)
    wav_voice = BytesIO()
    voice_data.export(out_f=wav_voice, format="wav")
    wav_voice.seek(0)
    return wav_voice


#  -------------------------------------------------------------------------------------------------------------------
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

    return recognized_text


#  -------------------------------------------------------------------------------------------------------------------
def request_to_openai(_text: str, _user_settings: BotUserClass) -> str:
    """Send text to API and return response"""
    openai_endpoint = "https://api.openai.com/v1/completions"

    mode = None
    if _user_settings.mode == 1:
        print(_user_settings.mode)
        mode = {
            "model": "text-davinci-003",
            "prompt": "This message will consist of 3 texts."
                      f"1. {_text} "
                      "2. What mistakes are made in the text 1? "
                      "3. If text 1 does not contain a question"
                      "ask a question to keep the conversation going."
                      "Don't repeat numbers and instructions",
            "max_tokens": 100,
            "temperature": 0.7,
        }
    else:
        mode = {
            "model": "text-davinci-003",
            "prompt": f"{_text}",
            "max_tokens": 100,
            "temperature": 0.7,
        }

    # Send the text to the OpenAI API
    try:
        response = requests.post(openai_endpoint, headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {_user_settings.api_key}"
        }, json=mode, timeout=12)
    except FunctionTimedOut:
        response_text = ''
        return response_text

    # Get the response from the OpenAI API
    try:
        response_text = response.json()["choices"][0]["text"]
        return response_text
    except:
        logger.warning("No response from OpenAI")
        if response.json():
            response_text = response.json()
            return f'Unable to recognize text, server response: {response_text}'
        response_text = "Sorry, no response received. Make sure you have a valid OpenAI API key."

    logger.info(f"OpenAI API Response: {response_text}")

    return response_text


def send_msg_depending_user_settg(
        _user_settings: BotUserClass, _recognized_text: str | None, _response_text: str
) -> str | None:
    answer_text = None
    if _recognized_text:
        if _user_settings.show_text == 1:
            answer_text = f'You:\n  {_recognized_text}\n\nLESA:{_response_text}'
            return answer_text
            # send_text_msg(text=answer_text, chat_id=_user_settings.telegram_id)
        elif _user_settings.show_text == 2:
            answer_text = f'LESA:{_response_text}'
            return answer_text
            # send_text_msg(text=answer_text, chat_id=_user_settings.telegram_id)
        elif _user_settings.show_text == 3:
            answer_text = f'You:\n  {_recognized_text}'
            return answer_text
            # send_text_msg(text=answer_text, chat_id=_user_settings.telegram_id)
        else:
            return answer_text
    else:
        if _user_settings.show_text != 0:
            answer_text = f'LESA:{_response_text}'
            return answer_text
            # send_text_msg(text=answer_text, chat_id=_user_settings.telegram_id)
        else:
            return answer_text


#  -------------------------------------------------------------------------------------------------------------------
def text_to_speech_coqui(text: str) -> BytesIO:
    path = "/home/certo/lesa/venv/lib/python3.10/site-packages/TTS/.models.json"
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


def tts_depending_user_settings(_user_settings: BotUserClass, text: str) -> BytesIO | None:
    if _user_settings.tts_engine == 1:
        tts_response = None
        try:
            print(text)
            tts_response = func_timeout(12, text_to_speech_coqui, kwargs=dict(text=text))
            return tts_response
        except FunctionTimedOut:
            logger.info('text_to_speech_coqui first time out!')
        if not tts_response:
            try:
                tts_response = func_timeout(10, text_to_speech_coqui, kwargs=dict(text=text))
                return tts_response
            except FunctionTimedOut:
                logger.info('text_to_speech_coqui second time out!')
                return tts_response

    elif _user_settings.tts_engine == 2:
        tts_response = None
        try:
            tts_response = func_timeout(10, text_to_speech_google, kwargs=dict(text=text))
            return tts_response
        except FunctionTimedOut:
            logger.info('text_to_speech_google first time out!')
        if not tts_response:
            try:
                tts_response = func_timeout(10, text_to_speech_google, kwargs=dict(text=text))
                return tts_response
            except FunctionTimedOut:
                logger.info('text_to_speech_google second time out!')
                return tts_response

    elif _user_settings.tts_engine == 3:
        tts_response = None
        try:
            tts_response = func_timeout(12, text_to_speech_coqui, kwargs=dict(text=text))
            return tts_response
        except FunctionTimedOut:
            logger.info('option 3 text_to_speech_coqui time out!')
        if not tts_response:
            try:
                tts_response = func_timeout(10, text_to_speech_google, kwargs=dict(text=text))
                return tts_response
            except FunctionTimedOut:
                logger.info('option 3 text_to_speech_coqui first time out!')
                return tts_response

    elif _user_settings.tts_engine == 4:
        tts_response = None
        try:
            tts_response = func_timeout(10, text_to_speech_google, kwargs=dict(text=text))
            return tts_response
        except FunctionTimedOut:
            logger.info('option 3 text_to_speech_coqui time out!')
        if not tts_response:
            try:
                tts_response = func_timeout(12, text_to_speech_coqui, kwargs=dict(text=text))
                return tts_response
            except FunctionTimedOut:
                logger.info('option 3 text_to_speech_coqui first time out!')
                return tts_response

    else:
        tts_response = None
        return tts_response


#  messages----------------------------------------------------------------------------------------------------------
def send_text_msg(chat_id: int, text: str) -> None:
    strt = time.monotonic()
    token = TELEGRAM_BOT_TOKEN
    url = "https://api.telegram.org/bot" + token + "/sendMessage" + "?chat_id=" + str(chat_id) + "&text=" + text
    try:
        response = requests.get(url, timeout=5)
        logger.info(f'Sent for {time.monotonic() - strt}')
    except requests.exceptions.HTTPError as err:
        print('Error fetching response using requests')


def send_voice_msg(chat_id: int, voice_file: BytesIO) -> None:
    token = TELEGRAM_BOT_TOKEN
    url = "https://api.telegram.org/bot" + token + "/sendVoice" + "?chat_id=" + str(chat_id) + "&voice="
    file = {'voice': ('voice.ogg', voice_file)}
    try:
        post = requests.post(url, files=file, timeout=3)
        logger.info(f'voice message status code is {post.status_code}')
    except requests.exceptions.HTTPError as err:
        logger.warning('Error fetching response using requests')


hand_over_queue = Queue()


def engine() -> None:
    logger.info('Into engine')

    while True:
        # get data
        message__user_settings = hand_over_queue.get()

        user_settings: BotUserClass = message__user_settings[1]
        user_id: int = user_settings.telegram_id
        message: BytesIO | str = message__user_settings[0]

        if isinstance(message, BytesIO):
            wav_voice = take_and_convert_to_wav(message)
            logger.info('Converting to wav passed')

            # recognition
            recognized_text = speech_recognition(wav_voice)
            if not recognized_text:
                send_text_msg(chat_id=user_id, text="Sorry, the speech recognition service could not recognize your "
                                                    "speech or did not respond for a long time and recognition "
                                                    "was stopped. Try again."
                              )
                continue
            logger.info('recognized_text passed')

            # request to and response from OpenAI API
            response_text = request_to_openai(
                _text=recognized_text, _user_settings=user_settings
            )
            logger.info('Got response')

            text_answer = send_msg_depending_user_settg(
                _user_settings=user_settings,
                _response_text=response_text,
                _recognized_text=recognized_text)

            # tts if it in settings
            tts_response = tts_depending_user_settings(_user_settings=user_settings, text=response_text)
            logger.info('TTS is passed')

            start_t = time.monotonic()

            async def bot():
                bot = telegram.Bot(TELEGRAM_BOT_TOKEN)
                async with bot:
                    if text_answer:
                        await bot.send_message(chat_id=user_id, text=text_answer)
                    if tts_response:
                        await bot.send_voice(chat_id=user_id, voice=tts_response)

            asyncio.run(bot())
            logger.info(f'Sent by bot at {time.monotonic() - start_t}')

        if isinstance(message, str):
            # request to and response from OpenAI API
            response_text = request_to_openai(
                _text=message, _user_settings=user_settings
            )
            logger.info(f'Got response: {response_text}')

            # send text if it in settings
            text_answer = send_msg_depending_user_settg(
                _user_settings=user_settings,
                _response_text=response_text,
                _recognized_text=None)

            # tts if it in settings
            tts_response = tts_depending_user_settings(_user_settings=user_settings, text=response_text)
            logger.info('TTS is passed')

            start_t = time.monotonic()

            async def bot():
                bot = telegram.Bot(TELEGRAM_BOT_TOKEN)
                async with bot:
                    if text_answer:
                        await bot.send_message(chat_id=user_id, text=text_answer)
                    if tts_response:
                        await bot.send_voice(chat_id=user_id, voice=tts_response)

            asyncio.run(bot())
            logger.info(f'Sent by bot at {time.monotonic() - start_t}')


# def run_engine():
#     while True:
#         try:
#             engine()
#         except:
#             time.sleep(1)


engine_thread = threading.Thread(target=engine, daemon=True, name='engine_thread').start()
