from datetime import datetime
from decimal import Decimal

from sqlalchemy import ForeignKey, TIMESTAMP
from sqlalchemy.orm import mapped_column, Mapped, declarative_base

Base = declarative_base()


class BetStatuses(Base):
    __tablename__ = "bet_statuses"

    NEW = 1
    FINISHED_WIN = 2
    FINISHED_LOSE = 3

    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[str] = mapped_column(unique=True)


class Bets(Base):
    __tablename__ = "bets"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(nullable=False)
    bet_sum: Mapped[Decimal] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(type_=TIMESTAMP(timezone=True), default=datetime.utcnow())
    status_id: Mapped[int] = mapped_column(ForeignKey("bet_statuses.id"))
