from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
)

from config import TELEGRAM_BOT_TOKEN
from lesa_bot.handlers import start, message_voice

import logging.config
from config import LOGGING_CONFIG

logging.config.dictConfig(LOGGING_CONFIG)

logger = logging.getLogger(__name__)


def main() -> None:
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    start_handler = CommandHandler('start', start.start)
    echo_handler = MessageHandler(filters.VOICE & (~filters.COMMAND), message_voice.voice_answer)

    application.add_handler(start_handler)
    application.add_handler(echo_handler)

    application.run_polling()


if __name__ == '__main__':
    try:
        main()
    except Exception:
        import traceback
        logger.warning(traceback.format_exc())
    finally:
        pass
