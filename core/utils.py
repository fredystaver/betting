import json
import logging
from typing import Callable, Awaitable, Type

import aio_pika
from aio_pika.abc import AbstractIncomingMessage, AbstractChannel
from fastapi import FastAPI
from pydantic import ValidationError
from pydantic_settings import BaseSettings
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from starlette.requests import Request

from bet_maker.dao.bets import BetsDAO
from bet_maker.models.bets import BetStatuses
from core.constants import STATUSES
from core.schemas import EventStatusesEnum, EventMessage
from core.uow import SQLUnitOfWork


def create_engine(settings: BaseSettings) -> tuple[AsyncEngine, sessionmaker]:
    engine = create_async_engine(
        url=settings.database_url,
        pool_size=settings.pool_size,
        max_overflow=settings.max_overflow
    )
    logging.debug(msg=f"Установлено подключение к БД: {settings.database_url}")

    session_maker = sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

    return engine, session_maker


def setup_rabbit_connection(app: FastAPI) -> Callable[[], Awaitable[None]]:
    settings = app.state._settings.rabbit

    async def rabbit_connection() -> None:
        connection = await aio_pika.connect_robust(url=settings.rabbit_url)
        logging.debug(msg=f"Установлено подключение к RabbitMQ: {settings.rabbit_url}")
        channel = await connection.channel()
        queue = await channel.declare_queue(settings.queue_name, auto_delete=True)

        app.state.rabbit_channel = channel
        app.state.rabbit_connection = connection

        await queue.consume(_get_callback(app))

    return rabbit_connection


def _get_callback(app: FastAPI) -> Callable[[AbstractIncomingMessage], Awaitable[None]]:
    async def callback(message: AbstractIncomingMessage) -> None:
        async with message.process(), app.state.session_maker() as session:
            async with SQLUnitOfWork(session):

                message = EventMessage.model_validate(json.loads(message.body))
                bets = await BetsDAO(session).get_bets(message.event_id)

                for bet in bets:
                    match message.status_id:
                        case EventStatusesEnum.FINISHED_WIN:
                            bet.status_id = BetStatuses.FINISHED_WIN
                        case EventStatusesEnum.FINISHED_LOSE:
                            bet.status_id = BetStatuses.FINISHED_LOSE
                        case EventStatusesEnum.NEW:
                            bet.status_id = BetStatuses.NEW
                        case _:
                            raise ValidationError

    return callback


def get_rabbit_channel(request: Request) -> AbstractChannel:
    return request.app.state.rabbit_channel


def close_rabbit_connection(app: FastAPI) -> Callable[[], Awaitable[None]]:
    async def event() -> None:
        await app.state.rabbit_connection.close()

    return event


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
