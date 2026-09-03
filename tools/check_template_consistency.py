from __future__ import annotations

import hashlib
import json
import sys
import tomllib
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]


def _discover_manifest() -> Path:
    matches = sorted((ROOT / "src").glob("*/integration_package.json"))
    if len(matches) != 1:
        raise ValueError(
            "Expected exactly one namespaced integration_package.json under src/, "
            f"found {len(matches)}"
        )
    return matches[0]


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return payload


def _integration_id_const(schema: dict[str, Any]) -> str | None:
    integration = schema.get("properties", {}).get("integration", {})
    if not isinstance(integration, dict):
        return None
    identity = integration.get("properties", {}).get("id", {})
    if not isinstance(identity, dict):
        return None
    value = identity.get("const")
    return value if isinstance(value, str) else None


def main() -> int:
    try:
        manifest_path = _discover_manifest()
        package = manifest_path.parent
        pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        manifest = _load_json(manifest_path)
    except (OSError, ValueError, json.JSONDecodeError, tomllib.TOMLDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    errors: list[str] = []

    project = pyproject.get("project", {})
    project_version = project.get("version")
    manifest_version = manifest.get("adapter", {}).get("version")
    if project_version != manifest_version:
        errors.append("pyproject version and manifest adapter.version differ")

    argv_prefix = manifest.get("execution", {}).get("argv_prefix")
    scripts = project.get("scripts", {})
    if not isinstance(argv_prefix, list) or len(argv_prefix) != 1:
        errors.append("manifest execution.argv_prefix must contain one console-script name")
    elif not isinstance(scripts, dict) or argv_prefix[0] not in scripts:
        errors.append("manifest execution endpoint is not declared in pyproject project.scripts")

    schema_entries = manifest.get("profile_schemas")
    if not isinstance(schema_entries, list) or len(schema_entries) != 1:
        errors.append("template expects exactly one profile schema entry")
        schema_entry = None
    else:
        schema_entry = schema_entries[0]

    schema: dict[str, Any] | None = None
    if isinstance(schema_entry, dict):
        schema_rel = schema_entry.get("path")
        if not isinstance(schema_rel, str) or not schema_rel:
            errors.append("manifest profile schema path is missing")
        else:
            schema_path = package / schema_rel
            if not schema_path.is_file():
                errors.append(f"manifest profile schema does not exist: {schema_rel}")
            else:
                schema_sha = hashlib.sha256(schema_path.read_bytes()).hexdigest()
                if schema_entry.get("sha256") != schema_sha:
                    errors.append("manifest profile schema SHA-256 is stale")
                try:
                    schema = _load_json(schema_path)
                except (OSError, ValueError, json.JSONDecodeError) as exc:
                    errors.append(str(exc))

    manifest_integration_id = manifest.get("integration", {}).get("id")
    if schema is not None:
        schema_integration_id = _integration_id_const(schema)
        if schema_integration_id != manifest_integration_id:
            errors.append("profile schema integration.id differs from manifest integration.id")

    profile_path = ROOT / "examples" / "profile.yaml"
    try:
        profile = yaml.safe_load(profile_path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        errors.append(f"cannot load examples/profile.yaml: {exc}")
        profile = None

    if isinstance(profile, dict):
        profile_integration_id = profile.get("integration", {}).get("id")
        if profile_integration_id != manifest_integration_id:
            errors.append("example Profile integration.id differs from manifest integration.id")

        compatible_versions = manifest.get("profile_compatibility", {}).get("profile_versions", [])
        if profile.get("profile_version") not in compatible_versions:
            errors.append("example Profile version is not declared compatible by the manifest")
    elif profile is not None:
        errors.append("examples/profile.yaml must contain a mapping")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
