#!/usr/bin/env bash
set -euo pipefail

root="${GITHUB_WORKSPACE:?GITHUB_WORKSPACE is required}"
core="$root/_orbitfabric_core"
cosmos="$root/_cosmos"
work="/tmp/orbitfabric-openc3-cosmos-target-compatibility"
evidence="$work/evidence"
core_input="$work/core-input"
output="$work/output"
scenario="$work/scenario.yaml"
profile="$root/examples/profile.yaml"
manifest="$root/src/orbitfabric_openc3_cosmos_adapter/integration_package.json"

rm -rf "$work"
mkdir -p "$evidence" "$output"

orbitfabric export integration-input-set \
  "$core/examples/demo-3u/mission" \
  --output-dir "$core_input"

cat > "$scenario" <<EOF
scenario:
  id: cosmos_verification_smoke
  name: COSMOS verification smoke
  description: Canonical Scenario to OpenC3 COSMOS compatibility smoke.
mission:
  path: $core/examples/demo-3u/mission
initial_state:
  mode: NOMINAL
  telemetry:
    payload.acquisition.active: true
steps:
  - t: 1
    command: payload.stop_acquisition
  - t: 2
    expect_telemetry:
      payload.acquisition.active: false
EOF

orbitfabric-openc3-cosmos run \
  --operation verification_projection \
  --input-set-manifest "$core_input/integration_input_manifest.json" \
  --profile "$profile" \
  --operation-input scenario "$scenario" \
  --output-dir "$output"

python -m orbitfabric.conformance.integration_contracts result \
  "$manifest" \
  "$output/integration_result.json"

procedure="$output/verification_projection/cosmos/verification.py"
suite="$output/verification_projection/cosmos/verification_suite.py"
plan="$output/verification_projection/verification_projection_plan.json"

python -m py_compile "$procedure" "$suite"

test -f "$cosmos/openc3/python/openc3/script/commands.py"
test -f "$cosmos/openc3/python/openc3/script/api_shared.py"
test -f "$cosmos/openc3/python/openc3/script/suite.py"
grep -q '^def cmd(' "$cosmos/openc3/python/openc3/script/commands.py"
grep -q '^def wait_check(' "$cosmos/openc3/python/openc3/script/api_shared.py"
grep -q '^class Suite:' "$cosmos/openc3/python/openc3/script/suite.py"
grep -q '^class Group:' "$cosmos/openc3/python/openc3/script/suite.py"
grep -q 'from openc3.script import \*' "$procedure"
grep -q 'from openc3.script.suite import Group, Suite' "$suite"

cp "$output/integration_result.json" "$evidence/integration-result.json"
cp "$plan" "$evidence/verification-projection-plan.json"
cp "$procedure" "$evidence/verification.py"
cp "$suite" "$evidence/verification_suite.py"
cat > "$evidence/target-baseline.txt" <<EOF
OpenC3 COSMOS target baseline: v7.3.0
Control: generated Python syntax plus exact-baseline script API/source compatibility
Full live TCP/CTRF runtime: not claimed by this hosted CI control
EOF
