from fastapi import APIRouter, status, Depends

from bet_maker.controllers.events import EventsController
from core.dependencies import get_controller
from core.schemas import EventsResponseSchema

router = APIRouter(
    prefix="/events",
    tags=["Events"]
)


@router.get("", status_code=status.HTTP_200_OK)
async def get_all_events(
    controller: EventsController = Depends(get_controller(EventsController))
) -> list[EventsResponseSchema]:
    return await controller.get_all()
