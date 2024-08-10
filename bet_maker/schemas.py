from datetime import datetime

from pydantic import BaseModel, condecimal


class CreateBetRequest(BaseModel):
    bet_sum: condecimal(decimal_places=2, ge=50)
    event_id: int


class BetsResponseSchema(BaseModel):
    id: int
    event_id: int
    bet_sum: condecimal
    created_at: datetime
    status_id: int
