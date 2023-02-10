from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
)

from config import TELEGRAM_BOT_TOKEN
from lesa_bot.handlers import start, message_voice


def main() -> None:
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    start_handler = CommandHandler('start', start.start)
    echo_handler = MessageHandler(filters.VOICE & (~filters.COMMAND), message_voice.voice_answer)

    application.add_handler(start_handler)
    application.add_handler(echo_handler)

    application.run_polling()


if __name__ == '__main__':
    main()