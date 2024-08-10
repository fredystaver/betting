from abc import ABC

from pydantic_settings import BaseSettings
from sqlalchemy.ext.asyncio import AsyncSession

from core.uow import SQLUnitOfWork


class BaseController(ABC):

    def __init__(
        self,
        db_session: AsyncSession,
        settings: BaseSettings = None,
        unit_of_work: SQLUnitOfWork | None = None,
    ) -> None:
        self._settings = settings
        self._session = db_session
        self._unit_of_work = unit_of_work
