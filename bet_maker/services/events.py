from aiohttp import ClientSession, ClientTimeout
from fastapi import HTTPException
from pydantic_settings import BaseSettings

from core.schemas import EventsResponseSchema


class EventsService:
    def __init__(self, settings: BaseSettings):
        self._settings = settings

    async def get_all_events(self) -> list[EventsResponseSchema]:
        async with ClientSession(timeout=ClientTimeout(total=1)) as client:
            params = {"actual_events": "true"}
            response = await client.get(
                url=f"http://{self._settings.line_provider.host}:{self._settings.line_provider.port}/events",
                params=params
            )
            if response.ok:
                events = await response.json()
                return [EventsResponseSchema(**event) for event in events]
            else:
                raise HTTPException(detail=await response.json(), status_code=response.status)

    async def get_event_by_id(self, event_id: int) -> EventsResponseSchema:
        async with ClientSession(timeout=ClientTimeout(total=1)) as client:
            response = await client.get(
                url=f"http://{self._settings.line_provider.host}:{self._settings.line_provider.port}/events/{event_id}"
            )
            if response.ok:
                event = await response.json()
                return EventsResponseSchema(**event)
            else:
                raise HTTPException(detail=await response.json(), status_code=response.status)
