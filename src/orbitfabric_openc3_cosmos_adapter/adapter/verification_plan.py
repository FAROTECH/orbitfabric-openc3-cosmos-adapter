from __future__ import annotations

from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from .io import load_json
from .verification_projector import PLAN_KIND, PLAN_VERSION

SCHEMA_PATH = (
    Path(__file__).resolve().parents[1]
    / "schemas"
    / "verification-projection-plan-0.1.schema.json"
)


def validate_verification_plan(plan: dict[str, Any]) -> None:
    schema = load_json(SCHEMA_PATH)
    errors = sorted(
        Draft202012Validator(schema).iter_errors(plan),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        first = errors[0]
        location = ".".join(str(item) for item in first.absolute_path) or "<root>"
        raise ValueError(
            f"verification plan schema validation failed at {location}: {first.message}"
        )

    if plan.get("kind") != PLAN_KIND or plan.get("plan_version") != PLAN_VERSION:
        raise ValueError("verification plan identity mismatch")

    atoms = plan["atoms"]
    operations = plan["operations"]
    diagnostics = plan["diagnostics"]

    atom_by_id = {atom["id"]: atom for atom in atoms}
    if len(atom_by_id) != len(atoms):
        raise ValueError("verification plan contains duplicate atom ids")

    operation_by_id = {operation["id"]: operation for operation in operations}
    if len(operation_by_id) != len(operations):
        raise ValueError("verification plan contains duplicate operation ids")

    for expected_order, operation in enumerate(operations):
        if operation["order"] != expected_order:
            raise ValueError("verification plan operation order is not contiguous")
        atom = atom_by_id.get(operation["source_atom_id"])
        if atom is None:
            raise ValueError("verification plan operation references unknown source atom")
        if operation["id"] not in atom["operation_ids"]:
            raise ValueError("verification plan operation is not back-referenced by source atom")

    for atom in atoms:
        for operation_id in atom["operation_ids"]:
            operation = operation_by_id.get(operation_id)
            if operation is None:
                raise ValueError("verification plan atom references unknown operation")
            if operation["source_atom_id"] != atom["id"]:
                raise ValueError("verification plan atom/operation provenance is inconsistent")

        if atom["disposition"] == "projected" and atom["reason"] is not None:
            raise ValueError("projected atom must not contain a non-projection reason")
        if atom["disposition"] in {"not_projected", "blocked"} and not atom["reason"]:
            raise ValueError("non-projected/blocked atom requires an explicit reason")

    accounting = plan["accounting"]
    expected = {
        "source_atoms": len(atoms),
        "projected_atoms": sum(a["disposition"] == "projected" for a in atoms),
        "not_projected_atoms": sum(a["disposition"] == "not_projected" for a in atoms),
        "blocked_atoms": sum(a["disposition"] == "blocked" for a in atoms),
        "source_actions": sum(a["role"] == "action" for a in atoms),
        "source_expectations": sum(a["role"] == "expectation" for a in atoms),
        "projected_source_actions": sum(
            a["role"] == "action" and a["disposition"] == "projected" for a in atoms
        ),
        "projected_source_expectations": sum(
            a["role"] == "expectation" and a["disposition"] == "projected" for a in atoms
        ),
        "resolved_operations": len(operations),
    }
    if accounting != expected:
        raise ValueError("verification plan accounting does not match atoms/operations")

    diagnostic_atom_ids = {diagnostic["atom_id"] for diagnostic in diagnostics}
    if not diagnostic_atom_ids.issubset(atom_by_id):
        raise ValueError("verification plan diagnostic references unknown atom")

    expected_status = "blocked" if expected["blocked_atoms"] else "executable_subset"
    if plan["status"] != expected_status:
        raise ValueError("verification plan status does not match blocked-atom accounting")
