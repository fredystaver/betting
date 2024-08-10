from datetime import datetime
from decimal import Decimal
from typing import Sequence

from sqlalchemy import select

from core.dao import BaseDAO
from line_provider.models.events import Events


class EventsDAO(BaseDAO):
    async def get_all(self, dead_line_at: datetime) -> Sequence[Events]:
        query = select(Events)
        if dead_line_at:
            query = query.where(Events.dead_line_at > dead_line_at)
        result = await self._db_session.execute(query)
        return result.scalars().all()

    async def create(self, coefficient: Decimal, dead_line_at: datetime) -> Events:
        event = Events(coefficient=coefficient, dead_line_at=dead_line_at)
        self._db_session.add(event)
        await self._db_session.flush()
        return event

    async def get_by_id(self, event_id: int) -> Events | None:
        query = select(Events).where(Events.id == event_id)
        result = await self._db_session.execute(query)
        return result.scalar_one_or_none()
