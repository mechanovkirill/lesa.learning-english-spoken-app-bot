
from telegram import Update
from telegram.ext import (ContextTypes)
from lesa_bot.templates import messages


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=messages.Greeting_message
    )
