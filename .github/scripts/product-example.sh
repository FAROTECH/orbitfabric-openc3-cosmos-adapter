#!/usr/bin/env bash
set -euo pipefail

if [[ "${GITHUB_ACTIONS:-}" != "true" ]]; then
  echo "This product-example isolation proof must run only inside GitHub Actions." >&2
  exit 2
fi

root="${GITHUB_WORKSPACE:?GITHUB_WORKSPACE is required}"
work="/tmp/orbitfabric-openc3-cosmos-product-example"
state="$work/state"
evidence="$work/evidence"
wheelhouse="$work/wheelhouse"
release_dir="$work/release"
example="$root/examples/01-scenario-verification-projection"
output="$work/output"

export ORBITFABRIC_STATE_DIR="$state"

rm -rf "$work"
mkdir -p "$evidence" "$wheelhouse" "$release_dir"

cd "$root"
rm -rf dist
python -m build --wheel
wheel="$(realpath "$(find "$root/dist" -maxdepth 1 -name '*.whl' -print -quit)")"
test -n "$wheel"

python -m pip download --dest "$wheelhouse" "$wheel"
python -m pip download --dest "$wheelhouse" "hatchling>=1.24"

python tools/build_release_bundle.py \
  --wheel "$wheel" \
  --authority local.adapter.test \
  --publisher orbitfabric \
  --name openc3-cosmos \
  --output-dir "$release_dir"

descriptor="$release_dir/adapter-release.json"
descriptor_sha="$(sha256sum "$descriptor" | awk '{print $1}')"
cp "$descriptor" "$evidence/adapter-release.json"
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

rm -f "$wheel"
rm -rf "$wheelhouse"
rm -rf "$root/src"
test ! -d "$root/src"

cd /tmp
bash "$example/run.sh" "$INSTANCE_ID" "$output" \
  | tee "$evidence/example.stdout"

python -m orbitfabric.conformance.integration_contracts result \
  "$INSTALLED_MANIFEST" \
  "$output/projection/integration_result.json"

OUTPUT="$output" python - <<'PY'
import json
import os
from pathlib import Path

output = Path(os.environ["OUTPUT"])
result = json.loads((output / "projection" / "integration_result.json").read_text(encoding="utf-8"))
plan = json.loads(
    (output / "projection" / "verification_projection" / "verification_projection_plan.json").read_text(
        encoding="utf-8"
    )
)
assert result["result"] == "succeeded"
assert result["operation"]["id"] == "verification_projection"
assert result["mission"]["id"] == "demo-3u"
assert plan["status"] == "executable_subset"
assert plan["target"]["baseline"] == "v7.3.0"
assert plan["accounting"]["resolved_operations"] == 2
PY

cp "$output/verify.json" "$evidence/verify.json"
cp "$output/execution.json" "$evidence/execution.json"
cp "$output/projection/integration_result.json" "$evidence/integration-result.json"
cp "$output/projection/verification_projection/verification_projection_plan.json" \
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
