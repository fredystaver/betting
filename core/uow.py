from sqlalchemy.ext.asyncio import AsyncSession


class SQLUnitOfWork:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def __aenter__(self) -> None:
        return

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_val is None:
            await self._session.commit()
