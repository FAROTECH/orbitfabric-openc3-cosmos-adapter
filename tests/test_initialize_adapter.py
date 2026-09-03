from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_PACKAGE = ROOT / "src" / "orbitfabric_dummy_adapter"

pytestmark = pytest.mark.skipif(
    not TEMPLATE_PACKAGE.is_dir(),
    reason="Template-only initializer proof",
)


def _copy_template(tmp_path: Path) -> Path:
    target = tmp_path / "adapter"
    shutil.copytree(
        ROOT,
        target,
        ignore=shutil.ignore_patterns(
            ".git",
            ".venv",
            ".pytest_cache",
            ".ruff_cache",
            "__pycache__",
            "build",
            "dist",
            "generated",
            "site",
            "_orbitfabric_core",
        ),
    )
    return target


def test_initializer_separates_distribution_console_and_execution_identity(tmp_path: Path) -> None:
    target = _copy_template(tmp_path)
    command = [
        sys.executable,
        str(target / "tools" / "initialize_adapter.py"),
        "--root",
        str(target),
        "--adapter-name",
        "acme-target",
        "--python-package",
        "orbitfabric_acme_adapter",
        "--console-script",
        "of-acme",
        "--distribution-name",
        "acme-orbitfabric-adapter",
        "--adapter-id",
        "acme-orbitfabric",
    ]

    completed = subprocess.run(command, check=False, capture_output=True, text=True)
    assert completed.returncode == 0, completed.stderr

    assert not (target / "src" / "orbitfabric_dummy_adapter").exists()
    package = target / "src" / "orbitfabric_acme_adapter"
    assert package.is_dir()

    pyproject = tomllib.loads((target / "pyproject.toml").read_text(encoding="utf-8"))
    assert pyproject["project"]["name"] == "acme-orbitfabric-adapter"
    assert pyproject["project"]["scripts"] == {"of-acme": "orbitfabric_acme_adapter.cli:main"}

    manifest = json.loads((package / "integration_package.json").read_text(encoding="utf-8"))
    assert manifest["adapter"]["id"] == "acme-orbitfabric"
    assert manifest["integration"]["id"] == "acme-orbitfabric"
    assert manifest["execution"]["argv_prefix"] == ["of-acme"]

    schema_path = package / "schemas" / "profile-0.1.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    assert schema["properties"]["integration"]["properties"]["id"]["const"] == (
        "acme-orbitfabric"
    )
    assert manifest["profile_schemas"][0]["sha256"] == hashlib.sha256(
        schema_path.read_bytes()
    ).hexdigest()

    assert (target / "coverage" / "integration-coverage.md").read_text(encoding="utf-8") == (
        target / "coverage" / "coverage-template.md"
    ).read_text(encoding="utf-8")

    consistency = subprocess.run(
        [sys.executable, str(target / "tools" / "check_template_consistency.py")],
        cwd=target,
        check=False,
        capture_output=True,
        text=True,
    )
    assert consistency.returncode == 0, consistency.stderr

    initialized_tests = subprocess.run(
        [sys.executable, "-m", "pytest", "-q"],
        cwd=target,
        check=False,
        capture_output=True,
        text=True,
    )
    assert initialized_tests.returncode == 0, initialized_tests.stdout + initialized_tests.stderr
    assert "1 skipped" in initialized_tests.stdout

    repeated = subprocess.run(command, check=False, capture_output=True, text=True)
    assert repeated.returncode != 0
    assert "already be initialized" in repeated.stderr
