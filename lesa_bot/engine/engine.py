import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any

import aiohttp
import speech_recognition as sr
from pydub import AudioSegment
from io import BytesIO
from lesa_bot.engine.tts import text_to_speech_google_async, text_to_speech_coqui_async
from lesa_bot.db import BotUserClass

import logging
logger = logging.getLogger(__name__)


def take_and_convert_to_wav(ogg_file: BytesIO) -> BytesIO:
    """convert ogg audio stream to wav"""
    voice_data = AudioSegment.from_file(ogg_file)
    wav_voice = BytesIO()
    voice_data.export(out_f=wav_voice, format="wav")
    wav_voice.seek(0)
    return wav_voice


async def take_and_convert_to_wav_async(ogg_file: BytesIO) -> BytesIO:
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as pool:
        result = await loop.run_in_executor(pool, take_and_convert_to_wav, ogg_file)
    return result


#  ---------------------------------------------------------------------------------------------------
async def speech_recognition_google(speech: BytesIO) -> str:
    loop = asyncio.get_event_loop()
    # Initialize recognizer class (for recognizing the speech)
    r = sr.Recognizer()
    with sr.AudioFile(speech) as source:
        with ThreadPoolExecutor() as pool:
            audio_text = await loop.run_in_executor(pool, r.record, source)

    try:
        # using google speech recognition
        text = await loop.run_in_executor(None, r.recognize_google, audio_text)
        print("Speech Recognition Text:", text)
    except:
        print("Sorry, I did not get that")
        text = ""

    return text


#  -----------------------------------------------------------------------------------------------------
async def request_response_openai(request: str, _user_settings: BotUserClass) -> str:
    """Send request to OpenAI API and return response"""
    openai_endpoint = "https://api.openai.com/v1/completions"
    async with aiohttp.ClientSession() as session:
        async with session.post(openai_endpoint, headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {_user_settings.api_key}"
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
        }) as response:
            try:
                response_text = (await response.json())["choices"][0]["text"]
            except:
                if await response.json():
                    response_text = await response.json()
                else:
                    response_text = "Sorry, no response received from OpenAI."
            logger.info(response_text)

            return response_text


def voice_engine(message_voice: BytesIO, user_settings: BotUserClass) -> tuple[BytesIO, str, str] | BytesIO | str:
    logger.info('Into voice engine')

    wav_voice = take_and_convert_to_wav(message_voice)
    logger.info('Converting to wav passed')

    #  Recognize voice
    recognized_user_text = None
    try:
        recognized_user_text = await asyncio.wait_for(speech_recognition_google(wav_voice), timeout=1)
        logger.info('recognized_text passed')
    except asyncio.TimeoutError:
        logger.warning('speech_recognition_google timed out ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
    if recognized_user_text is None:
        try:
            recognized_user_text = await asyncio.wait_for(speech_recognition_google(wav_voice), timeout=1)
            logger.info('recognized_text passed')
        except asyncio.TimeoutError:
            logger.warning('speech_recognition_google second timed out ++++++++++++++++++++++++++++++++++++++++++++++')
            return "Failed to get text response from google speech recognition. Timeout exceeded."

    # send request to OpenAI
    try:
        response_ai_text = await asyncio.wait_for(
            request_response_openai(recognized_user_text, _user_settings=user_settings), timeout=10
        )
        logger.info('Got response from OpenAI')
    except asyncio.TimeoutError:
        logger.error('request_response_OpenAI timed out')
        return "Failed to get text response from OpenAI DaVinchi. Timeout exceeded."

    # text to speech
    tts_response = None
    tts_response_fail = None
    try:
        tts_response = await asyncio.wait_for(text_to_speech_google_async(response_ai_text), timeout=1)
        logger.info('TTS is passed. It is coming back to message')
    except asyncio.TimeoutError:
        logger.error('text_to_speech_coqui timed out')
    if tts_response is None:
        try:
            tts_response = await asyncio.wait_for(text_to_speech_google_async(response_ai_text), timeout=1)
            logger.info('TTS is passed. It is coming back to message')
        except asyncio.TimeoutError:
            logger.error('text_to_speech_coqui timed out')
            tts_response_fail = "Failed to convert response text to speech. Timeout exceeded."

    return recognized_user_text, response_ai_text, tts_response if tts_response else tts_response_fail


async def process_voice_message(audio_stream: BytesIO, user_settings: BotUserClass) -> Any:
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as pool:
        engine_answer = await loop.run_in_executor(pool, voice_engine, audio_stream, user_settings)

    return engine_answer



