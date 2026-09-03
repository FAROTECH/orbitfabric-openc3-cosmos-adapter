from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .constants import PROJECT_OPERATION, SCENARIO_ROLE, VERIFICATION_OPERATION
from .input_set import load_input_set
from .io import AdapterError, sha256_file
from .profile import load_profile
from .projection import project_telemetry, project_verification
from .result import failed_result, successful_result, write_result


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="orbitfabric-dummy-adapter")
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
    )
    run.add_argument("--output-dir", required=True)
    return parser


def _bindings(raw: list[list[str]]) -> dict[str, Path]:
    bindings: dict[str, Path] = {}
    for role, value in raw:
        if role in bindings:
            raise AdapterError(f"Operation input role is bound more than once: {role}")
        bindings[role] = Path(value)
    return bindings


def _validate_bindings(operation: str, bindings: dict[str, Path]) -> None:
    if operation == PROJECT_OPERATION and not bindings:
        return
    if operation == VERIFICATION_OPERATION and set(bindings) == {SCENARIO_ROLE}:
        return
    if operation not in {PROJECT_OPERATION, VERIFICATION_OPERATION}:
        raise AdapterError(f"Unsupported operation: {operation}")
    raise AdapterError(f"Operation input binding mismatch for {operation}")


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    operation = args.operation
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        bindings = _bindings(args.operation_input)
        _validate_bindings(operation, bindings)
        input_manifest_path = Path(args.input_set_manifest)
        profile_path = Path(args.profile)
        input_manifest, entity_index = load_input_set(input_manifest_path)
        profile = load_profile(profile_path)

        if operation == PROJECT_OPERATION:
            artifact, mappings = project_telemetry(entity_index, profile, output_dir)
            operation_inputs = []
        else:
            scenario_path = bindings[SCENARIO_ROLE]
            artifact, scenario_id = project_verification(scenario_path, output_dir)
            mappings = []
            operation_inputs = [
                {
                    "role": SCENARIO_ROLE,
                    "status": "available",
                    "id": scenario_id,
                    "sha256": sha256_file(scenario_path),
                    "reason": None,
                }
            ]

        result = successful_result(
            operation=operation,
            input_manifest=input_manifest,
            input_manifest_path=input_manifest_path,
            profile=profile,
            profile_path=profile_path,
            artifacts=[artifact],
            mappings=mappings,
            operation_inputs=operation_inputs,
        )
        result_path = write_result(output_dir, result)
    except (AdapterError, OSError) as exc:
        result_path = write_result(
            output_dir,
            failed_result(
                operation,
                str(exc),
                scenario_role=operation == VERIFICATION_OPERATION,
            ),
        )
        print(str(exc), file=sys.stderr)
        print(f"Integration Result: {result_path}", file=sys.stderr)
        return 1

    print(f"Integration Result: {result_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
