from __future__ import annotations

import json
from importlib.resources import files
from pathlib import Path

from orbitfabric.conformance.integration_contracts import validate_result

from orbitfabric_dummy_adapter.cli import main

ROOT = Path(__file__).resolve().parents[1]


def _manifest() -> dict:
    path = files("orbitfabric_dummy_adapter").joinpath("integration_package.json")
    return json.loads(path.read_text(encoding="utf-8"))


def test_verification_projection_emits_scenario_provenance(tmp_path: Path) -> None:
    output = tmp_path / "verification"

    status = main(
        [
            "run",
            "--operation",
            "verification_projection",
            "--input-set-manifest",
            str(ROOT / "examples" / "input-set" / "integration_input_manifest.json"),
            "--profile",
            str(ROOT / "examples" / "profile.yaml"),
            "--operation-input",
            "scenario",
            str(ROOT / "examples" / "scenario.yaml"),
            "--output-dir",
            str(output),
        ]
    )

    assert status == 0
    plan = json.loads(
        (output / "dummy_verification_plan.json").read_text(encoding="utf-8")
    )
    assert plan["scenario"]["id"] == "dummy_battery_check"

    result = json.loads((output / "integration_result.json").read_text(encoding="utf-8"))
    validate_result(_manifest(), result)
    assert result["inputs"]["operation_inputs"][0]["role"] == "scenario"
    assert result["inputs"]["operation_inputs"][0]["status"] == "available"


def test_verification_projection_rejects_missing_scenario_binding(tmp_path: Path) -> None:
    output = tmp_path / "missing"

    status = main(
        [
            "run",
            "--operation",
            "verification_projection",
            "--input-set-manifest",
            str(ROOT / "examples" / "input-set" / "integration_input_manifest.json"),
            "--profile",
            str(ROOT / "examples" / "profile.yaml"),
            "--output-dir",
            str(output),
        ]
    )

    assert status == 1
    result = json.loads((output / "integration_result.json").read_text(encoding="utf-8"))
    validate_result(_manifest(), result)
    assert result["result"] == "failed"
    assert result["inputs"]["operation_inputs"][0]["status"] == "unavailable"
