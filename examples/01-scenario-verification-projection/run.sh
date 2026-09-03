#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "usage: $0 <adapter-instance-id> [output-dir]" >&2
  exit 2
fi

instance_id="$1"
example_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
output_dir="${2:-$example_dir/generated}"
core_input="$output_dir/core-input"
projection="$output_dir/projection"

rm -rf "$output_dir"
mkdir -p "$core_input" "$projection"

orbitfabric export integration-input-set \
  "$example_dir/mission" \
  --output-dir "$core_input"

orbitfabric adapter verify "$instance_id" --json \
  > "$output_dir/verify.json"

orbitfabric adapter execute "$instance_id" \
  --operation verification_projection \
  --input-set-manifest "$core_input/integration_input_manifest.json" \
  --profile "$example_dir/profile.yaml" \
  --operation-input "scenario=$example_dir/scenario.yaml" \
  --output-dir "$projection" \
  --json > "$output_dir/execution.json"

test -f "$projection/integration_result.json"
test -f "$projection/verification_projection/verification_projection_plan.json"
test -f "$projection/verification_projection/cosmos/verification.py"
test -f "$projection/verification_projection/cosmos/verification_suite.py"

echo "OrbitFabric OpenC3 COSMOS product example PASS"
echo "output: $output_dir"
