from __future__ import annotations

import json
from importlib.resources import files
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from .constants import INTEGRATION_ID, INTEGRATION_SCHEMA_VERSION, PROFILE_VERSION
from .io import AdapterError, load_yaml


def load_profile(path: Path) -> dict[str, Any]:
    payload = load_yaml(path)
    schema_path = files("orbitfabric_dummy_adapter").joinpath(
        "schemas/profile-0.1.schema.json"
    )
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    errors = sorted(
        Draft202012Validator(schema).iter_errors(payload),
        key=lambda item: list(item.absolute_path),
    )
    if errors:
        detail = "; ".join(
            f"{'.'.join(str(part) for part in error.absolute_path) or '$'}: {error.message}"
            for error in errors
        )
        raise AdapterError(f"Projection Profile is not conformant: {detail}")

    if payload["kind"] != "orbitfabric.projection_profile":
        raise AdapterError("Unsupported Projection Profile kind")
    if payload["profile_version"] != PROFILE_VERSION:
        raise AdapterError("Unsupported Projection Profile version")
    if payload["integration"]["id"] != INTEGRATION_ID:
        raise AdapterError("Projection Profile integration id mismatch")
    if payload["integration"]["schema_version"] != INTEGRATION_SCHEMA_VERSION:
        raise AdapterError("Projection Profile integration schema mismatch")
    return payload
