from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from uvicorn import run

from core.utils import create_engine, setup_rabbit_connection, close_rabbit_connection, init_tables, insert_data
from line_provider.models.events import Base, EventStatuses
from line_provider.routers.events import router as events_router
from line_provider.settings import get_settings, Settings


def main() -> None:
    settings = get_settings()
    run(
        app=create_app(settings=settings),
        host=settings.line_provider.host,
        port=settings.line_provider.port,
    )


def create_app(settings: Settings) -> FastAPI:
    app = FastAPI(title=settings.line_provider.title)

    app.add_middleware(
        CORSMiddleware,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    engine, session_maker = create_engine(settings.postgres)

    app.state._settings = settings
    app.state.session_maker = session_maker

    app.add_event_handler(event_type="startup", func=init_tables(engine=engine, base=Base))
    app.add_event_handler(event_type="startup", func=insert_data(engine=engine, table=EventStatuses))
    app.add_event_handler(event_type="startup", func=setup_rabbit_connection(app=app))

    app.add_event_handler(event_type="shutdown", func=engine.dispose)
    app.add_event_handler(event_type="shutdown", func=close_rabbit_connection(app=app))

    app.include_router(router=events_router)
    return app
