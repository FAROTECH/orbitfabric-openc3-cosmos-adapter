from __future__ import annotations

import json
from pathlib import Path

import pytest
from orbitfabric.export.integration_input_set import write_integration_input_set

from orbitfabric_openc3_cosmos_adapter.adapter.core_input import load_core_input_set
from orbitfabric_openc3_cosmos_adapter.adapter.io import canonical_input_set_sha256

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "_orbitfabric_core"

pytestmark = pytest.mark.skipif(
    not CORE.is_dir(),
    reason="exact Core checkout is supplied by CI for input-set integrity tests",
)


def _input_set(tmp_path: Path) -> Path:
    mission = CORE / "examples" / "demo-3u" / "mission"
    result = write_integration_input_set(mission, tmp_path / "core-input")
    assert result.succeeded, (result.load_result, result.lint_result, result.generation_failed)
    return result.manifest_path


def test_valid_core_input_set_passes_integrity_and_compatibility(tmp_path: Path) -> None:
    loaded = load_core_input_set(_input_set(tmp_path))

    assert loaded.mission_id == "demo-3u"
    assert loaded.input_set_sha256 == canonical_input_set_sha256(loaded.manifest)


def test_tampered_input_set_fingerprint_is_rejected(tmp_path: Path) -> None:
    manifest_path = _input_set(tmp_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["input_set_sha256"] = "0" * 64
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match="fingerprint mismatch"):
        load_core_input_set(manifest_path)


def test_incompatible_required_surface_is_rejected_even_with_valid_fingerprint(
    tmp_path: Path,
) -> None:
    manifest_path = _input_set(tmp_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    entity_index = next(item for item in manifest["surfaces"] if item["role"] == "entity_index")
    entity_index["kind"] = "example.incompatible.entity_index"
    manifest["input_set_sha256"] = canonical_input_set_sha256(manifest)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match="kind is incompatible"):
        load_core_input_set(manifest_path)
