from db import (
    check_user_exist,
    BotUserClass,
    add_user,
)


async def check_and_save_user_if_not(user_id):
    if not await check_user_exist(user_id):
        user = BotUserClass(
            telegram_id=user_id,
            api_key=None,
            show_text=1,
            tts_engine=1,
            stt_engine=1,
            mode=1,
            payed=False,
            create_date=None
        )
        await add_user(user)
        return True

    return True
