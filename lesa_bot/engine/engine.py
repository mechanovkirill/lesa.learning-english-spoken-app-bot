import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any

import requests
import speech_recognition as sr
from pydub import AudioSegment
from TTS.utils.manage import ModelManager
from TTS.utils.synthesizer import Synthesizer
from gtts import gTTS
from io import BytesIO
from lesa_bot.db import BotUserClass

import logging
logger = logging.getLogger(__name__)


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

    try:
        # using google speech recognition
        text = r.recognize_google(audio_text)
        print("Speech Recognition Text:", text)
    except:
        print("Sorry, I did not get that")
        text = ""

    return text


def request_to_openai(request: str, key: str) -> str:
    openai_endpoint = "https://api.openai.com/v1/completions"
    # Send the text to the OpenAI API
    response = requests.post(openai_endpoint, headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {key}"
    }, json={
        "model": "text-davinci-003",
        "prompt": "This message will consist of 3 texts."
                  f"1. {request} "
                  "2. What mistakes are made in the text 1? "
                  "3. If text 1 does not contain a question"
                  "ask a question to keep the conversation going."
                  "Don't repeat numbers and instructions",
        "max_tokens": 100,
        "temperature": 0.7,
    })

    # Get the response from the OpenAI API
    try:
        response_text = response.json()["choices"][0]["text"]
    except:
        if response.json():
            response_text = response.json()
        response_text = "Sorry, no response received."

    print("OpenAI API Response:", response_text)

    return response_text


def voice_engine(message_voice: BytesIO, user_settings: BotUserClass) -> BytesIO:
    logger.info('Into engine')

    wav_voice = take_and_convert_to_wav(message_voice)
    logger.info('Converting to wav passed')

    recognized_text = speech_recognition(wav_voice)
    logger.info('recognized_text passed')

    response_text = request_to_openai(recognized_text, key=user_settings.api_key)
    logger.info('Got response')

    # tts_response = text_to_speech_coqui(response_text)
    tts_response = text_to_speech_google(response_text)
    logger.info('TTS is passed')

    return tts_response


async def sync_engine_to_async(message_voice: BytesIO, user_settings: BotUserClass) -> BytesIO:



