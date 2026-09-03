from __future__ import annotations

import hashlib
import json
import sys
import tomllib
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
THIS_FILE = Path(__file__).resolve()
EXPECTED_DISTRIBUTION = "orbitfabric-openc3-cosmos-adapter"
EXPECTED_PACKAGE = "orbitfabric_openc3_cosmos_adapter"
EXPECTED_CONSOLE = "orbitfabric-openc3-cosmos"
EXPECTED_ADAPTER_ID = "orbitfabric-openc3-cosmos"
EXPECTED_OPERATION = "verification_projection"
EXPECTED_VERSION = "0.1.0"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return payload


def main() -> int:
    errors: list[str] = []
    package = ROOT / "src" / EXPECTED_PACKAGE
    manifest_path = package / "integration_package.json"
    schema_path = package / "schemas" / "profile-0.1.schema.json"

    try:
        pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        manifest = _load_json(manifest_path)
        schema = _load_json(schema_path)
        profile = yaml.safe_load(
            (ROOT / "examples" / "profile.yaml").read_text(encoding="utf-8")
        )
    except (
        OSError,
        ValueError,
        json.JSONDecodeError,
        tomllib.TOMLDecodeError,
        yaml.YAMLError,
    ) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    project = pyproject.get("project", {})
    if project.get("name") != EXPECTED_DISTRIBUTION:
        errors.append("unexpected Python distribution identity")
    if project.get("version") != EXPECTED_VERSION:
        errors.append("unexpected stable Python distribution version")
    if manifest.get("adapter", {}).get("version") != EXPECTED_VERSION:
        errors.append("unexpected stable manifest adapter.version")
    if project.get("version") != manifest.get("adapter", {}).get("version"):
        errors.append("pyproject version and manifest adapter.version differ")

    scripts = project.get("scripts", {})
    if scripts != {EXPECTED_CONSOLE: f"{EXPECTED_PACKAGE}.cli:main"}:
        errors.append("console-script identity is inconsistent")

    if manifest.get("adapter", {}).get("id") != EXPECTED_ADAPTER_ID:
        errors.append("unexpected adapter.id")
    if manifest.get("integration", {}).get("id") != EXPECTED_ADAPTER_ID:
        errors.append("unexpected integration.id")
    if manifest.get("execution", {}).get("argv_prefix") != [EXPECTED_CONSOLE]:
        errors.append("manifest execution endpoint differs from console script")

    operations = manifest.get("operations")
    operation_ids = (
        [item.get("id") for item in operations]
        if isinstance(operations, list)
        else None
    )
    if operation_ids != [EXPECTED_OPERATION]:
        errors.append("initial product must declare only verification_projection")

    schema_entries = manifest.get("profile_schemas")
    if not isinstance(schema_entries, list) or len(schema_entries) != 1:
        errors.append("adapter expects exactly one Profile schema entry")
    else:
        declared_sha = schema_entries[0].get("sha256")
        computed_sha = hashlib.sha256(schema_path.read_bytes()).hexdigest()
        if declared_sha != computed_sha:
            errors.append(
                "manifest Profile schema SHA-256 is stale: "
                f"declared={declared_sha!r}, computed={computed_sha}"
            )

    schema_integration = (
        schema.get("properties", {})
        .get("integration", {})
        .get("properties", {})
        .get("id", {})
        .get("const")
    )
    if schema_integration != EXPECTED_ADAPTER_ID:
        errors.append("Profile schema integration.id differs from product identity")

    if not isinstance(profile, dict):
        errors.append("examples/profile.yaml must contain a mapping")
    else:
        if profile.get("integration", {}).get("id") != EXPECTED_ADAPTER_ID:
            errors.append("example Profile integration.id differs from product identity")
        compatible = manifest.get("profile_compatibility", {}).get("profile_versions", [])
        if profile.get("profile_version") not in compatible:
            errors.append("example Profile version is not declared compatible")

    forbidden = {
        "0.1.0.dev0",
        "orbitfabric-dummy-adapter",
        "orbitfabric_dummy_adapter",
        "orbitfabric-dummy",
        "exp001_verification_projection",
        "OrbitFabric Adapter Developer Template",
        "This repository is a developer template",
    }
    ignored_parts = {".git", ".venv", "build", "dist", "generated", "site"}
    text_suffixes = {".md", ".py", ".toml", ".json", ".yaml", ".yml", ".sh"}

    for path in ROOT.rglob("*"):
        if not path.is_file() or path.resolve() == THIS_FILE:
            continue
        if any(part in ignored_parts for part in path.relative_to(ROOT).parts):
            continue
        if path.suffix not in text_suffixes:
            continue
        text = path.read_text(encoding="utf-8")
        for token in forbidden:
            if token in text:
                errors.append(
                    f"{path.relative_to(ROOT)} retains forbidden bootstrap/release token {token}"
                )

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
