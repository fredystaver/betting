import logging
from typing import Callable, Awaitable, Type

from pydantic_settings import BaseSettings
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from core.constants import STATUSES


def create_engine(settings: BaseSettings) -> tuple[AsyncEngine, sessionmaker]:
    engine = create_async_engine(
        url=settings.database_url,
        pool_size=settings.pool_size,
        max_overflow=settings.max_overflow
    )
    logging.debug(msg=f"Установлено подключение к БД: {settings.database_url}")

    session_maker = sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

    return engine, session_maker


def init_tables(engine: AsyncEngine, base: DeclarativeBase) -> Callable[[], Awaitable[None]]:
    async def init() -> None:
        async with engine.begin() as conn:
            await conn.run_sync(base.metadata.drop_all)
            await conn.run_sync(base.metadata.create_all)

    return init


def insert_data(engine: AsyncEngine, table: Type[DeclarativeBase]) -> Callable[[], Awaitable[None]]:
    async def insert_() -> None:
        async with engine.begin() as conn:
            insert_statuses = insert(table).values(STATUSES)
            await conn.execute(insert_statuses)
            await conn.commit()

    return insert_
