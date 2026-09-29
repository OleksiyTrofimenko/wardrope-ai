"""Build and drive the app, in-process or in a fresh interpreter (for tests of process-level behaviour)."""

import subprocess
import sys
from collections.abc import AsyncIterator, Callable
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from pathlib import Path

import httpx
from fastapi import FastAPI
from pydantic import BaseModel

MakeClient = Callable[..., AbstractAsyncContextManager[httpx.AsyncClient]]


class ProbeBody(BaseModel):
    name: str
    size: int


def add_probe_routes(app: FastAPI) -> FastAPI:
    """Test-only routes: a templated route (AC-6), validation targets (AC-4) and a crash (AC-5)."""

    @app.get("/_probe/items/{item_id}")
    async def item(item_id: int, limit: int = 10) -> dict[str, int]:
        return {"item_id": item_id, "limit": limit}

    @app.post("/_probe/body")
    async def body(payload: ProbeBody) -> ProbeBody:
        return payload

    @app.get("/_probe/boom")
    async def boom() -> None:
        raise RuntimeError("probe exploded")

    return app


def build_app() -> FastAPI:
    from capsule_core.main import create_app  # lazy: a missing implementation fails tests, not collection

    return add_probe_routes(create_app())


@asynccontextmanager
async def running(app: FastAPI) -> AsyncIterator[httpx.AsyncClient]:
    """Runs the app's lifespan (startup/shutdown) around an httpx client bound to it."""
    async with app.router.lifespan_context(app):
        transport = httpx.ASGITransport(app=app, raise_app_exceptions=False)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            yield client


CHILD = """
import asyncio, sys
from helpers.app import build_app, running

async def main():
    async with running(build_app()) as client:
        for path in sys.argv[1:]:
            await client.get(path)

asyncio.run(main())
"""


def run_child(cwd: Path, env: dict[str, str], *paths: str) -> subprocess.CompletedProcess[str]:
    """Starts the app in a fresh interpreter and GETs `paths`. `cwd` should be empty (no stray .env)."""
    argv = [sys.executable, "-c", CHILD, *paths]
    return subprocess.run(argv, cwd=cwd, env=env, capture_output=True, text=True, timeout=60)
