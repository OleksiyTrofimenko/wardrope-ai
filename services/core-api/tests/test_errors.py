"""AC-3..AC-5: RFC 7807 problem details (spec: docs/specs/foundation/E3-1-core-api-skeleton.md)."""

import httpx
import pytest
from helpers.logs import error_records, has_traceback
from helpers.problems import assert_problem


async def test_AC3_unknown_route_returns_404_problem_with_trace_id(client: httpx.AsyncClient) -> None:
    assert_problem(await client.get("/does-not-exist"), 404)


async def test_AC3_trace_id_follows_incoming_traceparent(client: httpx.AsyncClient) -> None:
    trace_id = "4bf92f3577b34da6a3ce929d0e0e4736"
    headers = {"traceparent": f"00-{trace_id}-00f067aa0ba902b7-01"}
    body = assert_problem(await client.get("/does-not-exist", headers=headers), 404)
    assert body["trace_id"] == trace_id


async def test_AC3_wrong_method_returns_405_problem(client: httpx.AsyncClient) -> None:
    assert_problem(await client.delete("/healthz"), 405)


async def test_AC4_invalid_query_param_returns_422_with_field_errors(client: httpx.AsyncClient) -> None:
    body = assert_problem(await client.get("/_probe/items/1", params={"limit": "many"}), 422)
    assert body["errors"], "errors[] must not be empty"
    for error in body["errors"]:
        assert isinstance(error["field"], str) and isinstance(error["message"], str) and error["message"]
    assert any("limit" in e["field"] for e in body["errors"])


async def test_AC4_every_missing_body_field_is_listed(client: httpx.AsyncClient) -> None:
    body = assert_problem(await client.post("/_probe/body", json={}), 422)
    fields = " ".join(e["field"] for e in body["errors"])
    assert "name" in fields and "size" in fields


async def test_AC4_malformed_json_body_returns_422_problem(client: httpx.AsyncClient) -> None:
    response = await client.post("/_probe/body", content=b"{not json", headers={"content-type": "application/json"})
    assert assert_problem(response, 422)["errors"]


async def test_AC5_unhandled_exception_returns_500_problem_without_stack_trace(client: httpx.AsyncClient) -> None:
    response = await client.get("/_probe/boom")
    assert_problem(response, 500)
    assert "Traceback" not in response.text
    assert 'File "' not in response.text


async def test_AC5_unhandled_exception_logs_one_error_with_traceback(
    client: httpx.AsyncClient, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.clear()
    await client.get("/_probe/boom")
    errors = error_records(caplog)
    assert len(errors) == 1, [r.getMessage() for r in errors]
    assert has_traceback(errors[0])
