from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from uvicorn import run

from bet_maker.models.bets import Base, BetStatuses
from bet_maker.routers.bets import router as bets_router
from bet_maker.routers.events import router as events_router
from bet_maker.settings import get_settings, Settings
from core.utils import create_engine, setup_rabbit_connection, close_rabbit_connection, init_tables, insert_data


def main() -> None:
    settings = get_settings()
    run(
        app=create_app(settings=settings),
        host=settings.bet_maker.host,
        port=settings.bet_maker.port,
    )


def create_app(settings: Settings) -> FastAPI:
    app = FastAPI(title=settings.bet_maker.title)

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
    app.add_event_handler(event_type="startup", func=insert_data(engine=engine, table=BetStatuses))
    app.add_event_handler(event_type="startup", func=setup_rabbit_connection(app=app))

    app.add_event_handler(event_type="shutdown", func=engine.dispose)
    app.add_event_handler(event_type="shutdown", func=close_rabbit_connection(app=app))

    app.include_router(router=bets_router)
    app.include_router(router=events_router)
    return app
