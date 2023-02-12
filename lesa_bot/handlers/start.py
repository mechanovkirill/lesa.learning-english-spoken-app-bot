import asyncio
from telegram import Update
from telegram.ext import (ContextTypes)
from lesa_bot.templates import messages
from lesa_bot.db.db import check_user_exist


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    print(await check_user_exist(user_id))
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=messages.Greeting_message
    )
