from datetime import datetime

from pydantic import BaseModel, condecimal


class EventCreateRequest(BaseModel):
    coefficient: condecimal(gt=0, decimal_places=2) | None
    dead_line_at: datetime | None


class EventChangeRequest(BaseModel):
    coefficient: condecimal(gt=0, decimal_places=2) | None = None
    dead_line_at: datetime | None = None
    status_id: int | None = None
