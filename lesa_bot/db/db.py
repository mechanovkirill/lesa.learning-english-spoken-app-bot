from __future__ import annotations
from dataclasses import dataclass
import asyncio
import datetime
import logging

from sqlalchemy import Column, BigInteger, String, func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy.orm import selectinload

logger = logging.getLogger(__name__)

engine = create_async_engine(
    "sqlite+aiosqlite:///../db.sqlite3",
    echo=True,
)
async_session = async_sessionmaker(engine, expire_on_commit=False)

@dataclass
class BotUserClass:
    telegram_id: int
    api_key: str
    show_recognized_text: int
    show_text_answer: int
    language_: int
    tts_engine: int
    stt_engine: int
    mode: int
    create_date: datetime.datetime


class Base(DeclarativeBase):
    pass


class BotUser(Base):
    __tablename__ = "bot_users"

    telegram_id: Mapped[int] = Column(BigInteger, primary_key=True)
    api_key: Mapped[str] = Column(String(80), nullable=True)
    show_recognized_text: Mapped[int]
    show_text_answer: Mapped[int]
    language_: Mapped[int]
    tts_engine: Mapped[int]
    stt_engine: Mapped[int]
    mode: Mapped[int]
    create_date: Mapped[datetime.datetime] = mapped_column(server_default=func.now())


async def add_user(bot_user: BotUserClass, async_session_: async_sessionmaker[AsyncSession] = async_session) -> None:
    logger.info("Into add_user")

    async with async_session_() as session:
        async with session.begin():
            user = BotUser(
                telegram_id=bot_user.telegram_id,
                api_key=bot_user.api_key,
                show_recognized_text=bot_user.show_recognized_text,
                show_text_answer=bot_user.show_text_answer,
                language_=bot_user.language_,
                tts_engine=bot_user.tts_engine,
                stt_engine=bot_user.stt_engine,
                mode=bot_user.mode
            )
            session.add(user)


async def get_user(telegram_id: int, async_session_: async_sessionmaker[AsyncSession] = async_session) -> BotUser | None:
    logger.info("Into get_user")
    async with async_session_() as session:

        query = await session.get(BotUser, telegram_id)
        print(query)
        return query


async def check_user_exist(
        telegram_id: int, async_session_: async_sessionmaker[AsyncSession] = async_session
) -> True | False:
    logger.info("Into check_user")
    async with async_session_() as session:

        query = await session.get(BotUser, telegram_id)
        if query:
            return True
        return False

async def close_db() -> None:
    await engine.dispose()

#######################################################################################################################

# async def async_main() -> None:
#     logger.info("Into async_main")
#     engine = create_async_engine(
#         "sqlite+aiosqlite:///../db.sqlite3",
#         echo=True,
#     )
#
#     # async_sessionmaker: a factory for new AsyncSession objects.
#     # expire_on_commit - don't expire objects after transaction commit
#     async_session = async_sessionmaker(engine, expire_on_commit=False)
#
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
#
#     # for AsyncEngine created in function scope, close and
#     # clean-up pooled connections
#     await engine.dispose()
#
# asyncio.run(async_main())
#
# if __name__ == "__main__":
#     async_main()
