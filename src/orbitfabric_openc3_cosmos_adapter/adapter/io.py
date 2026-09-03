from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path
from typing import Any

import rfc8785
import yaml


def sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_input_set_sha256(manifest: dict[str, Any]) -> str:
    try:
        surfaces = []
        for record in sorted(manifest["surfaces"], key=lambda item: item["role"]):
            surfaces.append(
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
        payload = {
            "kind": manifest["kind"],
            "input_set_version": manifest["input_set_version"],
            "orbitfabric_version": manifest["orbitfabric_version"],
            "mission": manifest["mission"],
            "load_result": manifest["load_result"],
            "lint_result": manifest["lint_result"],
            "surfaces": surfaces,
        }
    except (KeyError, TypeError) as exc:
        raise ValueError(f"Core Integration Input Set manifest is incomplete: {exc}") from exc
    return sha256(rfc8785.dumps(payload)).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object in {path}")
    return payload


def load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected YAML mapping in {path}")
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return path
