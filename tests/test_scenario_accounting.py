from __future__ import annotations

import json
from pathlib import Path

import pytest
from orbitfabric.conformance.scenario_projection_accounting import (
    validate_accounting,
    verify_bundle,
)

from orbitfabric_openc3_cosmos_adapter.adapter.result import successful_result, write_result
from orbitfabric_openc3_cosmos_adapter.adapter.scenario_accounting import (
    ACCOUNTING_KIND,
    ACCOUNTING_VERSION,
    scenario_projection_accounting,
    write_scenario_projection_accounting,
)

ROOT = Path(__file__).resolve().parents[1]
R1_PLAN = ROOT / "tests" / "fixtures" / "r1" / "cosmos-verification-plan.json"


def r1_plan() -> dict:
    return json.loads(R1_PLAN.read_text(encoding="utf-8"))


def test_complete_r1_accounting_preserves_all_eight_producer_claims() -> None:
    accounting = scenario_projection_accounting(r1_plan())
    records = {record["atom_id"]: record for record in accounting["records"]}

    assert accounting["kind"] == ACCOUNTING_KIND
    assert accounting["accounting_version"] == ACCOUNTING_VERSION
    assert accounting["completeness"] == "complete"
    assert accounting["scenario"] == {
        "id": "payload_stop_acquisition_verification",
        "sha256": "b19ff6e1cf3c45cdb81e239d30aad97e8b6f037703c06f27102b762e69a1146a",
    }
    assert len(records) == 8
    validate_accounting(accounting)
    assert records["atom-0001"] == {
        "atom_id": "atom-0001",
        "disposition": "projected",
        "mapping_ids": [],
    }
    assert records["atom-0003"]["disposition"] == "not_projected"
    assert records["atom-0003"]["mapping_ids"] == []
    assert records["atom-0003"]["reason"]
    assert records["atom-0006"] == {
        "atom_id": "atom-0006",
        "disposition": "projected",
        "mapping_ids": ["mapping.op-0002"],
    }


def test_accounting_is_derived_from_adapter_owned_operations_not_entity_refs() -> None:
    plan = r1_plan()
    atom_3 = plan["atoms"][2]
    atom_6 = plan["atoms"][5]
    assert atom_3["source"] == atom_6["source"]

    records = {
        record["atom_id"]: record for record in scenario_projection_accounting(plan)["records"]
    }
    assert records["atom-0003"]["disposition"] != records["atom-0006"]["disposition"]


def test_blocked_projection_cannot_emit_success_accounting() -> None:
    plan = r1_plan()
    plan["status"] = "blocked"
    plan["atoms"][5]["disposition"] = "blocked"
    with pytest.raises(ValueError, match="executable"):
        scenario_projection_accounting(plan)


def test_not_projected_claim_requires_reason_and_no_mapping() -> None:
    plan = r1_plan()
    plan["atoms"][2]["reason"] = None
    with pytest.raises(ValueError, match="requires empty mappings"):
        scenario_projection_accounting(plan)


def test_new_result_owns_exact_conformant_r1_accounting_bundle(tmp_path: Path) -> None:
    plan = r1_plan()
    bundle = tmp_path / "verification_projection"
    bundle.mkdir()
    plan_path = bundle / "verification_projection_plan.json"
    procedure_path = bundle / "cosmos" / "verification.py"
    suite_path = bundle / "cosmos" / "verification_suite.py"
    procedure_path.parent.mkdir()
    plan_path.write_text(json.dumps(plan) + "\n", encoding="utf-8")
    procedure_path.write_text("# generated procedure\n", encoding="utf-8")
    suite_path.write_text("# generated suite\n", encoding="utf-8")
    accounting_path = write_scenario_projection_accounting(
        plan, bundle / "scenario_projection_accounting.json"
    )
    result = successful_result(
        operation="verification_projection",
        plan=plan,
        output_dir=tmp_path,
        plan_path=plan_path,
        procedure_path=procedure_path,
        suite_path=suite_path,
        accounting_path=accounting_path,
    )
    result_path = write_result(tmp_path, result)

    artifacts = {artifact["id"]: artifact for artifact in result["artifacts"]}
    assert artifacts["scenario.accounting"]["kind"] == ACCOUNTING_KIND
    assert artifacts["scenario.accounting"]["derived_from_mappings"] == [
        "mapping.op-0001",
        "mapping.op-0002",
    ]
    outcome = verify_bundle(
        result_path,
        "scenario.accounting",
        ROOT / "tests" / "fixtures" / "r1" / "scenario-declaration.json",
    )
    assert outcome["completeness"] == "complete"
    assert outcome["unaccounted_atom_ids"] == []

    plan = r1_plan()
    plan["atoms"][2]["operation_ids"] = ["op-0002"]
    with pytest.raises(ValueError, match="requires empty mappings"):
        scenario_projection_accounting(plan)
