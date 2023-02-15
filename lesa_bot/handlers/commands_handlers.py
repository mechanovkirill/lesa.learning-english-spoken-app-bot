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
    set_show_text_answer,
    engine
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
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
    entry_points=[CommandHandler("setkey", setkey)],
    states={
        0: [CommandHandler("cancel", cancel), MessageHandler(filters.TEXT, get_and_set_key)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)


#  set_spech_recogn_option ------------------------------------------------------------------------------------------
async def set_show_rt_option(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """/srt Set the option to show messages with recognized text or not"""
    user_id = update.effective_user.id
    if not await check_user_exist(user_id):
        await update.message.reply_text(messages.ACCAUNT_IS_NOT_EXIST)

        return ConversationHandler.END

    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=messages.SET_SRT_MESSAGE
    )

    return 0


async def get_and_set_srt_value(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    value = update.message.text
    if value.isnumeric():
        value = int(value)
        if value != 1 and value != 0:
            await update.message.reply_text(messages.WRONG_DATA)
        else:
            user_id = update.message.from_user.id
            await set_show_recognized_text(telegram_id=user_id, value=value)

            await update.message.reply_text(
                "The data has been received and stored."
            )

            return ConversationHandler.END

    else:
        await update.message.reply_text(messages.WRONG_DATA)


srt_conversation_handler = ConversationHandler(
    entry_points=[CommandHandler("srt", set_show_rt_option)],
    states={
        0: [CommandHandler("cancel", cancel), MessageHandler(filters.TEXT, get_and_set_srt_value)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)


#  sta --------------------------------------------------------------------------------------------------------------
async def set_show_ta_option(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    if not await check_user_exist(user_id):
        await update.message.reply_text(messages.ACCAUNT_IS_NOT_EXIST)

        return ConversationHandler.END

    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=messages.SET_STA_MESSAGE
    )

    return 0


async def get_and_set_ta_value(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    value = update.message.text
    if value.isnumeric():
        value = int(value)
        if value != 1 and value != 0:
            await update.message.reply_text(messages.WRONG_DATA)
        else:
            user_id = update.message.from_user.id
            await set_show_text_answer(telegram_id=user_id, value=value)

            await update.message.reply_text(
                "The data has been received and stored."
            )

            return ConversationHandler.END

    else:
        await update.message.reply_text(messages.WRONG_DATA)


sta_conversation_handler = ConversationHandler(
    entry_points=[CommandHandler("sta", set_show_ta_option)],
    states={
        0: [CommandHandler("cancel", cancel), MessageHandler(filters.TEXT, get_and_set_ta_value)],
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
        if value != 1 and value != 0:
            await update.message.reply_text(messages.WRONG_DATA)
        else:
            user_id = update.message.from_user.id
            await set_tts_engine(telegram_id=user_id, value=value)

            await update.message.reply_text(
                "The data has been received and stored."
            )

            return ConversationHandler.END

    else:
        await update.message.reply_text(messages.WRONG_DATA)


tts_conversation_handler = ConversationHandler(
    entry_points=[CommandHandler("tts", set_tts)],
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
        if value != 1 and value != 0:
            await update.message.reply_text(messages.WRONG_DATA)
        else:
            user_id = update.message.from_user.id
            await set_stt_engine(telegram_id=user_id, value=value)

            await update.message.reply_text(
                "The data has been received and stored."
            )

            return ConversationHandler.END

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
    entry_points=[CommandHandler("setmode", set_mode_)],
    states={
        0: [CommandHandler("cancel", cancel), MessageHandler(filters.TEXT, get_and_set_mode_value)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)


all_command_handlers = (
    start_handler,
    setkey_conversation_handler,
    srt_conversation_handler,
    sta_conversation_handler,
    tts_conversation_handler,
    stt_conversation_handler,
    mode_conversation_handler
)


