from __future__ import annotations

import json
from importlib.resources import files
from pathlib import Path

from orbitfabric.conformance.integration_contracts import validate_manifest

from orbitfabric_openc3_cosmos_adapter.adapter.profile import load_projection_profile

ROOT = Path(__file__).resolve().parents[1]


def test_manifest_conforms_to_core_contract() -> None:
    manifest_path = files("orbitfabric_openc3_cosmos_adapter").joinpath(
        "integration_package.json"
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    validate_manifest(manifest)

    assert [item["id"] for item in manifest["operations"]] == ["verification_projection"]
    assert manifest["execution"]["protocol"] == "orbitfabric.adapter_cli.v1"
    assert manifest["adapter"]["id"] == "orbitfabric-openc3-cosmos"


def test_reference_profile_conforms_to_adapter_schema() -> None:
    profile = load_projection_profile(ROOT / "examples" / "profile.yaml")

    assert profile.document["integration"]["id"] == "orbitfabric-openc3-cosmos"
    assert profile.document["integration"]["schema_version"] == "0.1-candidate"
    assert profile.target_name == "OFDEMO"
