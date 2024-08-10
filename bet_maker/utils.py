import json
import logging
from typing import Callable, Awaitable

import aio_pika
from aio_pika.abc import AbstractIncomingMessage
from fastapi import FastAPI
from pydantic import ValidationError

from bet_maker.dao.bets import BetsDAO
from bet_maker.models.bets import BetStatuses
from core.schemas import EventMessage, EventStatusesEnum
from core.uow import SQLUnitOfWork


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


def close_rabbit_connection(app: FastAPI) -> Callable[[], Awaitable[None]]:
    async def event() -> None:
        await app.state.rabbit_connection.close()

    return event
