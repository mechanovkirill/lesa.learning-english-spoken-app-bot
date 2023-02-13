from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    filters,
)

from config import TELEGRAM_BOT_TOKEN, LOGGING_CONFIG
from handlers import start, message_voice, setkey, get_value, cancel

from db import close_db

import logging.config

logging.config.dictConfig(LOGGING_CONFIG)

logger = logging.getLogger(__name__)


def main() -> None:
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    start_handler = CommandHandler('start', start.start)

    setkey_handler = ConversationHandler(
        entry_points=[CommandHandler("setkey", setkey.setkey)],
        states={
            0: [CommandHandler("cancel", cancel.cancel), MessageHandler(filters.TEXT, get_value.get_and_set_value)],
        },
        fallbacks=[CommandHandler("cancel", cancel.cancel)],
    )


    echo_voice_handler = MessageHandler(filters.VOICE & (~filters.COMMAND), message_voice.voice_answer)

    application.add_handler(start_handler)
    application.add_handler(setkey_handler)
    application.add_handler(echo_voice_handler)

    application.run_polling()


if __name__ == '__main__':
    try:
        main()
    except Exception:
        import traceback
        logger.warning(traceback.format_exc())
    finally:
        close_db()
