import requests
from db import BotUserClass
from config import TOKENS_AMOUNT, TEMPERATURE

import logging
import traceback

logger = logging.getLogger(__name__)


def request_to_openai(
        _text: str,
        _user_settings: BotUserClass,
        tokens_n=int(TOKENS_AMOUNT),
        temperature=float(TEMPERATURE),
) -> str:
    """Send text to API and return response"""
    openai_endpoint = "https://api.openai.com/v1/chat/completions"
    key = _user_settings.api_key
    if not key:
        response_text = """
        OpenAI API key missing :(
        Please use the /set_key command to save your key, or use the /help command for information.
        """
        return response_text

    if _user_settings.mode == 1:
        mode = {
            "model": "gpt-3.5-turbo",
            "messages": [{
                "role": "user",
                "content": f'What are the errors in the following statement: "{_text}"? If the statement did not '
                           'contain a question, then ask a question to keep the conversation going, otherwise '
                           'answer the question in the statement and then ask a question to keep the conversation '
                           'going. (Short example:"What\'s the advantages of AI in business and how can it improve '
                           'customer experience?"'
                           'The two grammatical errors are:'
                           '"Explanation of the first error".'
                           '"Explanation of the second error".'
                           '"The answer to the question in the statement".'
                           'Counterquestion:e.g."How do you want to use AI?")'
            }],
            "max_tokens": tokens_n,
            "temperature": temperature,
        }
    else:
        mode = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": f"{_text}"}]
        }

    # Send the text to the OpenAI API
    try:
        response = requests.post(openai_endpoint, headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}"
        }, json=mode, timeout=14)
    except (requests.exceptions.RequestException, Exception):
        logger.warning(f'Request to OpenAI error{traceback.format_exc()}')
        response_text = 'Failed to get response from OpenAI'
        return response_text

    # Get the response from the OpenAI API
    try:
        response_text = response.json()['choices'][0]['message']['content']
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
