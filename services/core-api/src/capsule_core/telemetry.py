"""OpenTelemetry tracer + meter providers and FastAPI instrumentation.

An SDK TracerProvider is always installed, so every request has a valid trace_id for logs and problem details.
Exporters: OTLP when OTEL_EXPORTER_OTLP_ENDPOINT is set (PR-B2), console in local (PR-B2), none in tests.
"""

import os

from fastapi import FastAPI
from opentelemetry import metrics, trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider

from capsule_core.settings import Settings

_globals_set = False


def setup_telemetry(app: FastAPI, settings: Settings) -> tuple[TracerProvider, MeterProvider]:
    global _globals_set
    # The FastAPI instrumentation emits the stable `http.server.request.duration` metric (docs/observability.md,
    # E3-1 §5) only with this opt-in; the default is the legacy `http.server.duration`. It is read once per
    # process when the first instrumentation initialises, so it must be set before `instrument_app`.
    os.environ.setdefault("OTEL_SEMCONV_STABILITY_OPT_IN", "http")

    resource = Resource.create(
        {
            "service.name": settings.service_name,
            "service.version": settings.service_version,
            "deployment.environment": settings.env,
        }
    )
    tracer_provider = TracerProvider(resource=resource)
    meter_provider = MeterProvider(resource=resource)
    if not _globals_set:  # OTel allows setting the global providers once per process.
        trace.set_tracer_provider(tracer_provider)
        metrics.set_meter_provider(meter_provider)
        _globals_set = True
    FastAPIInstrumentor.instrument_app(app, tracer_provider=tracer_provider, meter_provider=meter_provider)
    return tracer_provider, meter_provider
