from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from tools.build_native_runtime_evidence import (
    EVIDENCE_KIND,
    EXPECTED_COSMOS_PROJECT_COMMIT,
    build_evidence,
)
from tools.validate_cosmos_ctrf import (
    CtrfValidationError,
    extract_ctrf_payload,
    validate_single_test_pass,
)

ROOT = Path(__file__).resolve().parents[1]


def test_native_acceptance_shell_is_syntactically_valid() -> None:
    subprocess.run(
        ["bash", "-n", str(ROOT / "tools" / "run_native_cosmos_acceptance.sh")],
        check=True,
    )


def test_ofdemo_fixture_matches_canonical_projection_profile() -> None:
    plugin = (ROOT / "acceptance" / "cosmos" / "plugin-overlay" / "plugin.txt.in").read_text(
        encoding="utf-8"
    )
    command = (
        ROOT
        / "acceptance"
        / "cosmos"
        / "plugin-overlay"
        / "targets"
        / "OFDEMO"
        / "cmd_tlm"
        / "cmd.txt"
    ).read_text(encoding="utf-8")
    telemetry = (
        ROOT
        / "acceptance"
        / "cosmos"
        / "plugin-overlay"
        / "targets"
        / "OFDEMO"
        / "cmd_tlm"
        / "tlm.txt"
    ).read_text(encoding="utf-8")

    assert "TARGET OFDEMO" in plugin
    assert plugin.count("__OFDEMO_HOST__") == 1
    assert "COMMAND OFDEMO STOP_ACQUISITION" in command
    assert "TELEMETRY OFDEMO STATUS" in telemetry
    assert "ACQUISITION_ACTIVE" in telemetry
    assert "OFPOC" not in plugin + command + telemetry


def test_ctrf_extraction_is_fail_closed() -> None:
    payload = {
        "results": {
            "summary": {
                "tests": 1,
                "passed": 1,
                "failed": 0,
                "skipped": 0,
            }
        }
    }
    raw = "transport noise\n" + json.dumps(payload) + "\nwrapper noise\n"

    extracted = extract_ctrf_payload(raw)
    validate_single_test_pass(extracted)

    with pytest.raises(CtrfValidationError, match="exactly one CTRF"):
        extract_ctrf_payload(raw + json.dumps(payload))


def test_native_runtime_evidence_joins_canonical_provenance(tmp_path: Path) -> None:
    result = {
        "result": "succeeded",
        "operation": {"id": "verification_projection"},
        "adapter": {"id": "orbitfabric-openc3-cosmos", "version": "0.1.0.dev0"},
    }
    plan = {
        "kind": "orbitfabric.openc3_cosmos.verification_projection_plan",
        "plan_version": "0.1-candidate",
        "status": "executable_subset",
        "integration": {"id": "orbitfabric-openc3-cosmos"},
        "target": {"baseline": "v7.3.0", "target_name": "OFDEMO"},
        "source": {"scenario_id": "cosmos_native_acceptance", "scenario_sha256": "1" * 64},
        "core_input": {
            "kind": "orbitfabric.integration_input_set",
            "input_set_version": "0.1-candidate",
            "input_set_sha256": "2" * 64,
            "mission_id": "demo-3u",
            "model_version": "0.1.0",
        },
        "profile": {"id": "openc3-cosmos-demo-3u", "version": "0.1.0", "sha256": "3" * 64},
        "operations": [
            {"id": "op-0001", "source_atom_id": "atom-0004"},
            {"id": "op-0002", "source_atom_id": "atom-0005"},
        ],
    }
    ctrf = {
        "results": {
            "summary": {"tests": 1, "passed": 1, "failed": 0, "skipped": 0}
        }
    }
    baseline = {
        "adapter_source_commit": "4" * 40,
        "cosmos_project_commit": EXPECTED_COSMOS_PROJECT_COMMIT,
        "cosmos_version": "v7.3.0",
        "plugin_version": "0.1.0",
        "simulator_host": "host.docker.internal",
        "suite": "OrbitFabricVerificationSuite",
        "group": "OrbitFabricVerificationGroup",
        "script": "test_scenario",
    }
    simulator_records = [
        {"event": "command_received", "command": "STOP_ACQUISITION"},
        {"event": "telemetry_sent", "packet": "STATUS", "acquisition_active": False},
    ]

    paths = {
        "integration_result": tmp_path / "integration-result.json",
        "plan": tmp_path / "plan.json",
        "procedure": tmp_path / "verification.py",
        "suite": tmp_path / "verification_suite.py",
        "ctrf": tmp_path / "ctrf.json",
        "simulator": tmp_path / "simulator.jsonl",
        "baseline": tmp_path / "runtime-baseline.json",
        "wheel": tmp_path / "adapter.whl",
    }
    paths["integration_result"].write_text(json.dumps(result), encoding="utf-8")
    paths["plan"].write_text(json.dumps(plan), encoding="utf-8")
    paths["procedure"].write_text("cmd('OFDEMO STOP_ACQUISITION')\n", encoding="utf-8")
    paths["suite"].write_text("class OrbitFabricVerificationSuite: pass\n", encoding="utf-8")
    paths["ctrf"].write_text(json.dumps(ctrf), encoding="utf-8")
    paths["simulator"].write_text(
        "\n".join(json.dumps(item) for item in simulator_records) + "\n",
        encoding="utf-8",
    )
    paths["baseline"].write_text(json.dumps(baseline), encoding="utf-8")
    paths["wheel"].write_bytes(b"wheel-bytes")

    evidence = build_evidence(
        integration_result_path=paths["integration_result"],
        plan_path=paths["plan"],
        procedure_path=paths["procedure"],
        suite_path=paths["suite"],
        ctrf_path=paths["ctrf"],
        simulator_log_path=paths["simulator"],
        runtime_baseline_path=paths["baseline"],
        wheel_path=paths["wheel"],
    )

    assert evidence["kind"] == EVIDENCE_KIND
    assert evidence["status"] == "passed"
    assert evidence["adapter"]["id"] == "orbitfabric-openc3-cosmos"
    assert evidence["target"]["fixture_target"] == "OFDEMO"
    assert evidence["execution"]["ctrf_summary"]["passed"] == 1
