from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, condecimal


class CreateBetRequest(BaseModel):
    bet_sum: condecimal(decimal_places=2, gt=0)
    event_id: int


class BetsResponseSchema(BaseModel):
    id: int
    event_id: int
    bet_sum: Decimal
    created_at: datetime
    status_id: int
