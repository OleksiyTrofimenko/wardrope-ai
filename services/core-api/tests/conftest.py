"""Shared fixtures (conventions set in E3-1).

`settings` sets the env the app reads; `create_app()` must read env on every call (tests build a fresh app each).
DB "down" is the default: DATABASE_URL points at a closed localhost port (instant connection refused).
`postgres_url` is a real Postgres via testcontainers; its tests are marked `integration` and skip without Docker.
"""

import os
import socket
from collections.abc import AsyncIterator, Iterator
from contextlib import asynccontextmanager

import httpx
import pytest
from helpers.app import MakeClient, build_app, running

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))


def unreachable_database_url() -> str:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    return f"postgresql+asyncpg://capsule:capsule@127.0.0.1:{port}/capsule"


@pytest.fixture
def settings(monkeypatch: pytest.MonkeyPatch) -> dict[str, str]:
    env = {"ENV": "test", "LOG_LEVEL": "INFO", "DATABASE_URL": unreachable_database_url()}
    monkeypatch.delenv("OTEL_EXPORTER_OTLP_ENDPOINT", raising=False)
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    return env


@pytest.fixture
def make_client(settings: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> MakeClient:
    """`async with make_client(**env_overrides) as client:` -> create_app() + probe routes, lifespan running."""

    @asynccontextmanager
    async def _make(**env: str) -> AsyncIterator[httpx.AsyncClient]:
        for key, value in env.items():
            monkeypatch.setenv(key, value)
        async with running(build_app()) as client:
            yield client

    return _make


@pytest.fixture
async def client(make_client: MakeClient) -> AsyncIterator[httpx.AsyncClient]:
    async with make_client() as c:
        yield c


@pytest.fixture(scope="session")
def postgres_url() -> Iterator[str]:
    docker = pytest.importorskip("docker")
    try:
        docker.from_env().ping()
    except docker.errors.DockerException as exc:
        pytest.skip(f"Docker unreachable: {exc}")
    from testcontainers.community.postgres import PostgresContainer

    with PostgresContainer("pgvector/pgvector:pg16", driver="asyncpg") as pg:
        yield pg.get_connection_url()


@pytest.fixture
def child_env(settings: dict[str, str]) -> dict[str, str]:
    """Env for `helpers.app.run_child`: the patched env plus src/ and tests/ on PYTHONPATH."""
    src = os.path.join(os.path.dirname(TESTS_DIR), "src")
    return {**os.environ, "PYTHONPATH": os.pathsep.join([src, TESTS_DIR])}
