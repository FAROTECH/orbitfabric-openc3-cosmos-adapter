from __future__ import annotations

import json
from importlib.resources import files
from pathlib import Path

import yaml
from orbitfabric.conformance.integration_contracts import validate_result

from orbitfabric_dummy_adapter.cli import main

ROOT = Path(__file__).resolve().parents[1]


def _manifest() -> dict:
    path = files("orbitfabric_dummy_adapter").joinpath("integration_package.json")
    return json.loads(path.read_text(encoding="utf-8"))


def test_project_operation_emits_conformant_result(tmp_path: Path) -> None:
    output = tmp_path / "project"

    status = main(
        [
            "run",
            "--operation",
            "project",
            "--input-set-manifest",
            str(ROOT / "examples" / "input-set" / "integration_input_manifest.json"),
            "--profile",
            str(ROOT / "examples" / "profile.yaml"),
            "--output-dir",
            str(output),
        ]
    )

    assert status == 0
    projection = json.loads((output / "dummy_projection.json").read_text(encoding="utf-8"))
    assert projection["telemetry"] == [
        {
            "display_name": "Battery Voltage",
            "source_id": "eps.battery.voltage",
            "target_name": "BATTERY_VOLTAGE",
        }
    ]

    result = json.loads((output / "integration_result.json").read_text(encoding="utf-8"))
    validate_result(_manifest(), result)
    assert result["result"] == "succeeded"
    assert result["operation"]["id"] == "project"
    assert result["inputs"]["operation_inputs"] == []
    assert result["mappings"][0]["status"] == "projected"
    assert result["coverage"]["summary"]["projected_mappings"] == 1
    assert result["coverage"]["summary"]["intentionally_not_projected_mappings"] == 0


def test_project_operation_retains_intentional_non_projection(tmp_path: Path) -> None:
    profile = yaml.safe_load((ROOT / "examples" / "profile.yaml").read_text(encoding="utf-8"))
    binding = profile["bindings"][0]
    binding["intent"] = "do_not_project"
    binding["reason"] = "The target intentionally omits this source in this profile."
    binding.pop("config", None)

    profile_path = tmp_path / "profile.yaml"
    profile_path.write_text(yaml.safe_dump(profile, sort_keys=False), encoding="utf-8")
    output = tmp_path / "not-projected"

    status = main(
        [
            "run",
            "--operation",
            "project",
            "--input-set-manifest",
            str(ROOT / "examples" / "input-set" / "integration_input_manifest.json"),
            "--profile",
            str(profile_path),
            "--output-dir",
            str(output),
        ]
    )

    assert status == 0
    projection = json.loads((output / "dummy_projection.json").read_text(encoding="utf-8"))
    assert projection["telemetry"] == []

    result = json.loads((output / "integration_result.json").read_text(encoding="utf-8"))
    validate_result(_manifest(), result)
    assert result["mappings"] == [
        {
            "id": "telemetry.battery_voltage",
            "status": "intentionally_not_projected",
            "source": {"domain": "telemetry", "id": "eps.battery.voltage"},
            "reason": "The target intentionally omits this source in this profile.",
        }
    ]
    assert result["coverage"]["summary"]["projected_mappings"] == 0
    assert result["coverage"]["summary"]["intentionally_not_projected_mappings"] == 1
