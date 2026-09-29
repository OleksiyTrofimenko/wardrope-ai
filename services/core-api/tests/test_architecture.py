"""AC-8: layering enforced by import-linter (spec: docs/specs/foundation/E3-1-core-api-skeleton.md)."""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

SERVICE_ROOT = Path(__file__).resolve().parents[1]
LINT_IMPORTS = Path(sys.executable).parent / "lint-imports"


def lint_imports(root: Path) -> subprocess.CompletedProcess[str]:
    """Runs lint-imports with `root`'s .importlinter against `root`/src/capsule_core."""
    env = {**os.environ, "PYTHONPATH": str(root / "src")}
    return subprocess.run([str(LINT_IMPORTS)], cwd=root, env=env, capture_output=True, text=True, timeout=120)


def test_AC8_lint_imports_passes_on_skeleton() -> None:
    assert (SERVICE_ROOT / ".importlinter").is_file()
    assert (SERVICE_ROOT / "src" / "capsule_core").is_dir()
    result = lint_imports(SERVICE_ROOT)
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize(
    ("layer", "statement"),
    [
        ("repositories", "from capsule_core.api import x"),  # the case named in AC-8
        ("repositories", "from capsule_core.services import x"),
        ("services", "from capsule_core.api import x"),
        ("models", "from capsule_core.repositories import x"),
        ("models", "import fastapi"),
    ],
)
def test_AC8_reverse_import_fails_lint_imports(tmp_path: Path, layer: str, statement: str) -> None:
    shutil.copy(SERVICE_ROOT / ".importlinter", tmp_path / ".importlinter")
    shutil.copytree(SERVICE_ROOT / "src", tmp_path / "src", ignore=shutil.ignore_patterns("__pycache__"))
    (tmp_path / "src" / "capsule_core" / layer / "_violation.py").write_text(statement + "\n")
    result = lint_imports(tmp_path)
    assert result.returncode != 0, result.stdout
    assert "_violation" in result.stdout + result.stderr


def test_AC8_legitimate_layer_chain_passes(tmp_path: Path) -> None:
    shutil.copy(SERVICE_ROOT / ".importlinter", tmp_path / ".importlinter")
    shutil.copytree(SERVICE_ROOT / "src", tmp_path / "src", ignore=shutil.ignore_patterns("__pycache__"))
    pkg = tmp_path / "src" / "capsule_core"
    # The chain the spec allows: api -> services -> repositories -> models, one hop each.
    (pkg / "api" / "_chain.py").write_text("from capsule_core.services._chain import value\n")
    (pkg / "services" / "_chain.py").write_text("from capsule_core.repositories._chain import value\n")
    (pkg / "repositories" / "_chain.py").write_text("from capsule_core.models._chain import value\n")
    (pkg / "models" / "_chain.py").write_text("value = 1\n")
    result = lint_imports(tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr

    # A direct skip-level edge on top of the same chain must still fail.
    (pkg / "api" / "_skip.py").write_text("from capsule_core.models import _chain\n")
    result = lint_imports(tmp_path)
    assert result.returncode != 0, result.stdout
    assert "_skip" in result.stdout + result.stderr
