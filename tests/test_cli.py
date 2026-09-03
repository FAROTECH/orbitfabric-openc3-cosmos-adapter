from __future__ import annotations

import json
from pathlib import Path

from orbitfabric_openc3_cosmos_adapter.adapter.cli import main


def test_missing_scenario_binding_fails_closed(tmp_path: Path) -> None:
    manifest = tmp_path / "missing-input-set.json"
    profile = tmp_path / "missing-profile.yaml"
    output = tmp_path / "out"

    status = main(
        [
            "run",
            "--operation",
            "verification_projection",
            "--input-set-manifest",
            str(manifest),
            "--profile",
            str(profile),
            "--output-dir",
            str(output),
        ]
    )

    assert status == 1
    result = json.loads((output / "integration_result.json").read_text(encoding="utf-8"))
    assert result["result"] == "failed"
    assert result["operation"]["id"] == "verification_projection"
    assert result["inputs"]["operation_inputs"][0]["role"] == "scenario"
    assert result["inputs"]["operation_inputs"][0]["status"] == "unavailable"
