from typing import Callable, TypeVar, Type, Awaitable, AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from bet_maker.settings import Settings, get_settings
from core.controller import BaseController
from core.uow import SQLUnitOfWork

Controller = TypeVar("Controller", bound=BaseController)


async def get_db_session(
    request: Request
) -> AsyncGenerator[AsyncSession, None]:
    async with request.app.state.session_maker() as session:
        yield session


def get_controller(
    controller_class: Type[Controller]
) -> Callable[[AsyncSession], Awaitable[Controller]]:
    async def _get_controller(
        session: AsyncSession = Depends(get_db_session),
        settings: Settings = Depends(get_settings)
    ) -> Controller:
        return controller_class(
            db_session=session,
            settings=settings,
            unit_of_work=SQLUnitOfWork(session),
        )

    return _get_controller
