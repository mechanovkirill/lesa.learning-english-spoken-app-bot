from telegram import Update
from telegram.ext import ContextTypes
from io import BytesIO
from lesa_bot.db import get_user

from lesa_bot.engine.engine import audio_engine

import logging

logger = logging.getLogger(__name__)


async def voice_or_text_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    logger.info("%s: %s", user.username, "voice_or_text_response start voice")

    user_settings = await get_user(telegram_id=user.id)

    if update.message.voice:
        bot = context.bot
        file_id = update.message.voice.file_id
        voice = await bot.get_file(file_id)
        audio_stream = BytesIO()
        await voice.download_to_memory(out=audio_stream)
        audio_stream.seek(0)

        audio_answer = await audio_engine(audio_stream, user_settings)

        await context.bot.send_voice(
            chat_id=update.effective_chat.id, voice=audio_answer,
        )

    if update.message.text:
        logger.info("%s: %s", user.username, "voice_or_text_response start voice")
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text="It was a text!"
        )
