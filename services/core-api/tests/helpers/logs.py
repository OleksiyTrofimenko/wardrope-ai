"""caplog assertions on structlog events. Assumes core-api logs via stdlib `logging` and keeps existing root
handlers (so caplog sees records); the event dict is `record.msg` (ProcessorFormatter) or JSON in the message."""

import json
import logging
from typing import Any

import pytest


def event_dict(record: logging.LogRecord) -> dict[str, Any] | None:
    if isinstance(record.msg, dict):
        return record.msg
    try:
        parsed = json.loads(record.getMessage())
    except ValueError:
        return None
    return parsed if isinstance(parsed, dict) else None


def events(caplog: pytest.LogCaptureFixture, name: str) -> list[dict[str, Any]]:
    """All structured events whose `event` equals `name`, in emission order."""
    found = (event_dict(r) for r in caplog.records)
    return [e for e in found if e is not None and e.get("event") == name]


def error_records(caplog: pytest.LogCaptureFixture) -> list[logging.LogRecord]:
    return [r for r in caplog.records if r.levelno >= logging.ERROR]


def has_traceback(record: logging.LogRecord) -> bool:
    """True when the record carries the exception: stdlib `exc_info` or structlog's `exception` field."""
    return bool(record.exc_info) or bool((event_dict(record) or {}).get("exception"))
