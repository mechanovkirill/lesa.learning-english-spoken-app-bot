import requests
from db import BotUserClass

import logging
import traceback
logger = logging.getLogger(__name__)


def request_to_openai(_text: str, _user_settings: BotUserClass) -> str:
    """Send text to API and return response"""
    openai_endpoint = "https://api.openai.com/v1/completions"

    if _user_settings.mode == 1:
        mode = {
            "model": "text-davinci-003",
            "prompt": f"{_text}" """- answer briefly. 
            What are the mistakes in the first text above? Ask a question to continue the conversation. 
            """,
            "max_tokens": 100,
            "temperature": 0.5,
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
        }, json=mode, timeout=14)
    except (requests.exceptions.RequestException, Exception):
        logger.warning(f'Request to OpenAI error{traceback.format_exc()}')
        response_text = 'Failed to get response from OpenAI'
        return response_text

    # Get the response from the OpenAI API
    try:
        response_text = response.json()["choices"][0]["text"]
        return response_text
    except Exception:
        logger.warning(f"No response from OpenAI.{traceback.format_exc()}")
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
