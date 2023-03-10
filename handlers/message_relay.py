from telegram import Update
from telegram.ext import ContextTypes
from io import BytesIO

# import sys
# sys.path.append('./')

from engine.engine import hand_over_queue
from db import get_user
from templates.messages import HAVENOT_SETTINGS

import logging

logger = logging.getLogger(__name__)


async def hand_over_voice_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Receives and transmits users settings from database, voice and text messages from users
    to engine."""
    user = update.message.from_user
    logger.info("%s: %s", user.username, "Income message got")

    bot = context.bot

    user_settings = await get_user(user.id)
    if not user_settings:
        await bot.send_message(chat_id=update.effective_chat.id, text=HAVENOT_SETTINGS)
    elif not user_settings.api_key:
        await bot.send_message(chat_id=update.effective_chat.id, text=HAVENOT_SETTINGS)
    else:
        # checking data
        if update.message.voice:
            file_id = update.message.voice.file_id
            voice = await bot.get_file(file_id)
            audio_stream = BytesIO()
            await voice.download_to_memory(out=audio_stream)
            audio_stream.seek(0)

            #  hand over data to engine through queue
            message__user_settings = (audio_stream, user_settings,)
            hand_over_queue.put(message__user_settings)

        if update.message.text:
            text = update.message.text
            #  hand over data to engine through queue
            message__user_settings = (text, user_settings,)
            hand_over_queue.put(message__user_settings)
