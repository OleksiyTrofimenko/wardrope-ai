"""Structured logging: structlog -> stdlib -> one JSON object per line on stdout (console renderer in local).

Every event carries service, env, version, trace_id, span_id, ts, level, event, msg; request_id is bound by
`middleware.RequestContextMiddleware`. Existing root handlers are kept (pytest's caplog relies on it).
"""

import logging
import sys

import structlog
from opentelemetry import trace
from structlog.types import EventDict, Processor, WrappedLogger

from capsule_core.settings import Settings

_HANDLER_NAME = "capsule_core.stdout"


def current_trace_ids() -> tuple[str | None, str | None]:
    ctx = trace.get_current_span().get_span_context()
    if not ctx.is_valid:
        return None, None
    return format(ctx.trace_id, "032x"), format(ctx.span_id, "016x")


def _add_trace_ids(_: WrappedLogger, __: str, event_dict: EventDict) -> EventDict:
    trace_id, span_id = current_trace_ids()
    event_dict.setdefault("trace_id", trace_id)
    event_dict.setdefault("span_id", span_id)
    return event_dict


def _add_msg(_: WrappedLogger, __: str, event_dict: EventDict) -> EventDict:
    event_dict.setdefault("msg", event_dict.get("event"))
    return event_dict


def configure_logging(settings: Settings) -> None:
    static = {"service": settings.service_name, "env": settings.env, "version": settings.service_version}

    def add_static(_: WrappedLogger, __: str, event_dict: EventDict) -> EventDict:
        for key, value in static.items():
            event_dict.setdefault(key, value)
        return event_dict

    shared: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True, key="ts"),
        add_static,
        _add_trace_ids,
        _add_msg,
        structlog.processors.format_exc_info,
    ]
    structlog.configure(
        processors=[*shared, structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=False,
    )
    renderer: Processor = structlog.dev.ConsoleRenderer() if settings.is_local else structlog.processors.JSONRenderer()
    handler = logging.StreamHandler(sys.stdout)
    handler.set_name(_HANDLER_NAME)
    handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            foreign_pre_chain=shared,
            processors=[structlog.stdlib.ProcessorFormatter.remove_processors_meta, renderer],
        )
    )
    root = logging.getLogger()
    for existing in [h for h in root.handlers if h.get_name() == _HANDLER_NAME]:
        root.removeHandler(existing)
    root.addHandler(handler)
    root.setLevel(settings.log_level)
