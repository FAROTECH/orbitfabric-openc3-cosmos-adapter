from __future__ import annotations

import json
from pathlib import Path

from orbitfabric_dummy_adapter.input_set import load_input_set
from orbitfabric_dummy_adapter.io import AdapterError

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "examples" / "input-set" / "integration_input_manifest.json"


def test_synthetic_input_set_is_coherent() -> None:
    manifest, entity_index = load_input_set(MANIFEST)

    assert manifest["input_set_sha256"] == (
        "2a10a3be8f4c1df9210a6a1a41f2fd7f32ed5fd3bcfb80eb9e56f3108610bd5a"
    )
    assert entity_index["kind"] == "orbitfabric.entity_index"


def test_input_set_fingerprint_tamper_is_rejected(tmp_path: Path) -> None:
    source = json.loads(MANIFEST.read_text(encoding="utf-8"))
    source["mission"]["id"] = "tampered"
    tampered = tmp_path / "integration_input_manifest.json"
    tampered.write_text(json.dumps(source, indent=2) + "\n", encoding="utf-8")

    try:
        load_input_set(tampered)
    except AdapterError as exc:
        assert "fingerprint mismatch" in str(exc)
    else:
        raise AssertionError("Tampered input set fingerprint was accepted")
