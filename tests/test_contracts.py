from __future__ import annotations

import json
from importlib.resources import files
from pathlib import Path

from orbitfabric.conformance.integration_contracts import validate_manifest

from orbitfabric_dummy_adapter.profile import load_profile

ROOT = Path(__file__).resolve().parents[1]


def test_manifest_conforms_to_core_contract() -> None:
    manifest_path = files("orbitfabric_dummy_adapter").joinpath("integration_package.json")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    validate_manifest(manifest)

    assert {item["id"] for item in manifest["operations"]} == {
        "project",
        "verification_projection",
    }


def test_example_profile_conforms_to_adapter_schema() -> None:
    payload = load_profile(ROOT / "examples" / "profile.yaml")

    assert payload["integration"]["id"] == "orbitfabric-dummy"
