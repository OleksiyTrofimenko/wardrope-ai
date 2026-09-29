"""AC-1 /healthz, AC-2 /readyz (spec: docs/specs/foundation/E3-1-core-api-skeleton.md)."""

from collections.abc import Iterator

import httpx
import pytest
from helpers.app import MakeClient
from helpers.problems import assert_problem
from sqlalchemy import event
from sqlalchemy.pool import Pool


@pytest.fixture
def db_checkouts() -> Iterator[list[object]]:
    """Records every connection checkout from any SQLAlchemy pool while the test runs."""
    seen: list[object] = []

    def on_checkout(*args: object) -> None:
        seen.append(args)

    event.listen(Pool, "checkout", on_checkout)
    yield seen
    event.remove(Pool, "checkout", on_checkout)


async def test_AC1_healthz_ok_with_version_while_database_is_down(
    client: httpx.AsyncClient, db_checkouts: list[object]
) -> None:
    response = await client.get("/healthz")  # default settings: DATABASE_URL points at a closed port
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert isinstance(body["version"], str) and body["version"]
    assert db_checkouts == []


@pytest.mark.integration
async def test_AC1_healthz_does_not_touch_reachable_database(
    make_client: MakeClient, postgres_url: str, db_checkouts: list[object]
) -> None:
    async with make_client(DATABASE_URL=postgres_url) as client:
        db_checkouts.clear()  # ignore anything startup may do
        assert (await client.get("/healthz")).status_code == 200
    assert db_checkouts == []


@pytest.mark.integration
async def test_AC2_readyz_ok_when_postgres_reachable(make_client: MakeClient, postgres_url: str) -> None:
    async with make_client(DATABASE_URL=postgres_url) as client:
        assert (await client.get("/readyz")).status_code == 200


async def test_AC2_readyz_503_problem_when_postgres_unreachable(client: httpx.AsyncClient) -> None:
    # Also proves lifespan startup tolerates a down DB: the `client` fixture already ran it.
    assert_problem(await client.get("/readyz"), 503)
