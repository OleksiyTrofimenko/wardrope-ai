"""Per-request context: request_id binding, one `http.request` log line, and the catch-all for unhandled errors.

It sits inside OTel's middleware (so the span and trace_id are active) and outside FastAPI's ExceptionMiddleware.
Unhandled exceptions are logged once and answered here; Starlette's ServerErrorMiddleware would re-raise them,
which makes uvicorn log a second ERROR line.
"""

import time
import uuid

import structlog
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from capsule_core.errors import internal_error

log = structlog.get_logger("capsule_core.http")


class RequestContextMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_id = uuid.uuid4().hex
        started = time.perf_counter()
        status = 500
        response_started = False

        async def send_wrapper(message: Message) -> None:
            nonlocal status, response_started
            if message["type"] == "http.response.start":
                status = message["status"]
                response_started = True
                message.setdefault("headers", []).append((b"x-request-id", request_id.encode()))
            await send(message)

        with structlog.contextvars.bound_contextvars(request_id=request_id):
            try:
                await self.app(scope, receive, send_wrapper)
            except Exception as exc:
                span = trace.get_current_span()
                span.record_exception(exc)
                span.set_status(Status(StatusCode.ERROR, type(exc).__name__))
                log.exception("http.unhandled_exception", method=scope["method"], path=scope["path"])
                if response_started:
                    # Known limit: once headers are sent (e.g. a failing streaming body) we cannot answer with a
                    # problem response, so the exception is re-raised and the server logs a second ERROR line.
                    raise
                await internal_error(scope["path"])(scope, receive, send_wrapper)
            finally:
                route = scope.get("route")
                log.info(
                    "http.request",
                    method=scope["method"],
                    route=getattr(route, "path", None),
                    status=status,
                    duration_ms=round((time.perf_counter() - started) * 1000, 3),
                )
