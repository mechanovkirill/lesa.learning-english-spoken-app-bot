from telegram import Update
from telegram.ext import (ContextTypes)
from lesa_bot.templates import messages
from lesa_bot.db import check_user_exist, BotUserClass, add_user


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not await check_user_exist(user_id):
        user = BotUserClass(
            telegram_id=user_id,
            api_key=None,
            show_recognized_text=1,
            show_text_answer=1,
            language_=1,
            tts_engine=1,
            stt_engine=1,
            mode=1,
            create_date=None
        )
        await add_user(user)

        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=messages.GREETING_MESSAGE
        )
        return

    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=messages.GREETING_MESSAGE
    )
