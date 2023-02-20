from telegram import Update
from telegram.ext import ContextTypes
from io import BytesIO

from lesa_bot.engine.engine import hand_over_queue
from lesa_bot.db import get_user

import logging
logger = logging.getLogger(__name__)


async def voice_text_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler. It is receives and transmits users settings from database, voice and text messages from users
    to engine."""
    user = update.message.from_user
    logger.info("%s: %s", user.username, "voice_answer start")

    bot = context.bot

    # get data from database
    user_settings = await get_user(user.id)
    if not user_settings or not user_settings.api_key:
        await bot.send_message(chat_id=update.effective_chat.id, text="""I'm sorry, but your account does not have 
an OpenAI API key, or your account settings are missing. You can get the OpenAI Key for free by registering 
at the link https://platform.openai.com/account/api-keys 
You can use the /help command for more information, or you can use the /set_key command to save OpenAI API key.
    """)
    else:
        # checking data
        if update.message.voice:
            file_id = update.message.voice.file_id
            voice = await bot.get_file(file_id)
            audio_stream = BytesIO()
            await voice.download_to_memory(out=audio_stream)
            audio_stream.seek(0)

            #  hand over data to engine through queue
            message__user_settings = (audio_stream, user_settings, )
            hand_over_queue.put(message__user_settings)

        if update.message.text:
            text = update.message.text
            #  hand over data to engine through queue
            message__user_settings = (text, user_settings, )
            hand_over_queue.put(message__user_settings)



