from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
from templates import messages
from db import (
    check_user_exist,
    set_key,
    set_mode,
    set_stt_engine,
    set_tts_engine,
    set_text_display
)
from services.handlers_services import check_and_save_user_if_not

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
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id

    if await check_and_save_user_if_not(user_id):
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=messages.GREETING_MESSAGE
        )

start_handler = CommandHandler(('start', 'help'), start)


# setkey--------------------------------------------------------------------------------------------------------
async def setkey(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    if not await check_user_exist(user_id):
        await update.message.reply_text(messages.ACCAUNT_IS_NOT_EXIST)

        return ConversationHandler.END

    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=messages.SET_KEY_MESSAGE
    )

    return 0


async def get_and_set_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    value = update.message.text
    user_id = update.message.from_user.id
    await set_key(telegram_id=user_id, value=value)

    await update.message.reply_text(
        "The data has been received and stored."
    )

    return ConversationHandler.END


setkey_conversation_handler = ConversationHandler(
    entry_points=[CommandHandler("set_key", setkey)],
    states={
        0: [CommandHandler("cancel", cancel), MessageHandler(filters.TEXT, get_and_set_key)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)


#  set_text_display_option ------------------------------------------------------------------------------------------
async def set_text_display_option(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """/srt Set the option to show messages with recognized text or not"""
    user_id = update.effective_user.id
    if not await check_user_exist(user_id):
        await update.message.reply_text(messages.ACCAUNT_IS_NOT_EXIST)

        return ConversationHandler.END

    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=messages.SET_TEXT_DISPLAY
    )

    return 0


async def get_and_set_td_value(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    value = update.message.text
    if value.isnumeric():
        value = int(value)
        if 0 <= value <= 3:
            user_id = update.message.from_user.id
            await set_text_display(telegram_id=user_id, value=value)

            await update.message.reply_text(
                "The data has been received and stored."
            )

            return ConversationHandler.END
        else:
            await update.message.reply_text(messages.WRONG_DATA)

    else:
        await update.message.reply_text(messages.WRONG_DATA)


std_conversation_handler = ConversationHandler(
    entry_points=[CommandHandler("set_text", set_text_display_option)],
    states={
        0: [CommandHandler("cancel", cancel), MessageHandler(filters.TEXT, get_and_set_td_value)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)


#  tts --------------------------------------------------------------------------------------------------------
async def set_tts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    if not await check_user_exist(user_id):
        await update.message.reply_text(messages.ACCAUNT_IS_NOT_EXIST)

        return ConversationHandler.END

    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=messages.SET_TTS_MESSAGE
    )

    return 0


async def get_and_set_tts_value(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    value = update.message.text
    if value.isnumeric():
        value = int(value)
        if 0 <= value <= 4:
            user_id = update.message.from_user.id
            await set_tts_engine(telegram_id=user_id, value=value)

            await update.message.reply_text(
                "The data has been received and stored."
            )

            return ConversationHandler.END
        else:
            await update.message.reply_text(messages.WRONG_DATA)

    else:
        await update.message.reply_text(messages.WRONG_DATA)


tts_conversation_handler = ConversationHandler(
    entry_points=[CommandHandler("set_tts", set_tts)],
    states={
        0: [CommandHandler("cancel", cancel), MessageHandler(filters.TEXT, get_and_set_tts_value)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)


# stt ----------------------------------------------------------------------------------------------------------------
async def set_stt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    if not await check_user_exist(user_id):
        await update.message.reply_text(messages.ACCAUNT_IS_NOT_EXIST)

        return ConversationHandler.END

    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=messages.SET_STT_MESSAGE
    )

    return 0


async def get_and_set_stt_value(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    value = update.message.text
    if value.isnumeric():
        value = int(value)
        if 0 <= value <= 2:
            user_id = update.message.from_user.id
            await set_stt_engine(telegram_id=user_id, value=value)

            await update.message.reply_text(
                "The data has been received and stored."
            )

            return ConversationHandler.END
        else:
            await update.message.reply_text(messages.WRONG_DATA)

    else:
        await update.message.reply_text(messages.WRONG_DATA)


stt_conversation_handler = ConversationHandler(
    entry_points=[CommandHandler("stt", set_stt)],
    states={
        0: [CommandHandler("cancel", cancel), MessageHandler(filters.TEXT, get_and_set_stt_value)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)


# mode --------------------------------------------------------------------------------------------------------------
async def set_mode_(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    if not await check_user_exist(user_id):
        await update.message.reply_text(messages.ACCAUNT_IS_NOT_EXIST)

        return ConversationHandler.END

    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=messages.SET_MODE_MESSAGE
    )

    return 0


async def get_and_set_mode_value(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    value = update.message.text
    if value.isnumeric():
        value = int(value)
        if value != 1 and value != 0:
            await update.message.reply_text(messages.WRONG_DATA)
        else:
            user_id = update.message.from_user.id
            await set_mode(telegram_id=user_id, value=value)

            await update.message.reply_text(
                "The data has been received and stored."
            )

            return ConversationHandler.END

    else:
        await update.message.reply_text(messages.WRONG_DATA)


mode_conversation_handler = ConversationHandler(
    entry_points=[CommandHandler("set_mode", set_mode_)],
    states={
        0: [CommandHandler("cancel", cancel), MessageHandler(filters.TEXT, get_and_set_mode_value)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

all_command_handlers = (
    start_handler,
    setkey_conversation_handler,
    std_conversation_handler,
    tts_conversation_handler,
    mode_conversation_handler
)
