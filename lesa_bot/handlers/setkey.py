from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from lesa_bot.templates import messages
from lesa_bot.db import check_user_exist


async def setkey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not await check_user_exist(user_id):
        await update.message.reply_text(
            "Ваш аккаунт не найден, пожалуйста, введите команду /start, "
            "затем повторите команду /setkey для сохранения ключа."
        )

        return ConversationHandler.END

    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=messages.SET_KEY_MESSAGE
    )

    return 0
