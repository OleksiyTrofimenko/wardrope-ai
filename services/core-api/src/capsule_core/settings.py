"""Typed settings read from the environment. Missing required values fail startup with a clear message."""

from importlib.metadata import PackageNotFoundError, version
from typing import Literal

from pydantic import Field, SecretStr, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


def _package_version() -> str:
    try:
        return version("capsule-core")
    except PackageNotFoundError:
        return "0.0.0+unknown"


class SettingsError(RuntimeError):
    """Raised when the environment does not provide a valid configuration."""


class Settings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=False, extra="ignore")

    env: Literal["local", "test", "dev", "staging", "prod"]
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    database_url: SecretStr
    service_name: str = "core-api"
    service_version: str = Field(default_factory=_package_version)
    otel_exporter_otlp_endpoint: str | None = None
    readyz_timeout_s: float = 2.0

    @property
    def is_local(self) -> bool:
        return self.env == "local"


def load_settings() -> Settings:
    """Reads the environment on every call (no cache): tests and workers build fresh apps."""
    try:
        return Settings()  # type: ignore[call-arg]  # required fields come from the environment
    except ValidationError as exc:
        problems = ", ".join(f"{'.'.join(str(p) for p in err['loc']).upper()} ({err['msg']})" for err in exc.errors())
        raise SettingsError(f"Invalid configuration, check environment variables: {problems}") from None
