from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from orbitfabric.export.integration_input_set import write_integration_input_set

from orbitfabric_openc3_cosmos_adapter.adapter.cosmos_materializer import (
    materialize_python_procedure,
    materialize_python_suite,
)
from orbitfabric_openc3_cosmos_adapter.adapter.verification_plan import (
    validate_verification_plan,
)
from orbitfabric_openc3_cosmos_adapter.adapter.verification_projector import (
    project_verification_scenario,
)

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "_orbitfabric_core"
PROFILE = ROOT / "examples" / "profile.yaml"

pytestmark = pytest.mark.skipif(
    not CORE.is_dir(),
    reason="exact Core checkout is supplied by CI for integration projection tests",
)


def _scenario(tmp_path: Path) -> Path:
    mission = (CORE / "examples" / "demo-3u" / "mission").resolve()
    payload = {
        "scenario": {
            "id": "cosmos_verification_smoke",
            "name": "COSMOS verification smoke",
            "description": "Minimal canonical Scenario to COSMOS verification projection.",
        },
        "mission": {"path": str(mission)},
        "initial_state": {
            "mode": "NOMINAL",
            "telemetry": {"payload.acquisition.active": True},
        },
        "steps": [
            {"t": 1, "command": "payload.stop_acquisition"},
            {"t": 2, "expect_telemetry": {"payload.acquisition.active": False}},
        ],
    }
    path = tmp_path / "scenario.yaml"
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    return path


def _core_input(tmp_path: Path) -> Path:
    mission = CORE / "examples" / "demo-3u" / "mission"
    result = write_integration_input_set(mission, tmp_path / "core-input")
    assert result.succeeded, (result.load_result, result.lint_result, result.generation_failed)
    return result.manifest_path


def test_scenario_projects_to_resolved_cosmos_operations(tmp_path: Path) -> None:
    plan = project_verification_scenario(_scenario(tmp_path), _core_input(tmp_path), PROFILE)
    validate_verification_plan(plan)

    assert plan["status"] == "executable_subset"
    assert plan["target"]["baseline"] == "v7.3.0"
    assert plan["accounting"] == {
        "source_atoms": 5,
        "projected_atoms": 3,
        "not_projected_atoms": 2,
        "blocked_atoms": 0,
        "source_actions": 1,
        "source_expectations": 1,
        "projected_source_actions": 1,
        "projected_source_expectations": 1,
        "resolved_operations": 2,
    }

    send, wait = plan["operations"]
    assert send["operation"] == "send_command"
    assert send["resolved"] == {
        "target": "OFDEMO",
        "command": "STOP_ACQUISITION",
        "arguments": {},
    }
    assert wait["operation"] == "wait_telemetry"
    assert wait["resolved"]["packet"] == "STATUS"
    assert wait["resolved"]["item"] == "ACQUISITION_ACTIVE"
    assert wait["resolved"]["expected_value"] == 0
    assert wait["resolved"]["timeout_s"] == 5.0


def test_materializers_emit_native_cosmos_python(tmp_path: Path) -> None:
    plan = project_verification_scenario(_scenario(tmp_path), _core_input(tmp_path), PROFILE)
    procedure = materialize_python_procedure(plan, tmp_path / "verification.py")
    suite = materialize_python_suite(plan, tmp_path / "verification_suite.py")

    procedure_text = procedure.read_text(encoding="utf-8")
    suite_text = suite.read_text(encoding="utf-8")

    assert "from openc3.script import *" in procedure_text
    assert "cmd('OFDEMO STOP_ACQUISITION')" in procedure_text
    assert "wait_check('OFDEMO STATUS ACQUISITION_ACTIVE == 0', 5, type='RAW')" in procedure_text
    assert "class OrbitFabricVerificationGroup(Group):" in suite_text
    assert "class OrbitFabricVerificationSuite(Suite):" in suite_text


def test_missing_telemetry_binding_blocks_instead_of_dropping_intent(tmp_path: Path) -> None:
    profile = yaml.safe_load(PROFILE.read_text(encoding="utf-8"))
    profile["bindings"] = [
        binding
        for binding in profile["bindings"]
        if binding["sources"][0] != {
            "domain": "telemetry",
            "id": "payload.acquisition.active",
        }
    ]
    profile_path = tmp_path / "profile.yaml"
    profile_path.write_text(yaml.safe_dump(profile, sort_keys=False), encoding="utf-8")

    plan = project_verification_scenario(
        _scenario(tmp_path),
        _core_input(tmp_path),
        profile_path,
    )
    validate_verification_plan(plan)

    assert plan["status"] == "blocked"
    blocked = [atom for atom in plan["atoms"] if atom["disposition"] == "blocked"]
    assert len(blocked) == 1
    assert blocked[0]["kind"] == "expect_telemetry"
    assert plan["accounting"]["resolved_operations"] == 1
