#!/usr/bin/env bash
set -euo pipefail

if [[ "${GITHUB_ACTIONS:-}" != "true" ]]; then
  echo "This is the CI release-proof control. Use tools/build_release_bundle.py locally." >&2
  exit 2
fi

root="${GITHUB_WORKSPACE:?GITHUB_WORKSPACE is required}"
work="/tmp/orbitfabric-openc3-cosmos-release-proof"
state="$work/state"
evidence="$work/evidence"
wheelhouse="$work/wheelhouse"
release_dir="$work/release"
publisher_release_dir="$work/publisher-release"

export ORBITFABRIC_STATE_DIR="$state"

rm -rf "$work"
mkdir -p "$evidence" "$wheelhouse" "$release_dir" "$publisher_release_dir"

cd "$root"
rm -rf dist
python -m build --wheel
wheel="$(realpath "$(find "$root/dist" -maxdepth 1 -name '*.whl' -print -quit)")"
test -n "$wheel"

python tools/build_release_bundle.py \
  --wheel "$wheel" \
  --authority local.adapter.test \
  --publisher orbitfabric \
  --name openc3-cosmos \
  --output-dir "$release_dir"

descriptor="$release_dir/adapter-release.json"
lock="$release_dir/adapter-project-lock.json"

python - <<PY
from orbitfabric.adapter_manager import ProjectLockService
from orbitfabric.conformance.adapter_release import load_release_descriptor

release = load_release_descriptor("$descriptor")
assert release["source_coordinate"] == {
    "authority": "local.adapter.test",
    "publisher": "orbitfabric",
    "name": "openc3-cosmos",
}
assert release["release_version"] == "0.1.0.dev0"
ProjectLockService().load("$lock")
PY

cp "$descriptor" "$evidence/adapter-release.json"
cp "$lock" "$evidence/adapter-project-lock.json"
cp "$release_dir/SHA256SUMS" "$evidence/SHA256SUMS"

python tools/build_release_bundle.py \
  --wheel "$wheel" \
  --authority local.adapter.test \
  --publisher orbitfabric \
  --name openc3-cosmos \
  --release-only \
  --output-dir "$publisher_release_dir"

test -f "$publisher_release_dir/adapter-release.json"
test -f "$publisher_release_dir/SHA256SUMS"
test ! -e "$publisher_release_dir/adapter-project-lock.json"

mkdir -p "$evidence/publisher-release"
cp "$publisher_release_dir/adapter-release.json" \
  "$evidence/publisher-release/adapter-release.json"
cp "$publisher_release_dir/SHA256SUMS" "$evidence/publisher-release/SHA256SUMS"
cp "$wheel" "$evidence/publisher-release/$(basename "$wheel")"

python -m pip download --dest "$wheelhouse" "$wheel"
python -m pip download --dest "$wheelhouse" "hatchling>=1.24"
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

report = json.loads(
    Path("/tmp/orbitfabric-openc3-cosmos-release-proof/evidence/before-check.json").read_text()
)
assert report["status"] == "NOT_SATISFIED"
assert report["adapters"][0]["status"] == "MISSING"
PY

orbitfabric adapter lock install "$lock" \
  --source-coordinate "local.adapter.test:orbitfabric/openc3-cosmos" \
  --release-descriptor "$descriptor" \
  --artifact "$wheel" \
  --json | tee "$evidence/install-from-lock.json"

python - <<'PY' > "$work/install-env"
import json
from pathlib import Path

report = json.loads(
    Path(
        "/tmp/orbitfabric-openc3-cosmos-release-proof/evidence/install-from-lock.json"
    ).read_text()
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

report = json.loads(
    Path("/tmp/orbitfabric-openc3-cosmos-release-proof/evidence/after-check.json").read_text()
)
assert report["status"] == "MATCH"
assert report["adapters"][0]["status"] == "MATCH"
PY

orbitfabric adapter lock install "$lock" \
  --source-coordinate "local.adapter.test:orbitfabric/openc3-cosmos" \
  --release-descriptor "$descriptor" \
  --artifact "$wheel" \
  --json | tee "$evidence/second-install-from-lock.json"
python - <<'PY'
import json
from pathlib import Path

report = json.loads(
    Path(
        "/tmp/orbitfabric-openc3-cosmos-release-proof/evidence/second-install-from-lock.json"
    ).read_text()
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
    Path(
        "/tmp/orbitfabric-openc3-cosmos-release-proof/evidence/final-inventory.json"
    ).read_text()
)
assert inventory == []
PY

unset PIP_NO_INDEX
unset PIP_FIND_LINKS
