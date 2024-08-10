from datetime import datetime
from decimal import Decimal

from sqlalchemy import ForeignKey, TIMESTAMP
from sqlalchemy.orm import mapped_column, Mapped, declarative_base

Base = declarative_base()


class EventStatuses(Base):
    __tablename__ = "event_statuses"

    NEW = 1
    FINISHED_WIN = 2
    FINISHED_LOSE = 3

    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[str] = mapped_column(unique=True)


class Events(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    coefficient: Mapped[Decimal | None]
    dead_line_at: Mapped[datetime | None] = mapped_column(type_=TIMESTAMP(timezone=True))
    status_id: Mapped[int] = mapped_column(ForeignKey("event_statuses.id"), default=1)
