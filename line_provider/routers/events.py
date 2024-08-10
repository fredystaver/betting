from typing import Sequence

from fastapi import APIRouter, Depends, Path, status

from core.dependencies import get_controller
from core.schemas import EventsResponseSchema
from line_provider.controllers.events import EventsController
from line_provider.schemas import EventCreateRequest, EventChangeRequest

router = APIRouter(
    prefix="/events",
    tags=["Events"],
)


@router.get("", status_code=status.HTTP_200_OK)
async def get_all_events(
    actual_events: bool = False,
    controller: EventsController = Depends(get_controller(EventsController))
) -> Sequence[EventsResponseSchema]:
    return await controller.get_all_events(actual_events=actual_events)


@router.get("/{event_id}", status_code=status.HTTP_200_OK)
async def get_one_event(
    event_id: int = Path(),
    controller: EventsController = Depends(get_controller(EventsController))
) -> EventsResponseSchema:
    return await controller.get_by_id(event_id=event_id)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_event(
    body: EventCreateRequest,
    controller: EventsController = Depends(get_controller(EventsController))
) -> EventsResponseSchema:
    return await controller.create_event(
        coefficient=body.coefficient, dead_line_at=body.dead_line_at
    )


@router.put("/{event_id}/", status_code=status.HTTP_201_CREATED)
async def change_event(
    body: EventChangeRequest,
    event_id: int = Path(),
    controller: EventsController = Depends(get_controller(EventsController))
) -> EventsResponseSchema:
    return await controller.change_event(
        event_id=event_id,
        status=body.status_id,
        coefficient=body.coefficient,
        dead_line_at=body.dead_line_at
    )
