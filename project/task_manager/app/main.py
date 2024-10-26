import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import uvloop
from fastapi import FastAPI

from app.common.infrastructure.logging import setup_logging
from app.infrastrucrute.di.container import DIContainer
from app.presentation.api.middleware.headers import HeadersMiddleware
from app.presentation.api import router as api_router

from app.database import Database, Base
from settings.config import AppSettings, get_settings

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


class Application:
    def __init__(self) -> None:
        settings = get_settings()

        self.app = FastAPI(
            title="Task manager API",
            description="Python API for task manager service",
            lifespan=lifespan,
            openapi_url="/openapi.json",
            debug=settings.DEBUG,

        )
        self.app.state.settings = settings
        self.settings = settings

        self.app.include_router(api_router, prefix="/api")
        self.create_database_pool(settings)
        self.create_di_container()

        setup_logging()

        self.app.add_middleware(HeadersMiddleware)

    def create_database_pool(self, settings: AppSettings) -> None:

        db = Database(url=settings.DATABASE_URL, debug=settings.DEBUG)
        self.app.state.database = db

    def create_di_container(self) -> None:
        container = DIContainer()
        container.wire(packages=["app", __name__])
        self.app.state.container = container


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    async with app.state.database.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        yield


def get_app() -> FastAPI:
    return Application().app


if __name__ == "__main__":
    import uvicorn

    app = get_app()
    host = app.state.settings.APP_HOST
    port = app.state.settings.APP_PORT

    uvicorn.run(app, host=host, port=port)

