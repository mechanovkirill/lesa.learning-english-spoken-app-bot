from telegram import Update
from telegram.ext import ContextTypes
from io import BytesIO
import asyncio

from lesa_bot.engine.engine import queue
from lesa_bot.db import get_user

import logging
logger = logging.getLogger(__name__)


async def voice_text_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler. It is receives and transmits users settings from database, voice and text messages from users
    to engine."""
    user = update.message.from_user
    logger.info("%s: %s", user.username, "voice_answer start")

    bot = context.bot
    file_id = update.message.voice.file_id
    voice = await bot.get_file(file_id)
    audio_stream = BytesIO()
    await voice.download_to_memory(out=audio_stream)
    audio_stream.seek(0)

    # get data from database
    user_settings = await get_user(user.id)

    #  hand over data to engine through queue
    message__user_settings = (audio_stream, user_settings, )
    queue.put(message__user_settings)


