from telegram import Update
from telegram.ext import ContextTypes
from io import BytesIO
import asyncio

from lesa_bot.engine.engine import process_voice_message
from lesa_bot.db import get_user

import logging
logger = logging.getLogger(__name__)


async def voice_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler. It is receives and transmits users settings from database, voice and text messages from users
    to engine. And send response to users depending on the answer."""
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

        # voice_engine = asyncio.create_task(process_voice_message(audio_stream, user_settings))

        #  hand over data to engine
        engine_answer = await process_voice_message(audio_stream, user_settings)

        if isinstance(engine_answer, tuple):
            print(isinstance(engine_answer, tuple))
            if user_settings.show_recognized_text == 1:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id, text=engine_answer[0]
                )
            if user_settings.show_text_answer == 1:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id, text=engine_answer[1]
                )
            if isinstance(engine_answer[2], BytesIO):
                await context.bot.send_voice(
                    chat_id=update.effective_chat.id, voice=engine_answer[2]
                )
            else:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id, text=engine_answer[2]
                )
            return
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id, text=engine_answer
            )
            return

    if update.message.text:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text="This is a text!"
        )


