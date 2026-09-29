"""AC-6 request log line, AC-7 JSON output + LOG_LEVEL (spec: docs/specs/foundation/E3-1-core-api-skeleton.md)."""

import json
from pathlib import Path
from typing import Any

import httpx
import pytest
from helpers.app import run_child
from helpers.logs import events

REQUEST_FIELDS = {"method", "route", "status", "duration_ms", "trace_id"}
BOUND_FIELDS = {"service", "env", "version", "trace_id", "span_id", "request_id"}


@pytest.mark.parametrize(
    ("method", "path", "status", "route"),
    [
        ("GET", "/healthz", 200, "/healthz"),
        ("GET", "/_probe/items/7", 200, "/_probe/items/{item_id}"),  # route template, not raw path
        ("GET", "/_probe/items/x", 422, "/_probe/items/{item_id}"),
        ("POST", "/_probe/body", 422, "/_probe/body"),
        ("GET", "/_probe/boom", 500, "/_probe/boom"),
        ("GET", "/does-not-exist", 404, None),  # spec does not fix `route` for unmatched paths
    ],
)
async def test_AC6_each_request_logs_exactly_one_http_request_line(
    client: httpx.AsyncClient, caplog: pytest.LogCaptureFixture, method: str, path: str, status: int, route: str | None
) -> None:
    caplog.clear()
    response = await client.request(method, path)
    assert response.status_code == status
    lines = events(caplog, "http.request")
    assert len(lines) == 1, lines
    line = lines[0]
    assert REQUEST_FIELDS <= line.keys()
    assert (line["method"], line["status"]) == (method, status)
    assert isinstance(line["duration_ms"], int | float) and line["duration_ms"] >= 0
    if route is not None:
        assert line["route"] == route
    if status >= 400:
        assert line["trace_id"] == response.json()["trace_id"]


async def test_AC6_http_request_line_carries_bound_context(
    client: httpx.AsyncClient, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.clear()
    version = (await client.get("/healthz")).json()["version"]
    (line,) = events(caplog, "http.request")
    assert BOUND_FIELDS <= line.keys()
    assert (line["env"], line["version"]) == ("test", version)
    assert line["service"] and line["request_id"]


def child_logs(tmp_path: Path, env: dict[str, str]) -> list[dict[str, Any]]:
    """GETs /healthz and /_probe/boom in a fresh process; returns stdout parsed as one JSON object per line."""
    done = run_child(tmp_path, env, "/healthz", "/_probe/boom")
    assert done.returncode == 0, done.stderr
    lines = [ln for ln in done.stdout.splitlines() if ln.strip()]
    assert lines, f"no log lines on stdout; stderr:\n{done.stderr}"
    parsed = [json.loads(ln) for ln in lines]  # fails on any non-JSON or multi-line record
    assert all(isinstance(obj, dict) for obj in parsed)
    return parsed


def test_AC7_non_local_logs_are_single_line_json(tmp_path: Path, child_env: dict[str, str]) -> None:
    logs = child_logs(tmp_path, child_env)
    assert [e.get("event") for e in logs].count("http.request") == 2
    (error,) = [e for e in logs if str(e.get("level", "")).lower() == "error"]
    assert "probe exploded" in json.dumps(error)  # the traceback is inside the single JSON line


def test_AC7_log_level_warning_drops_info_lines(tmp_path: Path, child_env: dict[str, str]) -> None:
    logs = child_logs(tmp_path, {**child_env, "LOG_LEVEL": "WARNING"})
    levels = {str(e.get("level", "")).lower() for e in logs}
    assert "info" not in levels and "debug" not in levels
    assert not [e for e in logs if e.get("event") == "http.request" and e.get("status") == 200]
    assert "error" in levels
