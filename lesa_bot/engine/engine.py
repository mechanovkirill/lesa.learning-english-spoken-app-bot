import aiohttp
import speech_recognition as sr
from pydub import AudioSegment
from io import BytesIO
from lesa_bot.engine.tts import text_to_speech_google, text_to_speech_coqui
from lesa_bot.config import SECRET_KEY

import logging
logger = logging.getLogger(__name__)


async def take_and_convert_to_wav(ogg_file: BytesIO) -> BytesIO:
    """convert ogg audio stream to"""
    voice_data = AudioSegment.from_file(ogg_file)
    wav_voice = BytesIO()
    voice_data.export(out_f=wav_voice, format="wav")
    wav_voice.seek(0)
    return wav_voice


async def speech_recognition_google(speech: BytesIO) -> str:
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


async def request_response(request: str, key: str = SECRET_KEY) -> str:
    openai_endpoint = "https://api.openai.com/v1/completions"
    async with aiohttp.ClientSession() as session:
        async with session.post(openai_endpoint, headers={
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
        }) as response:
            try:
                response_text = (await response.json())["choices"][0]["text"]
            except:
                if await response.json():
                    response_text = await response.json()
                else:
                    response_text = "Sorry, no response received from OpenAI."

            print("OpenAI API Response:", response_text)

            return response_text


async def engine(message_voice: BytesIO) -> BytesIO:
    logger.info('Into engine')

    wav_voice = await take_and_convert_to_wav(message_voice)
    logger.info('Converting to wav passed')

    recognized_text = await speech_recognition_google(wav_voice)
    logger.info('recognized_text passed')

    response_text = await request_response(recognized_text)
    logger.info('Got response')

    tts_response = await text_to_speech_coqui(response_text)
    # tts_response = text_to_speech_google(response_text)
    logger.info('TTS is passed. It is coming back to message')

    return tts_response
