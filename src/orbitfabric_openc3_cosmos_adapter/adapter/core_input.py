from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .io import canonical_input_set_sha256, load_json, sha256_file

SURFACE_SPECS = {
    "entity_index": ("orbitfabric.entity_index", "0.1"),
    "lint_report": ("orbitfabric-lint", "v1"),
    "mission_snapshot": ("orbitfabric.mission_snapshot", "0.1-candidate"),
    "relationship_manifest": ("orbitfabric.relationship_manifest", "0.1-candidate"),
}
REQUIRED_SURFACES = set(SURFACE_SPECS)
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True)
class CoreInputSet:
    manifest_path: Path
    manifest: dict[str, Any]
    entity_index: dict[str, Any]
    entities: frozenset[tuple[str, str]]

    @property
    def input_set_sha256(self) -> str:
        return str(self.manifest["input_set_sha256"])

    @property
    def mission_id(self) -> str:
        return str(self.manifest["mission"]["id"])

    @property
    def model_version(self) -> str:
        return str(self.manifest["mission"]["model_version"])

    @property
    def orbitfabric_version(self) -> str:
        return str(self.manifest["orbitfabric_version"])

    def require_entity(self, domain: str, entity_id: str) -> None:
        if (domain, entity_id) not in self.entities:
            raise ValueError(
                f"Core entity does not resolve in Entity Index: {domain}:{entity_id}"
            )


def load_core_input_set(manifest_path: Path) -> CoreInputSet:
    manifest_path = manifest_path.resolve()
    manifest = load_json(manifest_path)

    if manifest.get("kind") != "orbitfabric.integration_input_set":
        raise ValueError("unsupported Core Integration Input Set kind")
    if manifest.get("input_set_version") != "0.1-candidate":
        raise ValueError("unsupported Core Integration Input Set version")
    if manifest.get("load_result") != "loaded":
        raise ValueError("Core Integration Input Set was not produced from a loaded mission")
    if manifest.get("lint_result") not in {"passed", "passed_with_warnings"}:
        raise ValueError("Core Integration Input Set lint result is not acceptable")

    orbitfabric_version = manifest.get("orbitfabric_version")
    if not isinstance(orbitfabric_version, str) or not orbitfabric_version:
        raise ValueError("Core Integration Input Set orbitfabric_version is missing")

    mission = manifest.get("mission")
    if not isinstance(mission, dict):
        raise ValueError("Core Integration Input Set mission identity is missing")
    if not isinstance(mission.get("id"), str) or not mission["id"]:
        raise ValueError("Core Integration Input Set mission.id is missing")
    if not isinstance(mission.get("model_version"), str) or not mission["model_version"]:
        raise ValueError("Core Integration Input Set mission.model_version is missing")

    input_set_sha = manifest.get("input_set_sha256")
    if not isinstance(input_set_sha, str) or SHA256_RE.fullmatch(input_set_sha) is None:
        raise ValueError("Core Integration Input Set digest is missing or malformed")
    computed_input_set_sha = canonical_input_set_sha256(manifest)
    if input_set_sha != computed_input_set_sha:
        raise ValueError(
            "Core Integration Input Set fingerprint mismatch: "
            f"declared={input_set_sha}, computed={computed_input_set_sha}"
        )

    surfaces = manifest.get("surfaces")
    if not isinstance(surfaces, list):
        raise ValueError("Core Integration Input Set surfaces are missing")

    by_role: dict[str, dict[str, Any]] = {}
    for record in surfaces:
        if not isinstance(record, dict):
            raise ValueError("Core Integration Input Set contains malformed surface record")
        role = record.get("role")
        if not isinstance(role, str) or not role or role in by_role:
            raise ValueError("Core Integration Input Set contains invalid/duplicate surface role")
        by_role[role] = record

    missing = sorted(REQUIRED_SURFACES - set(by_role))
    if missing:
        raise ValueError(f"Core Integration Input Set missing required surfaces: {missing}")

    root = manifest_path.parent.resolve()
    for role, (expected_kind, expected_version) in SURFACE_SPECS.items():
        record = by_role[role]
        if record.get("requirement") != "required":
            raise ValueError(f"required Core surface has wrong requirement: {role}")
        if record.get("status") != "available":
            raise ValueError(f"required Core surface is unavailable: {role}")
        if record.get("kind") != expected_kind:
            raise ValueError(
                f"required Core surface kind is incompatible: {role}: {record.get('kind')!r}"
            )
        if record.get("format_version") != expected_version:
            raise ValueError(
                "required Core surface format version is incompatible: "
                f"{role}: {record.get('format_version')!r}"
            )
        if record.get("unavailable_reason") is not None:
            raise ValueError(f"available Core surface has unavailable_reason: {role}")

        relative_path = record.get("path")
        expected_sha = record.get("sha256")
        if not isinstance(relative_path, str) or not relative_path:
            raise ValueError(f"required Core surface has no path: {role}")
        if not isinstance(expected_sha, str) or SHA256_RE.fullmatch(expected_sha) is None:
            raise ValueError(f"required Core surface has no valid digest: {role}")

        candidate = Path(relative_path)
        if candidate.is_absolute():
            raise ValueError(f"Core surface path must be relative: {role}")
        surface_path = (root / candidate).resolve()
        try:
            surface_path.relative_to(root)
        except ValueError as exc:
            raise ValueError(f"Core surface path escapes input-set directory: {role}") from exc
        if not surface_path.is_file():
            raise ValueError(f"required Core surface file is missing: {role}")
        if sha256_file(surface_path) != expected_sha:
            raise ValueError(f"Core surface digest mismatch: {role}")

    entity_path = root / str(by_role["entity_index"]["path"])
    entity_index = load_json(entity_path)
    if entity_index.get("kind") != "orbitfabric.entity_index":
        raise ValueError("Core entity_index surface kind mismatch")

    entity_mission = entity_index.get("mission")
    if not isinstance(entity_mission, dict):
        raise ValueError("Core Entity Index mission identity is missing")
    if entity_mission.get("id") != mission["id"]:
        raise ValueError("Core Entity Index mission id does not match input-set manifest")
    if entity_mission.get("model_version") != mission["model_version"]:
        raise ValueError("Core Entity Index model version does not match input-set manifest")

    entity_records = entity_index.get("entities")
    if not isinstance(entity_records, list):
        raise ValueError("Core Entity Index entities are missing")

    entities: set[tuple[str, str]] = set()
    for record in entity_records:
        if not isinstance(record, dict):
            raise ValueError("Core Entity Index contains malformed entity record")
        domain = record.get("domain")
        entity_id = record.get("id")
        if not isinstance(domain, str) or not isinstance(entity_id, str):
            raise ValueError("Core Entity Index contains entity without domain/id")
        key = (domain, entity_id)
        if key in entities:
            raise ValueError(f"Core Entity Index contains duplicate entity: {key}")
        entities.add(key)

    return CoreInputSet(
        manifest_path=manifest_path,
        manifest=manifest,
        entity_index=entity_index,
        entities=frozenset(entities),
    )
