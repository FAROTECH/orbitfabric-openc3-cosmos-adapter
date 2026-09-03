from __future__ import annotations

from pathlib import Path
from typing import Any

from .constants import (
    ADAPTER_ID,
    ADAPTER_VERSION,
    INTEGRATION_ID,
    INTEGRATION_SCHEMA_VERSION,
    RESULT_VERSION,
)
from .io import sha256_file, write_json


def _profile_provenance(profile: dict[str, Any], profile_path: Path) -> dict[str, Any]:
    return {
        "status": "available",
        "kind": profile["kind"],
        "profile_version": profile["profile_version"],
        "id": profile["profile"]["id"],
        "version": profile["profile"]["version"],
        "sha256": sha256_file(profile_path),
        "reason": None,
    }


def _mapping_summary(mappings: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "projected_mappings": sum(item.get("status") == "projected" for item in mappings),
        "intentionally_not_projected_mappings": sum(
            item.get("status") == "intentionally_not_projected" for item in mappings
        ),
    }


def successful_result(
    *,
    operation: str,
    input_manifest: dict[str, Any],
    input_manifest_path: Path,
    profile: dict[str, Any],
    profile_path: Path,
    artifacts: list[dict[str, Any]],
    mappings: list[dict[str, Any]],
    operation_inputs: list[dict[str, Any]],
) -> dict[str, Any]:
    mission = input_manifest.get("mission") or {}
    summary = {"generated_artifacts": len(artifacts), **_mapping_summary(mappings)}
    return {
        "kind": "orbitfabric.integration_result",
        "result_version": RESULT_VERSION,
        "result": "succeeded",
        "integration": {
            "id": INTEGRATION_ID,
            "schema_version": INTEGRATION_SCHEMA_VERSION,
        },
        "adapter": {"id": ADAPTER_ID, "version": ADAPTER_VERSION},
        "operation": {"id": operation},
        "mission": {
            "status": "available",
            "id": mission.get("id"),
            "model_version": mission.get("model_version"),
            "reason": None,
        },
        "inputs": {
            "core_input_set": {
                "status": "available",
                "kind": input_manifest["kind"],
                "version": input_manifest["input_set_version"],
                "sha256": sha256_file(input_manifest_path),
                "reason": None,
            },
            "profile": _profile_provenance(profile, profile_path),
            "operation_inputs": operation_inputs,
        },
        "capabilities": ["projection"],
        "artifacts": artifacts,
        "mappings": mappings,
        "resolutions": [],
        "diagnostics": [],
        "coverage": {
            "status": "available",
            "scope": {"domains": ["telemetry"] if operation == "project" else ["scenario"]},
            "summary": summary,
            "records": [],
        },
        "evidence": [],
        "external_tools": [],
    }


def failed_result(operation: str, message: str, *, scenario_role: bool) -> dict[str, Any]:
    operation_inputs = []
    if scenario_role:
        operation_inputs.append(
            {
                "role": "scenario",
                "status": "unavailable",
                "id": None,
                "sha256": None,
                "reason": message,
            }
        )
    return {
        "kind": "orbitfabric.integration_result",
        "result_version": RESULT_VERSION,
        "result": "failed",
        "integration": {
            "id": INTEGRATION_ID,
            "schema_version": INTEGRATION_SCHEMA_VERSION,
        },
        "adapter": {"id": ADAPTER_ID, "version": ADAPTER_VERSION},
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
                "severity": "ERROR",
                "code": "DUMMY-ADAPTER-001",
                "message": message,
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
    path = output_dir / "integration_result.json"
    write_json(path, payload)
    return path
