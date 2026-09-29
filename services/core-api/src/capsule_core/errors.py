"""RFC 7807 problem details. Canonical example: every error response in core-api goes through `problem()`."""

from collections.abc import Mapping
from http import HTTPStatus
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from capsule_core.logging import current_trace_ids

PROBLEM_CONTENT_TYPE = "application/problem+json"
PROBLEM_BASE = "urn:capsule:problem:"


def problem(
    status: int,
    *,
    instance: str,
    detail: str | None = None,
    type_: str = "about:blank",
    headers: Mapping[str, str] | None = None,
    **extensions: Any,
) -> JSONResponse:
    title = HTTPStatus(status).phrase
    trace_id, _ = current_trace_ids()
    body = {
        "type": type_,
        "title": title,
        "status": status,
        "detail": detail if detail is not None else title,
        "instance": instance,
        "trace_id": trace_id,
        **extensions,
    }
    return JSONResponse(body, status_code=status, headers=headers, media_type=PROBLEM_CONTENT_TYPE)


def internal_error(instance: str) -> JSONResponse:
    return problem(500, instance=instance, type_=PROBLEM_BASE + "internal-error", detail="Unexpected server error.")


async def _http_exception(request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, StarletteHTTPException)
    return problem(exc.status_code, instance=request.url.path, detail=str(exc.detail), headers=exc.headers)


async def _validation_error(request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, RequestValidationError)
    errors = [
        {"field": ".".join(str(part) for part in err.get("loc", ())), "message": str(err.get("msg", "invalid"))}
        for err in exc.errors()
    ]
    return problem(
        422,
        instance=request.url.path,
        type_=PROBLEM_BASE + "validation-error",
        detail="Request validation failed.",
        errors=errors,
    )


def register_error_handlers(app: FastAPI) -> None:
    """Unhandled exceptions are handled in `middleware.RequestContextMiddleware` (one ERROR log, no re-raise)."""
    app.add_exception_handler(StarletteHTTPException, _http_exception)
    app.add_exception_handler(RequestValidationError, _validation_error)
