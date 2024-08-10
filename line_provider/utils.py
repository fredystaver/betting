import logging
from typing import Callable, Awaitable

import aio_pika
from aio_pika.abc import AbstractChannel
from fastapi import FastAPI
from starlette.requests import Request


def setup_rabbit_connection(app: FastAPI) -> Callable[[], Awaitable[None]]:
    settings = app.state._settings.rabbit

    async def rabbit_connection() -> None:
        connection = await aio_pika.connect_robust(url=settings.rabbit_url)
        logging.debug(msg=f"Установлено подключение к RabbitMQ: {settings.rabbit_url}")
        channel = await connection.channel()

        app.state.rabbit_channel = channel
        app.state.rabbit_connection = connection

    return rabbit_connection


def get_rabbit_channel(request: Request) -> AbstractChannel:
    return request.app.state.rabbit_channel


def close_rabbit_connection(app: FastAPI) -> Callable[[], Awaitable[None]]:
    async def event() -> None:
        await app.state.rabbit_connection.close()

    return event
