#!/usr/bin/env bash
set -euo pipefail

if [[ "${GITHUB_ACTIONS:-}" != "true" ]]; then
  echo "This is a destructive CI isolation proof and must run only inside GitHub Actions." >&2
  exit 2
fi

root="${GITHUB_WORKSPACE:?GITHUB_WORKSPACE is required}"
core="$root/_orbitfabric_core"
work="/tmp/orbitfabric-openc3-cosmos-installed-lifecycle"
state="$work/state"
evidence="$work/evidence"
wheelhouse="$work/wheelhouse"
release_dir="$work/release"
core_input="$work/core-input"
verification_output="$work/verification-output"
scenario="$work/scenario.yaml"
profile="$root/examples/profile.yaml"

export ORBITFABRIC_STATE_DIR="$state"

rm -rf "$work"
mkdir -p "$evidence" "$wheelhouse" "$release_dir" "$verification_output"

cd "$root"
rm -rf dist
python -m build --wheel
wheel="$(realpath "$(find "$root/dist" -maxdepth 1 -name '*.whl' -print -quit)")"
test -n "$wheel"

orbitfabric export integration-input-set \
  "$core/examples/demo-3u/mission" \
  --output-dir "$core_input"
test -f "$core_input/integration_input_manifest.json"

cat > "$scenario" <<EOF
scenario:
  id: cosmos_verification_smoke
  name: COSMOS verification smoke
  description: Installed lifecycle Scenario for the canonical OpenC3 COSMOS adapter.
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

python -m pip download --dest "$wheelhouse" "$wheel"
python -m pip download --dest "$wheelhouse" "hatchling>=1.24"
test -n "$(find "$wheelhouse" -maxdepth 1 -type f -print -quit)"

python tools/build_release_bundle.py \
  --wheel "$wheel" \
  --authority local.adapter.test \
  --publisher orbitfabric \
  --name openc3-cosmos \
  --output-dir "$release_dir"

descriptor="$release_dir/adapter-release.json"
descriptor_sha="$(sha256sum "$descriptor" | awk '{print $1}')"
cp "$descriptor" "$evidence/release-descriptor.json"
cp "$core_input/integration_input_manifest.json" "$evidence/core-input-manifest.json"
sha256sum "$wheel" > "$evidence/adapter-wheel.sha256"

export PIP_NO_INDEX=1
export PIP_FIND_LINKS="$wheelhouse"
orbitfabric adapter install "$descriptor" \
  --artifact "$wheel" \
  --descriptor-sha256 "$descriptor_sha" \
  --json | tee "$evidence/install.json"
unset PIP_NO_INDEX
unset PIP_FIND_LINKS

EVIDENCE="$evidence" python - <<'PY' > "$work/install-env"
import json
import os
from pathlib import Path

record = json.loads((Path(os.environ["EVIDENCE"]) / "install.json").read_text(encoding="utf-8"))
assert record["backend_id"] == "python-wheel-managed-env"
assert Path(record["execution_argv_prefix"][0]).is_absolute()
assert Path(record["manifest_path"]).is_file()
print("INSTANCE_ID=" + record["instance_id"])
print("INSTALLED_MANIFEST=" + record["manifest_path"])
PY
source "$work/install-env"

rm -f "$wheel" "$descriptor"
rm -rf "$wheelhouse"
rm -rf "$root/src"
test ! -e "$wheel"
test ! -d "$root/src"

cd /tmp
PYTHONPATH= orbitfabric adapter verify "$INSTANCE_ID" --json \
  | tee "$evidence/verify.json"
EVIDENCE="$evidence" python - <<'PY'
import json
import os
from pathlib import Path

report = json.loads((Path(os.environ["EVIDENCE"]) / "verify.json").read_text(encoding="utf-8"))
for name in (
    "release_descriptor_integrity",
    "manifest_integrity",
    "manifest_conformance",
    "execution_binding",
    "backend_materialization",
):
    assert report[name]["status"] == "PASS", (name, report[name])
PY

PYTHONPATH= orbitfabric adapter execute "$INSTANCE_ID" \
  --operation verification_projection \
  --input-set-manifest "$core_input/integration_input_manifest.json" \
  --profile "$profile" \
  --operation-input "scenario=$scenario" \
  --output-dir "$verification_output" \
  --json | tee "$evidence/verification-execution.json"

python -m orbitfabric.conformance.integration_contracts result \
  "$INSTALLED_MANIFEST" \
  "$verification_output/integration_result.json"

SCENARIO="$scenario" OUTPUT="$verification_output" python - <<'PY'
import hashlib
import json
import os
from pathlib import Path

scenario = Path(os.environ["SCENARIO"])
output = Path(os.environ["OUTPUT"])
result = json.loads((output / "integration_result.json").read_text(encoding="utf-8"))
plan = json.loads(
    (output / "verification_projection" / "verification_projection_plan.json").read_text(
        encoding="utf-8"
    )
)

assert result["result"] == "succeeded"
assert result["operation"]["id"] == "verification_projection"
assert result["mission"]["id"] == "demo-3u"
provenance = result["inputs"]["operation_inputs"]
assert len(provenance) == 1
assert provenance[0]["role"] == "scenario"
assert provenance[0]["id"] == "cosmos_verification_smoke"
assert provenance[0]["sha256"] == hashlib.sha256(scenario.read_bytes()).hexdigest()
assert [item["id"] for item in result["artifacts"]] == [
    "verification.plan",
    "verification.cosmos_procedure",
    "verification.cosmos_suite",
]
assert plan["status"] == "executable_subset"
assert plan["target"]["baseline"] == "v7.3.0"
assert plan["accounting"]["resolved_operations"] == 2
assert (output / "verification_projection" / "cosmos" / "verification.py").is_file()
assert (output / "verification_projection" / "cosmos" / "verification_suite.py").is_file()
PY

cp "$verification_output/integration_result.json" \
  "$evidence/verification-integration-result.json"
cp "$verification_output/verification_projection/verification_projection_plan.json" \
  "$evidence/verification-projection-plan.json"

orbitfabric adapter remove "$INSTANCE_ID" --json | tee "$evidence/remove.json"
orbitfabric adapter list --json | tee "$evidence/final-inventory.json"
EVIDENCE="$evidence" python - <<'PY'
import json
import os
from pathlib import Path

inventory = json.loads(
    (Path(os.environ["EVIDENCE"]) / "final-inventory.json").read_text(encoding="utf-8")
)
assert inventory == []
PY
