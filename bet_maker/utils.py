import json
from typing import Callable, Awaitable

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
