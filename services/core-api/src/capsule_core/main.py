"""App factory. Run: `uvicorn capsule_core.main:create_app --factory --no-access-log`."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI

from capsule_core.api import health
from capsule_core.db.engine import create_engine, create_sessionmaker
from capsule_core.errors import register_error_handlers
from capsule_core.logging import configure_logging
from capsule_core.middleware import RequestContextMiddleware
from capsule_core.settings import load_settings
from capsule_core.telemetry import setup_telemetry

log = structlog.get_logger("capsule_core.app")


def create_app() -> FastAPI:
    settings = load_settings()
    configure_logging(settings)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        engine = create_engine(settings)
        app.state.engine = engine
        app.state.sessionmaker = create_sessionmaker(engine)
        log.info("app.startup")
        try:
            yield
        finally:
            await engine.dispose()
            tracer_provider.shutdown()
            meter_provider.shutdown()
            log.info("app.shutdown")

    local = settings.is_local
    app = FastAPI(
        title="capsule core-api",
        version=settings.service_version,
        debug=local,
        docs_url="/docs" if local else None,
        redoc_url="/redoc" if local else None,
        openapi_url="/openapi.json" if local else None,
        lifespan=lifespan,
    )
    app.state.settings = settings
    register_error_handlers(app)
    app.add_middleware(RequestContextMiddleware)
    app.include_router(health.router)
    tracer_provider, meter_provider = setup_telemetry(app, settings)
    return app
