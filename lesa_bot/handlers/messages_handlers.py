
from telegram import Update
from telegram.ext import ContextTypes
from io import BytesIO

from lesa_bot.engine.engine import voice_engine
from lesa_bot.db import get_user

import logging
logger = logging.getLogger(__name__)


async def voice_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    logger.info("%s: %s", user.username, "voice_answer start")

    bot = context.bot

    if update.message.voice:
        file_id = update.message.voice.file_id
        voice = await bot.get_file(file_id)
        audio_stream = BytesIO()
        await voice.download_to_memory(out=audio_stream)
        audio_stream.seek(0)

        # get data from database
        user_settings = await get_user(user.id)

        #  hand over data to engine
        engine_answer = await voice_engine(audio_stream, user_settings)

        if type(engine_answer) == tuple:
            await context.bot.send_voice(
                chat_id=update.effective_chat.id, voice=engine_answer[0],
            )
            if user_settings.show_recognized_text == 1:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id, text=engine_answer[1]
                )
            return
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id, text="Failed to receive a voice response."
            )

    if update.message.text:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text="This is a text!"
        )


