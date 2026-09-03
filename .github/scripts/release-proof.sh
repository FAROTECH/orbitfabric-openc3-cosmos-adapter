#!/usr/bin/env bash
set -euo pipefail

if [[ "${GITHUB_ACTIONS:-}" != "true" ]]; then
  echo "This is the CI release-proof control. Use tools/build_release_bundle.py for local release construction." >&2
  exit 2
fi

root="${GITHUB_WORKSPACE:?GITHUB_WORKSPACE is required}"
work="/tmp/orbitfabric-template-release-proof"
state="$work/state"
evidence="$work/evidence"
wheelhouse="$work/wheelhouse"
release_dir="$work/release"

export ORBITFABRIC_STATE_DIR="$state"

rm -rf "$work"
mkdir -p "$evidence" "$wheelhouse" "$release_dir"

cd "$root"
rm -rf dist
python -m build --wheel
wheel="$(realpath "$(find "$root/dist" -maxdepth 1 -name '*.whl' -print -quit)")"
test -n "$wheel"

python tools/build_release_bundle.py \
  --wheel "$wheel" \
  --authority template.local \
  --publisher orbitfabric \
  --name dummy-adapter \
  --output-dir "$release_dir"

descriptor="$release_dir/adapter-release.json"
lock="$release_dir/adapter-project-lock.json"

python - <<PY
from orbitfabric.adapter_manager import ProjectLockService
from orbitfabric.conformance.adapter_release import load_release_descriptor

load_release_descriptor("$descriptor")
ProjectLockService().load("$lock")
PY

cp "$descriptor" "$evidence/adapter-release.json"
cp "$lock" "$evidence/adapter-project-lock.json"
cp "$release_dir/SHA256SUMS" "$evidence/SHA256SUMS"

python -m pip download --dest "$wheelhouse" "$wheel"
export PIP_NO_INDEX=1
export PIP_FIND_LINKS="$wheelhouse"

set +e
orbitfabric adapter lock check "$lock" --json > "$evidence/before-check.json"
before_status=$?
set -e
test "$before_status" -ne 0

python - <<'PY'
import json
from pathlib import Path

report = json.loads(Path("/tmp/orbitfabric-template-release-proof/evidence/before-check.json").read_text())
assert report["status"] == "NOT_SATISFIED"
assert report["adapters"][0]["status"] == "MISSING"
PY

orbitfabric adapter lock install "$lock" \
  --source-coordinate "template.local:orbitfabric/dummy-adapter" \
  --release-descriptor "$descriptor" \
  --artifact "$wheel" \
  --json | tee "$evidence/install-from-lock.json"

python - <<'PY' > "$work/install-env"
import json
from pathlib import Path

report = json.loads(
    Path("/tmp/orbitfabric-template-release-proof/evidence/install-from-lock.json").read_text()
)
assert report["before_status"] == "MISSING"
assert report["action"] == "INSTALLED"
assert report["after_status"] == "MATCH"
assert report["installed_instance_id"]
print("INSTANCE_ID=" + report["installed_instance_id"])
PY
source "$work/install-env"

orbitfabric adapter lock check "$lock" --json | tee "$evidence/after-check.json"
python - <<'PY'
import json
from pathlib import Path

report = json.loads(Path("/tmp/orbitfabric-template-release-proof/evidence/after-check.json").read_text())
assert report["status"] == "MATCH"
assert report["adapters"][0]["status"] == "MATCH"
PY

orbitfabric adapter lock install "$lock" \
  --source-coordinate "template.local:orbitfabric/dummy-adapter" \
  --release-descriptor "$descriptor" \
  --artifact "$wheel" \
  --json | tee "$evidence/second-install-from-lock.json"
python - <<'PY'
import json
from pathlib import Path

report = json.loads(
    Path("/tmp/orbitfabric-template-release-proof/evidence/second-install-from-lock.json").read_text()
)
assert report["before_status"] == "MATCH"
assert report["action"] == "NOOP"
assert report["after_status"] == "MATCH"
assert report["installed_instance_id"] is None
PY

orbitfabric adapter verify "$INSTANCE_ID" --json | tee "$evidence/verify.json"
orbitfabric adapter remove "$INSTANCE_ID" --json | tee "$evidence/remove.json"
orbitfabric adapter list --json | tee "$evidence/final-inventory.json"

python - <<'PY'
import json
from pathlib import Path

inventory = json.loads(
    Path("/tmp/orbitfabric-template-release-proof/evidence/final-inventory.json").read_text()
)
assert inventory == []
PY

unset PIP_NO_INDEX
unset PIP_FIND_LINKS
