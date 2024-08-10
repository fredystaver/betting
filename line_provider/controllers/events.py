from datetime import datetime
from decimal import Decimal
from typing import Sequence

from core.controller import BaseController
from line_provider.dao.dao import EventsDAO
from line_provider.exceptions import EventIsNotExists
from line_provider.models.events import Events, EventStatuses


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
        status: str | None,
        dead_line_at: datetime | None,
        coefficient: Decimal | None
    ) -> Events:
        event = await self.get_by_id(event_id=event_id)
        async with self._unit_of_work:
            if coefficient:
                event.coefficient = coefficient
            if dead_line_at:
                event.dead_line_at = dead_line_at
            if status:
                event.status = EventStatuses.status
        return event
