from datetime import datetime
from typing import Literal

from pydantic import BaseModel, condecimal


class EventCreateRequest(BaseModel):
    coefficient: condecimal(gt=0, decimal_places=2) | None
    dead_line_at: datetime | None


class EventChangeRequest(BaseModel):
    coefficient: condecimal(gt=0, decimal_places=2) | None = None
    dead_line_at: datetime | None = None
    status_id: Literal[1, 2, 3] | None = None


class EventChangeStatusMessage(BaseModel):
    event_id: int
    status_id: int
