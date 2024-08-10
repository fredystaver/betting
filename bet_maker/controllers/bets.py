from datetime import datetime, timezone
from decimal import Decimal
from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from bet_maker.dao.bets import BetsDAO
from bet_maker.exceptions import EventIsClosed
from bet_maker.models.bets import Bets
from bet_maker.services.events import EventsService
from core.controller import BaseController


class BetsController(BaseController):
    def __init__(self, db_session: AsyncSession, *args, **kwargs):
        super().__init__(db_session, *args, **kwargs)
        self.bets_dao = BetsDAO(db_session=db_session)
        self.events_service = EventsService(self._settings)

    async def get_all(self) -> Sequence[Bets]:
        return await self.bets_dao.get_bets()

    async def create_bet(self, event_id: int, bet_sum: Decimal) -> Bets:
        event = await self.events_service.get_event_by_id(event_id=event_id)
        if event.dead_line_at < datetime.now(timezone.utc):
            raise EventIsClosed

        async with self._unit_of_work:
            return await self.bets_dao.create_bet(event_id=event_id, bet_sum=bet_sum)
