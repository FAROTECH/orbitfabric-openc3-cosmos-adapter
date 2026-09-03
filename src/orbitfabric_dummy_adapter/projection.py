from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .io import AdapterError, load_yaml, sha256_file, write_json


def _entities_by_key(entity_index: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    entities = entity_index.get("entities")
    if not isinstance(entities, list):
        raise AdapterError("entity_index.json must contain an entities array")
    return {
        (item["domain"], item["id"]): item
        for item in entities
        if isinstance(item, dict) and "domain" in item and "id" in item
    }


def _default_target_name(prefix: str, source_id: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9]+", "_", source_id).strip("_").upper()
    return f"{prefix}{normalized}"


def project_telemetry(
    entity_index: dict[str, Any],
    profile: dict[str, Any],
    output_dir: Path,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    entities = _entities_by_key(entity_index)
    prefix = profile.get("settings", {}).get("target_prefix", "DUMMY_")
    projected: list[dict[str, Any]] = []
    mappings: list[dict[str, Any]] = []

    for binding in profile.get("bindings", []):
        intent = binding.get("intent")
        sources = binding.get("sources", [])
        if len(sources) != 1:
            raise AdapterError("Dummy adapter bindings require exactly one source")
        source = sources[0]
        key = (source.get("domain"), source.get("id"))
        entity = entities.get(key)
        if entity is None:
            raise AdapterError(f"Profile source does not resolve in Entity Index: {key}")
        if key[0] != "telemetry":
            raise AdapterError("Dummy project operation supports telemetry sources only")

        if intent == "do_not_project":
            mappings.append(
                {
                    "id": binding["id"],
                    "status": "intentionally_not_projected",
                    "source": {"domain": key[0], "id": key[1]},
                    "reason": binding["reason"],
                }
            )
            continue
        if intent != "project":
            raise AdapterError(f"Unsupported binding intent: {intent}")

        target_name = binding.get("config", {}).get("target_name") or _default_target_name(
            prefix, key[1]
        )
        projected.append(
            {
                "source_id": key[1],
                "display_name": entity.get("display_name"),
                "target_name": target_name,
            }
        )
        mappings.append(
            {
                "id": binding["id"],
                "status": "projected",
                "source": {"domain": key[0], "id": key[1]},
                "target": {"kind": "dummy.telemetry", "id": target_name},
            }
        )

    payload = {
        "kind": "orbitfabric_dummy.telemetry_projection",
        "version": "0.1",
        "telemetry": projected,
    }
    path = output_dir / "dummy_projection.json"
    write_json(path, payload)
    return (
        {
            "id": "dummy.telemetry_projection",
            "kind": payload["kind"],
            "status": "generated",
            "path": path.name,
            "media_type": "application/json",
            "sha256": sha256_file(path),
        },
        mappings,
    )


def project_verification(
    scenario_path: Path,
    output_dir: Path,
) -> tuple[dict[str, Any], str]:
    scenario = load_yaml(scenario_path)
    identity = scenario.get("scenario")
    if not isinstance(identity, dict):
        raise AdapterError("Scenario input does not contain scenario identity")
    scenario_id = identity.get("id")
    if not isinstance(scenario_id, str) or not scenario_id:
        raise AdapterError("Scenario input id is missing")

    steps = scenario.get("steps", [])
    if not isinstance(steps, list):
        raise AdapterError("Scenario steps must be an array")

    payload = {
        "kind": "orbitfabric_dummy.verification_plan",
        "version": "0.1",
        "scenario": {
            "id": scenario_id,
            "name": identity.get("name"),
            "step_count": len(steps),
        },
    }
    path = output_dir / "dummy_verification_plan.json"
    write_json(path, payload)
    return (
        {
            "id": "dummy.verification_plan",
            "kind": payload["kind"],
            "status": "generated",
            "path": path.name,
            "media_type": "application/json",
            "sha256": sha256_file(path),
        },
        scenario_id,
    )
