from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from .cosmos_materializer import materialize_python_procedure, materialize_python_suite
from .io import write_json
from .result import failed_result, successful_result, unavailable_operation_input, write_result
from .verification_plan import validate_verification_plan
from .verification_projector import project_verification_scenario


OPERATION_ID = "verification_projection"
SCENARIO_ROLE = "scenario"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="orbitfabric-openc3-cosmos")
    subparsers = parser.add_subparsers(dest="command", required=True)
    run = subparsers.add_parser("run")
    run.add_argument("--operation", required=True)
    run.add_argument("--input-set-manifest", required=True)
    run.add_argument("--profile", required=True)
    run.add_argument(
        "--operation-input",
        action="append",
        nargs=2,
        metavar=("ROLE", "PATH"),
        default=[],
        help="Operation-input v1 binding. Repeat as --operation-input ROLE PATH.",
    )
    run.add_argument("--output-dir", required=True)
    return parser


def _parse_operation_inputs(raw: list[list[str]]) -> dict[str, Path]:
    bindings: dict[str, Path] = {}
    for role_value, path_value in raw:
        role = role_value.strip()
        if not role:
            raise ValueError("Operation input role must be a non-empty string.")
        if role in bindings:
            raise ValueError(f"Operation input role {role!r} is bound more than once.")
        if not path_value.strip():
            raise ValueError(f"Operation input role {role!r} has an empty resource path.")
        bindings[role] = Path(path_value)
    return bindings


def _validate_bindings(operation: str, bindings: dict[str, Path]) -> Path:
    if operation != OPERATION_ID:
        raise ValueError(f"Unsupported operation: {operation}")

    actual = set(bindings)
    expected = {SCENARIO_ROLE}
    if actual != expected:
        missing = sorted(expected - actual)
        unexpected = sorted(actual - expected)
        details: list[str] = []
        if missing:
            details.append(f"missing required roles: {', '.join(missing)}")
        if unexpected:
            details.append(f"unexpected roles: {', '.join(unexpected)}")
        raise ValueError(
            f"Operation {OPERATION_ID!r} requires exactly one 'scenario' binding; "
            + "; ".join(details)
        )

    scenario = bindings[SCENARIO_ROLE].resolve()
    if not scenario.is_file():
        raise ValueError(f"Scenario binding is not an existing file: {scenario}")
    return scenario


def _existing_file(path_value: str, label: str) -> Path:
    path = Path(path_value).resolve()
    if not path.is_file():
        raise ValueError(f"{label} is not an existing file: {path}")
    return path


def _prepare_output(output_dir: Path) -> Path:
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    for relative in ("integration_result.json", "verification_projection"):
        candidate = output_dir / relative
        if candidate.is_dir():
            shutil.rmtree(candidate)
        elif candidate.exists():
            candidate.unlink()
    return output_dir


def _failure_inputs(operation: str, message: str) -> list[dict]:
    if operation == OPERATION_ID:
        return [unavailable_operation_input(SCENARIO_ROLE, message)]
    return []


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    operation = args.operation
    output_dir = _prepare_output(Path(args.output_dir))

    try:
        bindings = _parse_operation_inputs(args.operation_input)
        scenario_path = _validate_bindings(operation, bindings)
        input_set_manifest = _existing_file(
            args.input_set_manifest,
            "Core Integration Input Set manifest",
        )
        profile_path = _existing_file(args.profile, "Projection Profile")
    except ValueError as exc:
        message = str(exc)
        write_result(
            output_dir,
            failed_result(
                operation=operation,
                message=message,
                operation_inputs=_failure_inputs(operation, message),
            ),
        )
        print(message, file=sys.stderr)
        return 1

    try:
        plan = project_verification_scenario(scenario_path, input_set_manifest, profile_path)
        validate_verification_plan(plan)
        if plan["status"] != "executable_subset":
            raise ValueError(
                "COSMOS verification projection is not executable_subset: "
                f"{plan['status']}"
            )

        bundle = output_dir / "verification_projection"
        plan_path = write_json(bundle / "verification_projection_plan.json", plan)
        procedure_path = materialize_python_procedure(
            plan,
            bundle / "cosmos" / "verification.py",
        )
        suite_path = materialize_python_suite(
            plan,
            bundle / "cosmos" / "verification_suite.py",
        )

        result = successful_result(
            operation=operation,
            plan=plan,
            output_dir=output_dir,
            plan_path=plan_path,
            procedure_path=procedure_path,
            suite_path=suite_path,
        )
        result_path = write_result(output_dir, result)
    except (ValueError, OSError) as exc:
        message = str(exc)
        write_result(
            output_dir,
            failed_result(
                operation=operation,
                message=message,
                operation_inputs=_failure_inputs(operation, message),
            ),
        )
        print(message, file=sys.stderr)
        return 1

    print(f"Integration Result: {result_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
