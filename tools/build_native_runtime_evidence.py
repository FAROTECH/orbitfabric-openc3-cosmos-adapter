from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

EVIDENCE_KIND = "orbitfabric.openc3_cosmos.native_runtime_evidence"
EVIDENCE_VERSION = "0.1-candidate"
EXPECTED_ADAPTER_ID = "orbitfabric-openc3-cosmos"
EXPECTED_COSMOS_VERSION = "v7.3.0"
EXPECTED_COSMOS_PROJECT_COMMIT = "9eb454f06fe0113d05aa6945d88b627155a2aa47"
EXPECTED_FIXTURE_TARGET = "OFDEMO"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {path}")
    return payload


def load_json_lines(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        payload = json.loads(line)
        if not isinstance(payload, dict):
            raise ValueError(f"expected JSON object at {path}:{line_number}")
        records.append(payload)
    return records


def build_evidence(
    *,
    integration_result_path: Path,
    plan_path: Path,
    procedure_path: Path,
    suite_path: Path,
    ctrf_path: Path,
    simulator_log_path: Path,
    runtime_baseline_path: Path,
    wheel_path: Path,
) -> dict[str, Any]:
    result = load_json(integration_result_path)
    plan = load_json(plan_path)
    ctrf = load_json(ctrf_path)
    baseline = load_json(runtime_baseline_path)
    simulator_records = load_json_lines(simulator_log_path)

    if result.get("result") != "succeeded":
        raise ValueError("Integration Result is not succeeded")
    if result.get("operation", {}).get("id") != "verification_projection":
        raise ValueError("Integration Result operation is not verification_projection")
    if result.get("adapter", {}).get("id") != EXPECTED_ADAPTER_ID:
        raise ValueError("Integration Result adapter identity is not canonical")
    if plan.get("status") != "executable_subset":
        raise ValueError("Verification Projection Plan is not executable_subset")
    if plan.get("integration", {}).get("id") != EXPECTED_ADAPTER_ID:
        raise ValueError("Verification Projection Plan integration identity is not canonical")
    if plan.get("target", {}).get("baseline") != EXPECTED_COSMOS_VERSION:
        raise ValueError("Verification Projection Plan does not target COSMOS v7.3.0")
    if plan.get("target", {}).get("target_name") != EXPECTED_FIXTURE_TARGET:
        raise ValueError("Verification Projection Plan does not target OFDEMO fixture")
    if baseline.get("cosmos_version") != EXPECTED_COSMOS_VERSION:
        raise ValueError("runtime baseline does not identify COSMOS v7.3.0")
    if baseline.get("cosmos_project_commit") != EXPECTED_COSMOS_PROJECT_COMMIT:
        raise ValueError("runtime baseline COSMOS project commit is not the validated pin")

    source_commit = baseline.get("adapter_source_commit")
    if not isinstance(source_commit, str) or len(source_commit) != 40:
        raise ValueError("runtime baseline adapter_source_commit is missing or malformed")

    summary = ctrf.get("results", {}).get("summary")
    if not isinstance(summary, dict):
        raise ValueError("runtime CTRF has no results.summary")
    expected = {"tests": 1, "passed": 1, "failed": 0}
    actual = {key: summary.get(key) for key in expected}
    if actual != expected:
        raise ValueError(f"runtime CTRF does not represent a one-test PASS: {summary}")

    command_events = [
        record
        for record in simulator_records
        if record.get("event") == "command_received"
        and record.get("command") == "STOP_ACQUISITION"
    ]
    telemetry_events = [
        record
        for record in simulator_records
        if record.get("event") == "telemetry_sent"
        and record.get("packet") == "STATUS"
        and record.get("acquisition_active") is False
    ]
    if not command_events:
        raise ValueError("runtime evidence has no STOP_ACQUISITION command_received event")
    if not telemetry_events:
        raise ValueError("runtime evidence has no inactive STATUS telemetry_sent event")

    operations = plan.get("operations")
    if not isinstance(operations, list) or len(operations) != 2:
        raise ValueError("expected exactly two projected verification operations")

    return {
        "kind": EVIDENCE_KIND,
        "evidence_version": EVIDENCE_VERSION,
        "status": "passed",
        "adapter": {
            "id": result["adapter"]["id"],
            "version": result["adapter"]["version"],
            "source_commit": source_commit,
            "wheel_sha256": sha256_file(wheel_path),
        },
        "source": {
            "scenario_id": plan["source"]["scenario_id"],
            "scenario_sha256": plan["source"]["scenario_sha256"],
        },
        "core_input": {
            "kind": plan["core_input"]["kind"],
            "input_set_version": plan["core_input"]["input_set_version"],
            "input_set_sha256": plan["core_input"]["input_set_sha256"],
            "mission_id": plan["core_input"]["mission_id"],
            "model_version": plan["core_input"]["model_version"],
        },
        "profile": {
            "id": plan["profile"]["id"],
            "version": plan["profile"]["version"],
            "sha256": plan["profile"]["sha256"],
        },
        "projection": {
            "plan_kind": plan["kind"],
            "plan_version": plan["plan_version"],
            "plan_sha256": sha256_file(plan_path),
            "operation_ids": [operation["id"] for operation in operations],
            "source_atom_ids": [operation["source_atom_id"] for operation in operations],
            "integration_result_sha256": sha256_file(integration_result_path),
        },
        "materialization": {
            "procedure_sha256": sha256_file(procedure_path),
            "suite_sha256": sha256_file(suite_path),
        },
        "target": {
            "ecosystem": "OpenC3 COSMOS",
            "cosmos_version": baseline["cosmos_version"],
            "cosmos_project_commit": baseline["cosmos_project_commit"],
            "fixture_target": EXPECTED_FIXTURE_TARGET,
            "plugin_version": baseline["plugin_version"],
            "simulator_host": baseline["simulator_host"],
        },
        "execution": {
            "suite": baseline["suite"],
            "group": baseline["group"],
            "script": baseline["script"],
            "ctrf_sha256": sha256_file(ctrf_path),
            "ctrf_summary": {
                "tests": summary.get("tests"),
                "passed": summary.get("passed"),
                "failed": summary.get("failed"),
                "skipped": summary.get("skipped", 0),
            },
            "external_target": {
                "command_events": command_events,
                "telemetry_events": telemetry_events,
                "simulator_log_sha256": sha256_file(simulator_log_path),
            },
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build adapter-owned native OpenC3 COSMOS runtime acceptance evidence."
    )
    parser.add_argument("--integration-result", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--procedure", type=Path, required=True)
    parser.add_argument("--suite", type=Path, required=True)
    parser.add_argument("--ctrf", type=Path, required=True)
    parser.add_argument("--simulator-log", type=Path, required=True)
    parser.add_argument("--runtime-baseline", type=Path, required=True)
    parser.add_argument("--wheel", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    payload = build_evidence(
        integration_result_path=args.integration_result,
        plan_path=args.plan,
        procedure_path=args.procedure,
        suite_path=args.suite,
        ctrf_path=args.ctrf,
        simulator_log_path=args.simulator_log,
        runtime_baseline_path=args.runtime_baseline,
        wheel_path=args.wheel,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(args.output.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
