from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


class CtrfValidationError(ValueError):
    """Raised when native COSMOS output does not contain the expected PASS report."""


def extract_ctrf_payload(raw_output: str) -> dict[str, Any]:
    """Extract exactly one CTRF payload from COSMOS Script Runner stdout."""

    decoder = json.JSONDecoder()
    candidates: list[dict[str, Any]] = []
    index = 0

    while index < len(raw_output):
        start = raw_output.find("{", index)
        if start < 0:
            break
        try:
            value, end = decoder.raw_decode(raw_output, start)
        except json.JSONDecodeError:
            index = start + 1
            continue

        if _is_ctrf_payload(value):
            candidates.append(value)
        index = max(end, start + 1)

    if len(candidates) != 1:
        raise CtrfValidationError(
            f"expected exactly one CTRF payload in COSMOS stdout, found {len(candidates)}"
        )
    return candidates[0]


def validate_single_test_pass(payload: dict[str, Any]) -> None:
    try:
        summary = payload["results"]["summary"]
    except (KeyError, TypeError) as exc:
        raise CtrfValidationError("CTRF payload has no results.summary") from exc

    expected = {"tests": 1, "passed": 1, "failed": 0}
    actual = {key: summary.get(key) for key in expected}
    if actual != expected:
        raise CtrfValidationError(f"unexpected CTRF summary: {summary}")


def _is_ctrf_payload(value: Any) -> bool:
    if not isinstance(value, dict):
        return False
    results = value.get("results")
    if not isinstance(results, dict):
        return False
    return isinstance(results.get("summary"), dict)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate canonical COSMOS CTRF acceptance output."
    )
    parser.add_argument("--input", type=Path, required=True, help="Raw Script Runner stdout")
    parser.add_argument("--output", type=Path, required=True, help="Normalized CTRF JSON")
    args = parser.parse_args()

    payload = extract_ctrf_payload(args.input.read_text(encoding="utf-8"))
    validate_single_test_pass(payload)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(args.output.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
