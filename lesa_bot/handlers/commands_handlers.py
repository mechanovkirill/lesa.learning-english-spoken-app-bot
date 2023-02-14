from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
from lesa_bot.templates import messages
from lesa_bot.db import (
    check_user_exist,
    BotUserClass,
    add_user,
    set_key,
    set_show_recognized_text,
    set_mode,
    set_stt_engine,
    set_tts_engine,
    set_show_text_answer
)

import logging

logger = logging.getLogger(__name__)


#  commonn-----------------------------------------------------------------------------------------------------
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.username)
    await update.message.reply_text(
        "Data entry cancelled.",
    )
    return ConversationHandler.END


#  /start -------------------------------------------------------------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not await check_user_exist(user_id):
        user = BotUserClass(
            telegram_id=user_id,
            api_key=None,
            show_recognized_text=1,
            show_text_answer=1,
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

start_handler = CommandHandler('start', start)

# setkey--------------------------------------------------------------------------------------------------------
async def setkey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not await check_user_exist(user_id):
        await update.message.reply_text(messages.ACCAUNT_IS_NOT_EXIST)

        return ConversationHandler.END

    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=messages.SET_KEY_MESSAGE
    )

    return 0


async def get_and_set_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    logger.info("%s: %s", user.username, "get value start")

    value = update.message.text
    user_id = user.id
    await set_key(telegram_id=user_id, value=value)

    await update.message.reply_text(
        "The data has been received and stored."
    )

    return ConversationHandler.END


setkey_conversation_handler = ConversationHandler(
    entry_points=[CommandHandler("setkey", setkey)],
    states={
        0: [CommandHandler("cancel", cancel), MessageHandler(filters.TEXT, get_and_set_key)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)


#  set_spech_recogn_option ------------------------------------------------------------------------------------------
async def set_show_rt_option(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/srt Set the option to show messages with recognized text or not"""
    user_id = update.effective_user.id
    if not await check_user_exist(user_id):
        await update.message.reply_text(messages.ACCAUNT_IS_NOT_EXIST)

        return ConversationHandler.END

    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=messages.SET_SRT_MESSAGE
    )

    return 0


async def get_and_set_srt_value(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    logger.info("%s: %s", user.username, "get value start")

    value = update.message.text
    if value.isnumeric():
        value = int(value)
        if value != 1 and value != 0:
            await update.message.reply_text(messages.WRONG_DATA)
        else:
            user_id = user.id
            await set_show_recognized_text(telegram_id=user_id, value=value)

            await update.message.reply_text(
                "The data has been received and stored."
            )

            return ConversationHandler.END

    else:
        await update.message.reply_text(messages.WRONG_DATA)

ssro_conversation_handler = ConversationHandler(
    entry_points=[CommandHandler("srt", set_show_rt_option)],
    states={
        0: [CommandHandler("cancel", cancel), MessageHandler(filters.TEXT, get_and_set_srt_value)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)
