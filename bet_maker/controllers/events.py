from sqlalchemy.ext.asyncio import AsyncSession

from bet_maker.services.events import EventsService
from core.controller import BaseController
from core.schemas import EventsResponseSchema


class EventsController(BaseController):
    def __init__(self, db_session: AsyncSession, *args, **kwargs):
        super().__init__(db_session, *args, **kwargs)
        self.events_service = EventsService(self._settings)

    async def get_all(self) -> list[EventsResponseSchema]:
        return await self.events_service.get_all_events()
