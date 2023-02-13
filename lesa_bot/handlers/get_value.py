

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from lesa_bot.db import set_key

import logging
logger = logging.getLogger(__name__)


async def get_and_set_value(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    logger.info("%s: %s", user.username, "get value start")

    value = update.message.text
    user_id = user.id
    await set_key(telegram_id=user_id, value=value)

    await update.message.reply_text(
        "Данные были получены и сохранены."
    )

    return ConversationHandler.END
