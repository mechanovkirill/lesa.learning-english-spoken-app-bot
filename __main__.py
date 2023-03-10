import asyncio

from telegram.ext import (
    Application,
    MessageHandler,
    filters,
)

from config import TELEGRAM_BOT_TOKEN, LOGGING_CONFIG
from handlers.message_relay import hand_over_voice_text
from handlers.commands_handlers import all_command_handlers

from db import close_db

import logging.config

logging.config.dictConfig(LOGGING_CONFIG)

logger = logging.getLogger(__name__)


def main() -> None:
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    echo_handler = MessageHandler((filters.VOICE | filters.TEXT) & ~filters.COMMAND, hand_over_voice_text)

    for handler in all_command_handlers:
        application.add_handler(handler)

    application.add_handler(echo_handler)

    application.run_polling()


if __name__ == '__main__':
    try:
        main()
    except Exception:
        import traceback
        logger.warning(traceback.format_exc())
    finally:
        asyncio.run(close_db())
