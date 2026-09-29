"""RFC 7807 problem-details assertion shared by the error-path tests."""

import re
from typing import Any

import httpx

PROBLEM_FIELDS = {"type", "title", "status", "detail", "instance", "trace_id"}
TRACE_ID = re.compile(r"^(?!0{32})[0-9a-f]{32}$")  # W3C / OTel trace id, never the invalid all-zero id


def assert_problem(response: httpx.Response, status: int) -> dict[str, Any]:
    assert response.status_code == status
    assert response.headers["content-type"].startswith("application/problem+json")
    body: dict[str, Any] = response.json()
    assert PROBLEM_FIELDS <= body.keys()
    assert body["status"] == status
    assert TRACE_ID.match(body["trace_id"]), body["trace_id"]
    return body
