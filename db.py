from __future__ import annotations
from dataclasses import dataclass
import datetime
import logging

from sqlalchemy import Column, BigInteger, String, func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from config import DATABASE

logger = logging.getLogger(__name__)

engine = create_async_engine(DATABASE, echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=True)


@dataclass
class BotUserClass:
    telegram_id: int
    api_key: str | None
    show_text: int
    tts_engine: int
    stt_engine: 0 | 1
    mode: 0 | 1
    payed: bool
    create_date: datetime.datetime | None


class Base(DeclarativeBase):
    pass


class BotUser(Base):
    __tablename__ = "bot_users"

    telegram_id: Mapped[int] = Column(BigInteger, primary_key=True)
    api_key: Mapped[str] = Column(String(80), nullable=True)
    show_text: Mapped[int]
    tts_engine: Mapped[int]
    stt_engine: Mapped[int]
    mode: Mapped[int]
    payed: Mapped[bool]
    create_date: Mapped[datetime.datetime] = mapped_column(server_default=func.now())


async def add_user(bot_user: BotUserClass, async_session_: async_sessionmaker[AsyncSession] = async_session) -> None:
    logger.info("Into add_user")

    async with async_session_() as session:
        async with session.begin():
            user = BotUser(
                telegram_id=bot_user.telegram_id,
                api_key=bot_user.api_key,
                show_text=bot_user.show_text,
                tts_engine=bot_user.tts_engine,
                stt_engine=bot_user.stt_engine,
                payed=bot_user.payed,
                mode=bot_user.mode
            )
            session.add(user)


async def get_user(telegram_id: int,
                   async_session_: async_sessionmaker[AsyncSession] = async_session) -> BotUserClass | None:
    logger.info("Into get_user")
    async with async_session_() as session:
        user = await session.get(BotUser, telegram_id)
        _isinstance = None
        if user:
            _isinstance = BotUserClass(
                telegram_id=user.telegram_id,
                api_key=user.api_key,
                show_text=user.show_text,
                tts_engine=user.tts_engine,
                stt_engine=user.stt_engine,
                mode=user.mode,
                payed=user.payed,
                create_date=None
            )

        return _isinstance


async def check_user_exist(
        telegram_id: int, async_session_: async_sessionmaker[AsyncSession] = async_session
) -> True | False:
    logger.info("Into check_user")
    async with async_session_() as session:
        query = await session.execute(select(BotUser.telegram_id).where(BotUser.telegram_id == telegram_id))
        if query.fetchone():
            return True
        return False


async def set_key(
        telegram_id: int,
        value: str,
        async_session_: async_sessionmaker[AsyncSession] = async_session
) -> None:
    logger.info("Into set key")
    async with async_session_() as session:
        user_inst = await session.get(BotUser, telegram_id)
        user_inst.api_key = value

        await session.commit()


async def set_text_display(
        telegram_id: int,
        value: int,
        async_session_: async_sessionmaker[AsyncSession] = async_session
) -> None:
    logger.info("Into set srt")
    async with async_session_() as session:
        user_inst = await session.get(BotUser, telegram_id)
        user_inst.show_text = value

        await session.commit()


async def set_tts_engine(
        telegram_id: int,
        value: int,
        async_session_: async_sessionmaker[AsyncSession] = async_session
) -> None:
    logger.info("Into set tts")
    async with async_session_() as session:
        user_inst = await session.get(BotUser, telegram_id)
        user_inst.tts_engine = value

        await session.commit()


async def set_stt_engine(
        telegram_id: int,
        value: int,
        async_session_: async_sessionmaker[AsyncSession] = async_session
) -> None:
    logger.info("Into set stt")
    async with async_session_() as session:
        user_inst = await session.get(BotUser, telegram_id)
        user_inst.stt_engine = value

        await session.commit()


async def set_mode(
        telegram_id: int,
        value: 0 | 1,
        async_session_: async_sessionmaker[AsyncSession] = async_session
) -> None:
    logger.info("Into set mode")
    async with async_session_() as session:
        user_inst = await session.get(BotUser, telegram_id)
        user_inst.mode = value

        await session.commit()


async def close_db() -> None:
    await engine.dispose()
