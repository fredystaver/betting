from decimal import Decimal
from typing import Sequence

from sqlalchemy import select

from bet_maker.models.bets import Bets, BetStatuses
from core.dao import BaseDAO


class BetsDAO(BaseDAO):

    async def get_bets(self, event_id: int | None = None) -> Sequence[Bets]:
        query = select(Bets)
        if event_id:
            query = query.where(Bets.event_id == event_id)
        result = await self._db_session.execute(query)
        return result.scalars().fetchall()

    async def create_bet(self, event_id: int, bet_sum: Decimal) -> Bets:
        bet = Bets(event_id=event_id, bet_sum=bet_sum, status_id=BetStatuses.NEW)
        self._db_session.add(bet)
        await self._db_session.flush()
        return bet
