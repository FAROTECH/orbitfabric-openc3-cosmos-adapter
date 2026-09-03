from __future__ import annotations

from pathlib import Path
from typing import Any

from orbitfabric_openc3_cosmos_adapter import __version__ as adapter_version

from .io import sha256_file, write_json
from .profile import INTEGRATION_ID, INTEGRATION_SCHEMA_VERSION


RESULT_VERSION = "0.2-candidate"
ADAPTER_ID = INTEGRATION_ID
CAPABILITIES = [
    "profile_validation",
    "projection",
    "artifact_generation",
    "traceability",
]


def unavailable_operation_input(role: str, reason: str) -> dict[str, Any]:
    return {
        "role": role,
        "status": "unavailable",
        "id": None,
        "sha256": None,
        "reason": reason,
    }


def available_scenario_input(plan: dict[str, Any]) -> dict[str, Any]:
    return {
        "role": "scenario",
        "status": "available",
        "id": plan["source"]["scenario_id"],
        "sha256": plan["source"]["scenario_sha256"],
        "reason": None,
    }


def _artifact(
    *,
    output_dir: Path,
    artifact_id: str,
    kind: str,
    path: Path,
    media_type: str,
    mapping_ids: list[str],
) -> dict[str, Any]:
    return {
        "id": artifact_id,
        "kind": kind,
        "requirement": "required",
        "status": "generated",
        "path": path.resolve().relative_to(output_dir.resolve()).as_posix(),
        "media_type": media_type,
        "sha256": sha256_file(path),
        "reason": None,
        "retained_partial": False,
        "derived_from_mappings": mapping_ids,
    }


def _mapping_records(plan: dict[str, Any]) -> list[dict[str, Any]]:
    mappings: list[dict[str, Any]] = []
    atoms = {atom["id"]: atom for atom in plan["atoms"]}
    for operation in plan["operations"]:
        atom = atoms[operation["source_atom_id"]]
        source = atom.get("source")
        if not isinstance(source, dict):
            continue

        resolved = operation["resolved"]
        if operation["operation"] == "send_command":
            target_kind = "command"
            target_id = f"{resolved['target']} {resolved['command']}"
        elif operation["operation"] == "wait_telemetry":
            target_kind = "telemetry_wait"
            target_id = f"{resolved['target']} {resolved['packet']} {resolved['item']}"
        else:
            continue

        mappings.append(
            {
                "id": f"mapping.{operation['id']}",
                "sources": [{"domain": source["domain"], "id": source["id"]}],
                "profile_bindings": [operation["binding_id"]],
                "targets": [
                    {
                        "namespace": "openc3.cosmos",
                        "kind": target_kind,
                        "id": target_id,
                    }
                ],
            }
        )
    return mappings


def successful_result(
    *,
    operation: str,
    plan: dict[str, Any],
    output_dir: Path,
    plan_path: Path,
    procedure_path: Path,
    suite_path: Path,
) -> dict[str, Any]:
    mappings = _mapping_records(plan)
    mapping_ids = [record["id"] for record in mappings]
    return {
        "kind": "orbitfabric.integration_result",
        "result_version": RESULT_VERSION,
        "result": "succeeded",
        "integration": {
            "id": INTEGRATION_ID,
            "schema_version": INTEGRATION_SCHEMA_VERSION,
        },
        "adapter": {"id": ADAPTER_ID, "version": adapter_version},
        "operation": {"id": operation},
        "mission": {
            "status": "available",
            "id": plan["core_input"]["mission_id"],
            "model_version": plan["core_input"]["model_version"],
            "reason": None,
        },
        "inputs": {
            "core_input_set": {
                "status": "available",
                "kind": plan["core_input"]["kind"],
                "version": plan["core_input"]["input_set_version"],
                "sha256": plan["core_input"]["input_set_sha256"],
                "reason": None,
            },
            "profile": {
                "status": "available",
                "kind": plan["profile"]["kind"],
                "profile_version": plan["profile"]["profile_version"],
                "id": plan["profile"]["id"],
                "version": plan["profile"]["version"],
                "sha256": plan["profile"]["sha256"],
                "reason": None,
            },
            "operation_inputs": [available_scenario_input(plan)],
        },
        "capabilities": list(CAPABILITIES),
        "artifacts": [
            _artifact(
                output_dir=output_dir,
                artifact_id="verification.plan",
                kind="openc3_cosmos.verification_projection_plan",
                path=plan_path,
                media_type="application/json",
                mapping_ids=mapping_ids,
            ),
            _artifact(
                output_dir=output_dir,
                artifact_id="verification.cosmos_procedure",
                kind="openc3_cosmos.python_procedure",
                path=procedure_path,
                media_type="text/x-python",
                mapping_ids=mapping_ids,
            ),
            _artifact(
                output_dir=output_dir,
                artifact_id="verification.cosmos_suite",
                kind="openc3_cosmos.python_suite",
                path=suite_path,
                media_type="text/x-python",
                mapping_ids=mapping_ids,
            ),
        ],
        "mappings": mappings,
        "resolutions": [],
        "diagnostics": [],
        "coverage": {
            "status": "unavailable",
            "scope": {"domains": []},
            "reason": (
                "Scenario atom accounting is retained in the target-owned Verification "
                "Projection Plan; release-level Integration Coverage is analyzed separately."
            ),
            "summary": {},
            "records": [],
        },
        "evidence": [],
        "external_tools": [],
    }


def failed_result(
    *,
    operation: str,
    message: str,
    operation_inputs: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "kind": "orbitfabric.integration_result",
        "result_version": RESULT_VERSION,
        "result": "failed",
        "integration": {
            "id": INTEGRATION_ID,
            "schema_version": INTEGRATION_SCHEMA_VERSION,
        },
        "adapter": {"id": ADAPTER_ID, "version": adapter_version},
        "operation": {"id": operation},
        "mission": {
            "status": "unavailable",
            "id": None,
            "model_version": None,
            "reason": message,
        },
        "inputs": {
            "core_input_set": {
                "status": "unavailable",
                "kind": None,
                "version": None,
                "sha256": None,
                "reason": message,
            },
            "profile": {
                "status": "unavailable",
                "kind": None,
                "profile_version": None,
                "id": None,
                "version": None,
                "sha256": None,
                "reason": message,
            },
            "operation_inputs": operation_inputs,
        },
        "capabilities": [],
        "artifacts": [],
        "mappings": [],
        "resolutions": [],
        "diagnostics": [
            {
                "id": "diag-001",
                "owner": "integration",
                "producer": INTEGRATION_ID,
                "phase": "execution",
                "severity": "ERROR",
                "code": "OF-COSMOS-EXEC-001",
                "message": message,
                "sources": [],
                "profile_bindings": [],
                "targets": [],
            }
        ],
        "coverage": {
            "status": "unavailable",
            "scope": {"domains": []},
            "reason": message,
            "summary": {},
            "records": [],
        },
        "evidence": [],
        "external_tools": [],
    }


def write_result(output_dir: Path, payload: dict[str, Any]) -> Path:
    return write_json(output_dir / "integration_result.json", payload)
