from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import rfc8785

from .io import AdapterError, load_json, sha256_file

EXPECTED_SURFACES = {
    "entity_index": ("required", "orbitfabric.entity_index", "0.1"),
    "lint_report": ("required", "orbitfabric-lint", "v1"),
    "mission_snapshot": ("required", "orbitfabric.mission_snapshot", "0.1-candidate"),
    "model_summary": ("companion", "orbitfabric.model_summary", "0.1"),
    "relationship_manifest": (
        "required",
        "orbitfabric.relationship_manifest",
        "0.1-candidate",
    ),
}


def _input_set_sha256(manifest: dict[str, Any]) -> str:
    digest_surfaces = []
    for record in sorted(manifest["surfaces"], key=lambda item: item["role"]):
        digest_surfaces.append(
            {
                "role": record["role"],
                "requirement": record["requirement"],
                "status": record["status"],
                "kind": record["kind"],
                "format_version": record["format_version"],
                "sha256": record["sha256"],
                "unavailable_reason": record["unavailable_reason"],
            }
        )

    digest_payload = {
        "kind": manifest["kind"],
        "input_set_version": manifest["input_set_version"],
        "orbitfabric_version": manifest["orbitfabric_version"],
        "mission": manifest["mission"],
        "load_result": manifest["load_result"],
        "lint_result": manifest["lint_result"],
        "surfaces": digest_surfaces,
    }
    return hashlib.sha256(rfc8785.dumps(digest_payload)).hexdigest()


def _surface_records(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    raw = manifest.get("surfaces")
    if not isinstance(raw, list):
        raise AdapterError("Core Integration Input Set surfaces must be an array")

    records: dict[str, dict[str, Any]] = {}
    for item in raw:
        if not isinstance(item, dict):
            raise AdapterError("Core Integration Input Set surface records must be objects")
        role = item.get("role")
        if not isinstance(role, str) or not role:
            raise AdapterError("Core Integration Input Set surface role is invalid")
        if role in records:
            raise AdapterError(f"Core Integration Input Set duplicates surface role: {role}")
        records[role] = item
    return records


def _verify_surface(
    manifest_path: Path,
    role: str,
    record: dict[str, Any],
) -> Path | None:
    expected = EXPECTED_SURFACES[role]
    if record.get("requirement") != expected[0]:
        raise AdapterError(f"{role} surface requirement mismatch")
    if record.get("kind") != expected[1]:
        raise AdapterError(f"{role} surface kind mismatch")
    if record.get("format_version") != expected[2]:
        raise AdapterError(f"{role} surface version mismatch")

    if record.get("status") == "unavailable":
        if expected[0] == "required":
            raise AdapterError(f"Required {role} surface is unavailable")
        return None
    if record.get("status") != "available":
        raise AdapterError(f"{role} surface status is invalid")

    relative = record.get("path")
    if not isinstance(relative, str) or not relative:
        raise AdapterError(f"{role} surface path is invalid")
    surface_path = (manifest_path.parent / relative).resolve()
    if not surface_path.is_file():
        raise AdapterError(f"{role} surface does not exist: {surface_path}")
    if sha256_file(surface_path) != record.get("sha256"):
        raise AdapterError(f"{role} surface SHA-256 mismatch")
    return surface_path


def load_input_set(manifest_path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    manifest = load_json(manifest_path)
    if manifest.get("kind") != "orbitfabric.integration_input_set":
        raise AdapterError("Unsupported Core Integration Input Set kind")
    if manifest.get("input_set_version") != "0.1-candidate":
        raise AdapterError("Unsupported Core Integration Input Set version")
    if manifest.get("load_result") != "loaded":
        raise AdapterError("Core Integration Input Set is not loaded")
    if manifest.get("lint_result") not in {"passed", "passed_with_warnings"}:
        raise AdapterError("Core Integration Input Set is not projection-ready")

    expected_digest = manifest.get("input_set_sha256")
    if not isinstance(expected_digest, str) or _input_set_sha256(manifest) != expected_digest:
        raise AdapterError("Core Integration Input Set fingerprint mismatch")

    records = _surface_records(manifest)
    missing = sorted(set(EXPECTED_SURFACES) - set(records))
    if missing:
        raise AdapterError(
            "Core Integration Input Set is missing canonical roles: " + ", ".join(missing)
        )

    paths = {
        role: _verify_surface(manifest_path, role, records[role])
        for role in EXPECTED_SURFACES
    }
    entity_path = paths["entity_index"]
    if entity_path is None:
        raise AdapterError("Required entity_index surface is unavailable")

    entity_index = load_json(entity_path)
    if entity_index.get("kind") != "orbitfabric.entity_index":
        raise AdapterError("Invalid entity_index payload kind")
    if entity_index.get("index_version") != "0.1":
        raise AdapterError("Invalid entity_index payload version")
    return manifest, entity_index
