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


def take_and_convert_to_wav(ogg_file: BytesIO) -> BytesIO:
    """convert ogg audio stream to"""
    voice_data = AudioSegment.from_file(ogg_file)
    wav_voice = BytesIO()
    voice_data.export(out_f=wav_voice, format="wav")
    wav_voice.seek(0)
    return wav_voice


def speech_recognition(speech: BytesIO) -> str:
    # Initialize recognizer class (for recognizing the speech)
    r = sr.Recognizer()
    with sr.AudioFile(speech) as source:
        audio_text = r.record(source)
    logger.info('Converted to flac')

    # using google speech recognition
    def recognition(audio):
        text = r.recognize_google(audio_data=audio)
        logger.info(f"Speech Recognition Text: {text}")
        return text

    try:
        text = func_timeout(timeout=5, func=recognition, kwargs=dict(audio=audio_text))
    except FunctionTimedOut:
        return audio_text
    if audio_text:
        try:
            text = func_timeout(timeout=7, func=recognition, kwargs=dict(audio=audio_text))
        except FunctionTimedOut:
            text = ""

    return text


def request_to_openai(_text: str, user_settings: tuple[BytesIO, BotUserClass]) -> str:
    openai_endpoint = "https://api.openai.com/v1/completions"

    mode = None
    if user_settings[1].mode == 1:
        print(user_settings[1].mode)
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
    response = requests.post(openai_endpoint, headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {user_settings[1].api_key}"
    }, json=mode, timeout=5)

    # Get the response from the OpenAI API
    try:
        response_text = response.json()["choices"][0]["text"]
    except:
        if response.json():
            response_text = response.json()
            return f'Unable to recognize text, server response: {response_text}'
        response_text = "Sorry, no response received."

    print("OpenAI API Response:", response_text)

    return response_text


def text_to_speech_coqui(text_: str) -> BytesIO:
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

    outputs = syn.tts(text_)
    answer = BytesIO()
    syn.save_wav(outputs, answer)
    return answer


def text_to_speech_google(text_: str) -> BytesIO:
    # Initialize gTTS
    answer = BytesIO()
    print('into gtts')
    gTTS(text=text_, lang='en').write_to_fp(answer)
    print('pass gtts')
    answer.seek(0)
    return answer


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


def voice_engine() -> None:
    logger.info('Into engine')
    logger.info(f'{threading.active_count()}')
    logger.info(f'{threading.current_thread()}')

    while True:
        message__user_settings = hand_over_queue.get()

        user_id: int = message__user_settings[1].telegram_id

        if isinstance(message__user_settings[0], BytesIO):
            wav_voice = take_and_convert_to_wav(message__user_settings[0])
            logger.info('Converting to wav passed')

            recognized_text = speech_recognition(wav_voice)
            logger.info('recognized_text passed')

            response_text = request_to_openai(
                _text="Hi, DaVinchi! Say anything for test my program.", user_settings=message__user_settings
            )
            logger.info('Got response')

            tts_response = text_to_speech_coqui(response_text)
            # tts_response = text_to_speech_google(response_text)
            logger.info('TTS is passed')

            answer_text = f'You:\n  {recognized_text}\n\nLESA:{response_text}'
            send_text_msg(text=answer_text, chat_id=user_id)

            async def bot():
                bot = telegram.Bot(TELEGRAM_BOT_TOKEN)
                async with bot:
                    await bot.send_voice(chat_id=user_id, voice=tts_response)

            asyncio.run(bot())


thread_engine = threading.Thread(target=voice_engine, daemon=True).start()
