from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from .io import load_json, load_yaml, sha256_file

INTEGRATION_ID = "orbitfabric-openc3-cosmos"
INTEGRATION_SCHEMA_VERSION = "0.1-candidate"
SCHEMA_PATH = Path(__file__).resolve().parents[1] / "schemas" / "profile-0.1.schema.json"


@dataclass(frozen=True)
class ProjectionBinding:
    id: str
    intent: str
    domain: str
    source_id: str
    config: dict[str, Any]
    reason: str | None


@dataclass(frozen=True)
class ProjectionProfile:
    path: Path
    document: dict[str, Any]
    sha256: str
    id: str
    version: str
    target_name: str
    telemetry_wait_timeout_s: float
    bindings: dict[tuple[str, str], ProjectionBinding]

    def binding_for(self, domain: str, entity_id: str) -> ProjectionBinding | None:
        return self.bindings.get((domain, entity_id))


def load_projection_profile(path: Path) -> ProjectionProfile:
    path = path.resolve()
    document = load_yaml(path)

    schema = load_json(SCHEMA_PATH)
    errors = sorted(
        Draft202012Validator(schema).iter_errors(document),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        first = errors[0]
        location = ".".join(str(item) for item in first.absolute_path) or "<root>"
        raise ValueError(
            f"Projection Profile schema validation failed at {location}: {first.message}"
        )

    profile = document["profile"]
    integration = document["integration"]
    settings = document["settings"]

    if integration["id"] != INTEGRATION_ID:
        raise ValueError("Projection Profile targets another integration")
    if integration["schema_version"] != INTEGRATION_SCHEMA_VERSION:
        raise ValueError("unsupported OpenC3 COSMOS integration schema version")

    bindings: dict[tuple[str, str], ProjectionBinding] = {}
    binding_ids: set[str] = set()
    for raw in document["bindings"]:
        binding = _load_binding(raw)
        if binding.id in binding_ids:
            raise ValueError(f"duplicate Projection Profile binding id: {binding.id}")
        binding_ids.add(binding.id)

        key = (binding.domain, binding.source_id)
        if key in bindings:
            raise ValueError(f"ambiguous Projection Profile bindings for {key}")
        bindings[key] = binding

    return ProjectionProfile(
        path=path,
        document=document,
        sha256=sha256_file(path),
        id=str(profile["id"]),
        version=str(profile["version"]),
        target_name=str(settings["target_name"]),
        telemetry_wait_timeout_s=float(settings["telemetry_wait_timeout_s"]),
        bindings=bindings,
    )


def _load_binding(raw: Any) -> ProjectionBinding:
    if not isinstance(raw, dict):
        raise ValueError("Projection Profile binding must be a mapping")

    binding_id = raw["id"]
    intent = raw["intent"]
    sources = raw["sources"]
    config = raw.get("config", {})
    reason = raw.get("reason")

    if len(sources) != 1:
        raise ValueError(f"OpenC3 COSMOS schema requires exactly one source: {binding_id}")
    if not isinstance(config, dict):
        raise ValueError(f"binding config must be a mapping: {binding_id}")

    source = sources[0]
    domain = source["domain"]
    source_id = source["id"]

    if intent == "do_not_project":
        if not isinstance(reason, str) or not reason:
            raise ValueError(f"do_not_project binding requires reason: {binding_id}")
        if config:
            raise ValueError(f"do_not_project binding must not contain config: {binding_id}")
    else:
        _validate_project_config(binding_id, domain, config)

    return ProjectionBinding(
        id=binding_id,
        intent=intent,
        domain=domain,
        source_id=source_id,
        config=config,
        reason=reason if isinstance(reason, str) else None,
    )


def _validate_project_config(binding_id: str, domain: str, config: dict[str, Any]) -> None:
    if domain == "commands":
        command = config.get("cosmos_command")
        if not isinstance(command, str) or not command:
            raise ValueError(f"command binding requires cosmos_command: {binding_id}")
        return

    if domain == "telemetry":
        packet = config.get("cosmos_packet")
        item = config.get("cosmos_item")
        encoding = config.get("value_encoding", "identity")
        if not isinstance(packet, str) or not packet:
            raise ValueError(f"telemetry binding requires cosmos_packet: {binding_id}")
        if not isinstance(item, str) or not item:
            raise ValueError(f"telemetry binding requires cosmos_item: {binding_id}")
        if encoding not in {"identity", "boolean_01"}:
            raise ValueError(f"unsupported telemetry value_encoding: {binding_id}")
        return

    raise ValueError(f"source domain is not supported by OpenC3 COSMOS schema: {domain}")
