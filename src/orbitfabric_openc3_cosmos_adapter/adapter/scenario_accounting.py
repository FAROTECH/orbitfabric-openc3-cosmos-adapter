from __future__ import annotations

from pathlib import Path
from typing import Any

from .io import write_json

ACCOUNTING_KIND = "orbitfabric.scenario_projection_accounting"
ACCOUNTING_VERSION = "0.1-candidate"


def scenario_projection_accounting(plan: dict[str, Any]) -> dict[str, Any]:
    """Project adapter-owned plan knowledge into the generic accounting contract."""
    if plan.get("status") != "executable_subset":
        raise ValueError("generic Scenario accounting requires an executable projection")

    records: list[dict[str, Any]] = []
    for atom in plan["atoms"]:
        disposition = atom["disposition"]
        if disposition not in {"projected", "not_projected"}:
            raise ValueError(
                f"successful generic accounting cannot publish {disposition!r}"
            )
        mapping_ids = [f"mapping.{operation_id}" for operation_id in atom["operation_ids"]]
        record: dict[str, Any] = {
            "atom_id": atom["id"],
            "disposition": disposition,
            "mapping_ids": mapping_ids,
        }
        reason = atom.get("reason")
        if reason is not None:
            record["reason"] = reason
        if disposition == "projected" and reason is not None:
            raise ValueError("projected atom must not carry a non-projection reason")
        if disposition == "not_projected" and (mapping_ids or not reason):
            raise ValueError(
                "not_projected atom requires empty mappings and a nonblank reason"
            )
        records.append(record)

    if len({record["atom_id"] for record in records}) != len(records):
        raise ValueError("generic accounting atom ids must be unique")

    return {
        "kind": ACCOUNTING_KIND,
        "accounting_version": ACCOUNTING_VERSION,
        "scenario": {
            "id": plan["source"]["scenario_id"],
            "sha256": plan["source"]["scenario_sha256"],
        },
        "completeness": "complete",
        "records": records,
    }


def write_scenario_projection_accounting(
    plan: dict[str, Any], path: Path
) -> Path:
    return write_json(path, scenario_projection_accounting(plan))
