#!/usr/bin/env bash
set -euo pipefail

if [[ "${GITHUB_ACTIONS:-}" != "true" ]]; then
  echo "This is a destructive CI isolation proof and must run only inside GitHub Actions." >&2
  exit 2
fi

root="${GITHUB_WORKSPACE:?GITHUB_WORKSPACE is required}"
core="$root/_orbitfabric_core"
work="/tmp/orbitfabric-template-installed-lifecycle"
state="$work/state"
evidence="$work/evidence"
wheelhouse="$work/wheelhouse"
release_dir="$work/release"
core_input="$work/core-input"
project_output="$work/project-output"
verification_output="$work/verification-output"

export ORBITFABRIC_STATE_DIR="$state"

rm -rf "$work"
mkdir -p "$evidence" "$wheelhouse" "$release_dir"

python -m build --wheel
wheel="$(realpath "$(find "$root/dist" -maxdepth 1 -name '*.whl' -print -quit)")"
test -n "$wheel"

orbitfabric export integration-input-set \
  "$core/examples/demo-3u/mission" \
  --output-dir "$core_input"
test -f "$core_input/integration_input_manifest.json"

python -m pip download --dest "$wheelhouse" "$wheel"
test -n "$(find "$wheelhouse" -maxdepth 1 -type f -print -quit)"

python tools/build_release_bundle.py \
  --wheel "$wheel" \
  --authority explicit-template-control \
  --publisher orbitfabric-template \
  --name dummy-adapter \
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

mkdir -p "$project_output"
PYTHONPATH= orbitfabric adapter execute "$INSTANCE_ID" \
  --operation project \
  --input-set-manifest "$core_input/integration_input_manifest.json" \
  --profile "$root/examples/profile.yaml" \
  --output-dir "$project_output" \
  --json | tee "$evidence/project-execution.json"
python -m orbitfabric.conformance.integration_contracts result \
  "$INSTALLED_MANIFEST" \
  "$project_output/integration_result.json"
PROJECT_OUTPUT="$project_output" python - <<'PY'
import json
import os
from pathlib import Path

output = Path(os.environ["PROJECT_OUTPUT"])
result = json.loads((output / "integration_result.json").read_text(encoding="utf-8"))
projection = json.loads((output / "dummy_projection.json").read_text(encoding="utf-8"))
assert result["result"] == "succeeded"
assert result["operation"]["id"] == "project"
assert result["mission"]["id"] == "demo-3u"
assert result["inputs"]["operation_inputs"] == []
assert projection["telemetry"][0]["source_id"] == "eps.battery.voltage"
PY
cp "$project_output/integration_result.json" "$evidence/project-integration-result.json"
cp "$project_output/dummy_projection.json" "$evidence/dummy-projection.json"

scenario="$core/examples/demo-3u/scenarios/battery_low_during_payload.yaml"
mkdir -p "$verification_output"
PYTHONPATH= orbitfabric adapter execute "$INSTANCE_ID" \
  --operation verification_projection \
  --input-set-manifest "$core_input/integration_input_manifest.json" \
  --profile "$root/examples/profile.yaml" \
  --operation-input "scenario=$scenario" \
  --output-dir "$verification_output" \
  --json | tee "$evidence/verification-execution.json"
python -m orbitfabric.conformance.integration_contracts result \
  "$INSTALLED_MANIFEST" \
  "$verification_output/integration_result.json"
SCENARIO="$scenario" VERIFICATION_OUTPUT="$verification_output" python - <<'PY'
import hashlib
import json
import os
from pathlib import Path

scenario = Path(os.environ["SCENARIO"])
output = Path(os.environ["VERIFICATION_OUTPUT"])
result = json.loads((output / "integration_result.json").read_text(encoding="utf-8"))
plan = json.loads((output / "dummy_verification_plan.json").read_text(encoding="utf-8"))
provenance = result["inputs"]["operation_inputs"]
assert result["result"] == "succeeded"
assert result["operation"]["id"] == "verification_projection"
assert len(provenance) == 1
assert provenance[0]["role"] == "scenario"
assert provenance[0]["id"] == "battery_low_during_payload"
assert provenance[0]["sha256"] == hashlib.sha256(scenario.read_bytes()).hexdigest()
assert plan["scenario"]["id"] == "battery_low_during_payload"
PY
cp "$verification_output/integration_result.json" "$evidence/verification-integration-result.json"
cp "$verification_output/dummy_verification_plan.json" "$evidence/dummy-verification-plan.json"

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
