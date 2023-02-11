
from telegram import Update
from telegram.ext import ContextTypes
from io import BytesIO

from lesa_bot.engine.engine import take_and_convert_to_wav

import logging
logger = logging.getLogger(__name__)


async def voice_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    user = update.message.from_user
    logger.info("%s: %s", user.username, "Going into answer")
    file_id = update.message.voice.file_id
    voice = await bot.get_file(file_id)
    audio_stream = BytesIO()
    await voice.download_to_memory(out=audio_stream)
    audio_stream.seek(0)

    audio_answer = take_and_convert_to_wav(audio_stream)

    logger.info("Gender of %s: %s", user.first_name, "Going to audio answer")

    await context.bot.send_voice(
        chat_id=update.effective_chat.id, voice=audio_answer,
    )

