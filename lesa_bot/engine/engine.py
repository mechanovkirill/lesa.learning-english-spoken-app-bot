import asyncio
import threading
import time
from queue import Queue
from func_timeout import func_timeout, FunctionTimedOut

import requests
import speech_recognition as sr
from pydub import AudioSegment
from TTS.utils.manage import ModelManager
from TTS.utils.synthesizer import Synthesizer
from gtts import gTTS
from io import BytesIO
from lesa_bot.db import BotUserClass
from telegram import Bot
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

    try:
        # using google speech recognition
        text = r.recognize_google(audio_text)
        print("Speech Recognition Text:", text)
    except FunctionTimedOut:
        print("Sorry, I did not get that")
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
    }, json=mode)

    # Get the response from the OpenAI API
    try:
        response_text = response.json()["choices"][0]["text"]
    except:
        if response.json():
            response_text = response.json()
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


queue = Queue()


def voice_engine() -> None:
    logger.info('Into engine')
    logger.info(f'{threading.active_count()}')
    logger.info(f'{threading.current_thread()}')

    while True:
        message__user_settings = queue.get()
        print(message__user_settings)
        # if message__user_settings[0] is BytesIO:
        wav_voice = take_and_convert_to_wav(message__user_settings[0])
        logger.info('Converting to wav passed')

        recognized_text = None
        try:
            recognized_text = func_timeout(timeout=1, func=speech_recognition, kwargs=dict(speech=wav_voice))
            logger.info('recognized_text passed')
            print(recognized_text)
        except FunctionTimedOut:
            print('speech_recognition time out!')
            try:
                recognized_text = func_timeout(timeout=6, func=speech_recognition, kwargs=dict(speech=wav_voice))
                logger.info('recognized_text passed')
                print(recognized_text)
            except FunctionTimedOut:
                print('The second speech_recognition time out!')

        response_text = request_to_openai(_text="Hi, DaVinchi! Say anything for test my program.", user_settings=message__user_settings)
        logger.info('Got response')

        # tts_response = text_to_speech_coqui(response_text)
        # tts_response = text_to_speech_google(response_text)
        logger.info('TTS is passed')

        strt_time = time.monotonic()
        async def send_replay():
            bot = Bot(token=TELEGRAM_BOT_TOKEN)
            async with bot:
                await bot.send_message(
                    chat_id=message__user_settings[1].telegram_id,
                    text=response_text
                )

        asyncio.run(send_replay())
        print(time.monotonic() - strt_time)

thread_engine = threading.Thread(target=voice_engine, daemon=True).start()


