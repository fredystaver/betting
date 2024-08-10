from datetime import datetime
from decimal import Decimal
from typing import Sequence

import aio_pika
from aio_pika import Channel

from core.controller import BaseController
from line_provider.dao.dao import EventsDAO
from line_provider.exceptions import EventIsNotExists
from line_provider.models.events import Events
from line_provider.schemas import EventChangeStatusMessage


class EventsController(BaseController):
    def __init__(self, db_session, *args, **kwargs):
        super().__init__(db_session, *args, **kwargs)
        self.events_dao = EventsDAO(db_session=db_session)

    async def get_all_events(self, actual_events: bool) -> Sequence[Events]:
        return await self.events_dao.get_all(dead_line_at=datetime.now() if actual_events else None)

    async def create_event(self, coefficient: Decimal, dead_line_at: datetime) -> Events:
        async with self._unit_of_work:
            return await self.events_dao.create(
                coefficient=coefficient, dead_line_at=dead_line_at
            )

    async def get_by_id(self, event_id: int) -> Events:
        if event := await self.events_dao.get_by_id(event_id=event_id):
            return event
        else:
            raise EventIsNotExists

    async def change_event(
        self,
        event_id: int,
        status: int | None,
        dead_line_at: datetime | None,
        coefficient: Decimal | None,
        rabbit_channel: Channel
    ) -> Events:
        message = None

        event = await self.get_by_id(event_id=event_id)
        async with self._unit_of_work:
            if coefficient:
                event.coefficient = coefficient
            if dead_line_at:
                event.dead_line_at = dead_line_at
            if status:
                if event.status_id != status:
                    message = EventChangeStatusMessage(event_id=event.id, status_id=status)
                    event.status_id = status
        if message:
            await self._send_change_msg(rabbit_channel=rabbit_channel, message=message)
        return event

    async def _send_change_msg(self, rabbit_channel: Channel, message: EventChangeStatusMessage | None) -> None:
        await rabbit_channel.default_exchange.publish(
            aio_pika.Message(
                body=message.json().encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            ),
            routing_key=self._settings.rabbit.queue_name,
        )
