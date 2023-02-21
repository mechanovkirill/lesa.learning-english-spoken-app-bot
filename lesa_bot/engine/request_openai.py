from func_timeout import FunctionTimedOut

import requests
from lesa_bot.db import BotUserClass

import logging

logger = logging.getLogger(__name__)


def request_to_openai(_text: str, _user_settings: BotUserClass) -> str:
    """Send text to API and return response"""
    openai_endpoint = "https://api.openai.com/v1/completions"

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
    except requests.exceptions.JSONDecodeError:
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

        elif _user_settings.show_text == 2:
            answer_text = f'LESA:{_response_text}'
            return answer_text

        elif _user_settings.show_text == 3:
            answer_text = f'You:\n  {_recognized_text}'
            return answer_text

        else:
            return answer_text
    else:
        if _user_settings.show_text != 0:
            answer_text = f'LESA:{_response_text}'
            return answer_text

        else:
            return answer_text
