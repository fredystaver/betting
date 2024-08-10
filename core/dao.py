from typing import Generic, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

_ModelT = TypeVar("_ModelT")


class BaseDAO(Generic[_ModelT]):
    def __init__(self, db_session: AsyncSession) -> None:
        self._db_session = db_session
