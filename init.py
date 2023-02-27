from __future__ import annotations
import asyncio
import datetime

from config import DATABASE
from engine.tts import text_to_speech_coqui

from sqlalchemy import Column, BigInteger, String, func
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase


import logging
logger = logging.getLogger(__name__)

text_to_speech_coqui('Text for model init')


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


async def async_main() -> None:
    logger.info("Into async_main")
    engine = create_async_engine(
        DATABASE,
        echo=True,
    )

    # async_sessionmaker: a factory for new AsyncSession objects.
    # expire_on_commit - don't expire objects after transaction commit
    async_session = async_sessionmaker(engine, expire_on_commit=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # for AsyncEngine created in function scope, close and
    # clean-up pooled connections
    await engine.dispose()

asyncio.run(async_main())

