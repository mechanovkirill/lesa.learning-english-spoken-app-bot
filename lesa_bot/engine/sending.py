import asyncio
import time

import telegram
import requests
from io import BytesIO
from lesa_bot.config import TELEGRAM_BOT_TOKEN

import logging

logger = logging.getLogger(__name__)


def send_via_bot(_user_id: int, content: tuple) -> None:
    # start_t = time.monotonic()

    async def bot() -> None:
        try:
            bot_ = telegram.Bot(TELEGRAM_BOT_TOKEN)
            async with bot_:
                for i in content:
                    if isinstance(i, str):
                        await bot_.send_message(chat_id=_user_id, text=i)
                    if isinstance(i, BytesIO):
                        await bot_.send_voice(chat_id=_user_id, voice=i)
        except telegram.error.TelegramError:
            try:
                bot_ = telegram.Bot(TELEGRAM_BOT_TOKEN)
                async with bot:
                    for i in content:
                        if isinstance(i, str):
                            await bot_.send_message(chat_id=_user_id, text=i)
                        if isinstance(i, BytesIO):
                            await bot_.send_voice(chat_id=_user_id, voice=i)
            except telegram.error.TelegramError as exc:
                logger.warning(f"Sanding error. {exc.message}")

    asyncio.run(bot())

    # logger.info(f'Sent by bot at {time.monotonic() - start_t}')


def send_text_msg(chat_id: int, text: str) -> None:
    # strt = time.monotonic()
    token = TELEGRAM_BOT_TOKEN
    url = "https://api.telegram.org/bot" + token + "/sendMessage" + "?chat_id=" + str(chat_id) + "&text=" + text
    try:
        response = requests.get(url, timeout=5)
        # logger.info(f'Sent for {time.monotonic() - strt}')
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

