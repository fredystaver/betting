from datetime import datetime
from decimal import Decimal
from enum import IntEnum, auto

from pydantic import BaseModel


class EventsResponseSchema(BaseModel):
    id: int
    coefficient: Decimal
    dead_line_at: datetime
    status_id: int


class EventStatusesEnum(IntEnum):
    PROCESSING = auto()
    WIN_FIRST = auto()
    WIN_SECOND = auto()


class EventMessage(BaseModel):
    event_id: int
    status_id: int
