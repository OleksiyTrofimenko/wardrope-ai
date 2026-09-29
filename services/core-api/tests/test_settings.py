"""AC-9 fail-fast settings, §5 security NFR (spec: docs/specs/foundation/E3-1-core-api-skeleton.md)."""

import re
from pathlib import Path

import httpx
import pytest
from helpers.app import run_child


def test_AC9_starts_with_required_settings(tmp_path: Path, child_env: dict[str, str]) -> None:
    result = run_child(tmp_path, child_env, "/healthz")
    assert result.returncode == 0, result.stderr


def test_AC9_missing_database_url_fails_startup_naming_the_setting(tmp_path: Path, child_env: dict[str, str]) -> None:
    env = {k: v for k, v in child_env.items() if k != "DATABASE_URL"}
    result = run_child(tmp_path, env, "/healthz")
    assert result.returncode != 0
    assert "DATABASE_URL" in (result.stdout + result.stderr).upper()


def test_AC9_missing_env_fails_startup_naming_the_setting(tmp_path: Path, child_env: dict[str, str]) -> None:
    env = {k: v for k, v in child_env.items() if k != "ENV"}
    result = run_child(tmp_path, env, "/healthz")
    assert result.returncode != 0
    # Word-boundary match: a bare substring check would also hit ".venv" / "environ" in any traceback.
    assert re.search(r"\bENV\b", (result.stdout + result.stderr).upper())


@pytest.mark.parametrize("path", ["/docs", "/redoc"])
async def test_NFR_docs_ui_disabled_outside_local(client: httpx.AsyncClient, path: str) -> None:
    assert (await client.get(path)).status_code == 404
