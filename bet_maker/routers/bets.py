from typing import Sequence

from fastapi import APIRouter, Depends, status

from bet_maker.controllers.bets import BetsController
from bet_maker.schemas import CreateBetRequest, BetsResponseSchema
from core.dependencies import get_controller

router = APIRouter(
    prefix="/bets",
    tags=["Bets"],
)


@router.get("", status_code=status.HTTP_200_OK)
async def get_all_bets(
    controller: BetsController = Depends(get_controller(BetsController))
) -> Sequence[BetsResponseSchema]:
    return await controller.get_all()


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_bet(
    body: CreateBetRequest,
    controller: BetsController = Depends(get_controller(BetsController))
) -> BetsResponseSchema:
    return await controller.create_bet(
        event_id=body.event_id, bet_sum=body.bet_sum
    )
