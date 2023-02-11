import requests
import speech_recognition as sr
from pydub import AudioSegment
from io import BytesIO
from lesa_bot.engine.tts import text_to_speech_google
from lesa_bot.config import SECRET_KEY

import logging
logger = logging.getLogger(__name__)

def take_and_convert_to_wav(message_voice) -> BytesIO:
    """convert ogg audio stream to"""
    voice_data = AudioSegment.from_file(message_voice)
    wav_voice = BytesIO()
    voice_data.export(out_f=wav_voice, format="wav")
    wav_voice.seek(0)
    return wav_voice


def audio_to_audio():
    openai_api_key = SECRET_KEY
    openai_endpoint = "https://api.openai.com/v1/completions"
    print("Got the message voice")

    print("Converted message voice to wav")
    # Initialize recognizer class (for recognizing the speech)
    r = sr.Recognizer()
    with sr.AudioFile(wav_voice) as source:
        audio_text = r.record(source)
    print("Got wav and open")

    try:
        # using google speech recognition
        text = r.recognize_google(audio_text)
        print("Speech Recognition Text:", text)
    except:
        print("Sorry, I did not get that")
        text = ""

    # Send the text to the OpenAI API
    response = requests.post(openai_endpoint, headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_api_key}"
    }, json={
        "model": "text-davinci-003",
        "prompt": "This message will consist of 3 texts."
                  f"1. {text} "
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
        response_text = response.json()

    print("OpenAI API Response:", response_text)

    # tts_response = text_to_speech_coqui(response_text)
    tts_response = text_to_speech_google(response_text)

    sound = AudioSegment.from_file(tts_response)
    audio_answer = BytesIO()
    sound.export(out_f=audio_answer, format="ogg")
    audio_answer.seek(0)
    print("File ogg was saved")

    return audio_answer
