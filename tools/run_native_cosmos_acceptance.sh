#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK_DIR="${NATIVE_ACCEPTANCE_WORK_DIR:-${ROOT}/generated/native-cosmos-acceptance}"
EVIDENCE_DIR="${EVIDENCE_DIR:-${WORK_DIR}/evidence}"
CORE_DIR="${CORE_CHECKOUT_DIR:-${ROOT}/generated/native-acceptance-orbitfabric-core}"
COSMOS_PROJECT_DIR="${COSMOS_PROJECT_DIR:-${ROOT}/generated/native-acceptance-cosmos-project}"
CORE_REPO="https://github.com/FAROTECH/orbitfabric.git"
CORE_COMMIT="4377d6656c62aa1dc19a7ed81d2de872b6b22ccd"
COSMOS_PROJECT_REPO="https://github.com/OpenC3/cosmos-project.git"
COSMOS_PROJECT_COMMIT="9eb454f06fe0113d05aa6945d88b627155a2aa47"
COSMOS_BASELINE="v7.3.0"
PLUGIN_VERSION="0.1.0"
SIMULATOR_HOST="${COSMOS_SIMULATOR_HOST:-host.docker.internal}"
API_PASSWORD="${OPENC3_API_PASSWORD:-orbitfabric-canonical-acceptance}"
COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-orbitfabric_openc3_acceptance}"
SIMULATOR_PID=""

export OPENC3_API_PASSWORD="${API_PASSWORD}"
export OPENC3_DEMO=0
export COMPOSE_PROJECT_NAME
export OPENC3_USER_ID="${OPENC3_USER_ID:-$(id -u)}"
export OPENC3_GROUP_ID="${OPENC3_GROUP_ID:-$(id -g)}"

log() {
  printf '[cosmos-native-acceptance] %s\n' "$*"
}

cleanup() {
  status=$?
  if [[ -n "${SIMULATOR_PID}" ]] && kill -0 "${SIMULATOR_PID}" 2>/dev/null; then
    kill "${SIMULATOR_PID}" 2>/dev/null || true
    wait "${SIMULATOR_PID}" 2>/dev/null || true
  fi
  if [[ -x "${COSMOS_PROJECT_DIR}/openc3.sh" ]]; then
    (
      cd "${COSMOS_PROJECT_DIR}"
      ./openc3.sh cleanup local force >/dev/null 2>&1 || true
    )
  fi
  exit "${status}"
}
trap cleanup EXIT INT TERM

require_command() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "Required command not found: $1" >&2
    exit 2
  }
}

wait_for_http() {
  local url="$1"
  local attempts="${2:-120}"
  for ((i=1; i<=attempts; i++)); do
    if curl -fsS "${url}" >/dev/null 2>&1; then
      return 0
    fi
    sleep 2
  done
  return 1
}

wait_for_log_event() {
  local path="$1"
  local event="$2"
  local attempts="${3:-60}"
  for ((i=1; i<=attempts; i++)); do
    if [[ -f "${path}" ]] && grep -q "\"event\": \"${event}\"" "${path}"; then
      return 0
    fi
    sleep 1
  done
  return 1
}

cosmos_cli() {
  local local_dir="$1"
  shift

  local compose_args=(
    docker compose
    --project-directory "${COSMOS_PROJECT_DIR}"
    --env-file "${COSMOS_PROJECT_DIR}/.env"
  )
  if [[ -f "${COSMOS_PROJECT_DIR}/.env.local" ]]; then
    compose_args+=(--env-file "${COSMOS_PROJECT_DIR}/.env.local")
  fi
  compose_args+=(-f "${COSMOS_PROJECT_DIR}/compose.yaml")
  if [[ -f "${COSMOS_PROJECT_DIR}/compose.override.yaml" ]]; then
    compose_args+=(-f "${COSMOS_PROJECT_DIR}/compose.override.yaml")
  fi

  (
    cd "${local_dir}"
    "${compose_args[@]}" run -T --rm \
      -v "$(pwd):/openc3/local:z" \
      -w /openc3/local \
      -e OPENC3_API_PASSWORD="${OPENC3_API_PASSWORD}" \
      --no-deps \
      openc3-cosmos-cmd-tlm-api \
      ruby /openc3/bin/openc3cli "$@"
  )
}

cosmos_report_to_ctrf() {
  local report_path="$1"

  local compose_args=(
    docker compose
    --project-directory "${COSMOS_PROJECT_DIR}"
    --env-file "${COSMOS_PROJECT_DIR}/.env"
  )
  if [[ -f "${COSMOS_PROJECT_DIR}/.env.local" ]]; then
    compose_args+=(--env-file "${COSMOS_PROJECT_DIR}/.env.local")
  fi
  compose_args+=(-f "${COSMOS_PROJECT_DIR}/compose.yaml")
  if [[ -f "${COSMOS_PROJECT_DIR}/compose.override.yaml" ]]; then
    compose_args+=(-f "${COSMOS_PROJECT_DIR}/compose.override.yaml")
  fi

  (
    cd "${COSMOS_PROJECT_DIR}"
    "${compose_args[@]}" run -T --rm \
      -e OPENC3_API_PASSWORD="${OPENC3_API_PASSWORD}" \
      --no-deps \
      openc3-cosmos-cmd-tlm-api \
      ruby \
        -ropenc3 \
        -ropenc3/utilities/bucket \
        -ropenc3/utilities/ctrf \
        -rjson \
        -e '
report_path = ARGV.fetch(0)
tmp_path = "/tmp/orbitfabric-script-report-#{Process.pid}.txt"

begin
  OpenC3::Bucket.getClient().get_object(
    bucket: ENV.fetch("OPENC3_LOGS_BUCKET"),
    key: report_path,
    path: tmp_path
  )

  unless File.file?(tmp_path)
    raise "COSMOS Script Runner report not found: #{report_path}"
  end

  report = File.binread(tmp_path)
  puts JSON.generate(OpenC3::Ctrf.convert_report(report))
ensure
  File.delete(tmp_path) if File.exist?(tmp_path)
end
' "${report_path}"
  )
}

require_command git
require_command docker
require_command curl
require_command python

docker compose version >/dev/null

if [[ "${ALLOW_DIRTY_ACCEPTANCE:-0}" != "1" ]]; then
  if ! git -C "${ROOT}" diff --quiet || ! git -C "${ROOT}" diff --cached --quiet; then
    echo "Native acceptance requires a clean adapter checkout. Set ALLOW_DIRTY_ACCEPTANCE=1 only for local debugging." >&2
    exit 2
  fi
fi

ADAPTER_SOURCE_COMMIT="$(git -C "${ROOT}" rev-parse HEAD)"

rm -rf "${WORK_DIR}"
mkdir -p "${WORK_DIR}" "${EVIDENCE_DIR}"

if curl -fsS http://localhost:2900 >/dev/null 2>&1; then
  echo "Port 2900 already serves an HTTP endpoint. Stop the existing COSMOS instance before running this isolated acceptance harness." >&2
  exit 2
fi

log "preparing exact Core fixture baseline"
if [[ ! -d "${CORE_DIR}/.git" ]]; then
  git clone --filter=blob:none "${CORE_REPO}" "${CORE_DIR}" \
    >"${EVIDENCE_DIR}/core-clone.log" 2>&1
fi
git -C "${CORE_DIR}" fetch origin "${CORE_COMMIT}" \
  >>"${EVIDENCE_DIR}/core-clone.log" 2>&1
git -C "${CORE_DIR}" checkout --detach "${CORE_COMMIT}" \
  >>"${EVIDENCE_DIR}/core-clone.log" 2>&1
if [[ "$(git -C "${CORE_DIR}" rev-parse HEAD)" != "${CORE_COMMIT}" ]]; then
  echo "Unexpected OrbitFabric Core checkout" >&2
  exit 2
fi

log "building and installing the canonical adapter wheel"
VENV="${WORK_DIR}/venv"
DIST="${WORK_DIR}/dist"
python -m venv "${VENV}"
PYTHON="${VENV}/bin/python"
PIP="${VENV}/bin/pip"
"${PIP}" install --upgrade pip build >"${EVIDENCE_DIR}/python-environment.log" 2>&1
"${PYTHON}" -m build --wheel --outdir "${DIST}" "${ROOT}" \
  >"${EVIDENCE_DIR}/wheel-build.log" 2>&1
WHEEL="$(find "${DIST}" -maxdepth 1 -name '*.whl' -print -quit)"
test -n "${WHEEL}"
"${PIP}" install "${WHEEL}" >>"${EVIDENCE_DIR}/python-environment.log" 2>&1

CORE_INPUT="${WORK_DIR}/core-input"
SCENARIO="${WORK_DIR}/scenario.yaml"
OUTPUT="${WORK_DIR}/adapter-output"
PROFILE="${ROOT}/examples/profile.yaml"
MANIFEST="${ROOT}/src/orbitfabric_openc3_cosmos_adapter/integration_package.json"

log "generating canonical Core input and Scenario"
"${VENV}/bin/orbitfabric" export integration-input-set \
  "${CORE_DIR}/examples/demo-3u/mission" \
  --output-dir "${CORE_INPUT}" \
  >"${EVIDENCE_DIR}/core-input.log" 2>&1

cat >"${SCENARIO}" <<EOF
scenario:
  id: cosmos_native_acceptance
  name: COSMOS native acceptance
  description: Canonical adapter native OpenC3 COSMOS runtime acceptance.
mission:
  path: ${CORE_DIR}/examples/demo-3u/mission
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

log "projecting canonical adapter artifacts"
"${VENV}/bin/orbitfabric-openc3-cosmos" run \
  --operation verification_projection \
  --input-set-manifest "${CORE_INPUT}/integration_input_manifest.json" \
  --profile "${PROFILE}" \
  --operation-input scenario "${SCENARIO}" \
  --output-dir "${OUTPUT}" \
  >"${EVIDENCE_DIR}/adapter-projection.log" 2>&1

"${PYTHON}" -m orbitfabric.conformance.integration_contracts result \
  "${MANIFEST}" \
  "${OUTPUT}/integration_result.json" \
  >>"${EVIDENCE_DIR}/adapter-projection.log" 2>&1

PLAN="${OUTPUT}/verification_projection/verification_projection_plan.json"
PROCEDURE="${OUTPUT}/verification_projection/cosmos/verification.py"
SUITE="${OUTPUT}/verification_projection/cosmos/verification_suite.py"
test -f "${PLAN}"
test -f "${PROCEDURE}"
test -f "${SUITE}"

log "preparing pinned COSMOS ${COSMOS_BASELINE} runtime"
if [[ ! -d "${COSMOS_PROJECT_DIR}/.git" ]]; then
  git clone --filter=blob:none "${COSMOS_PROJECT_REPO}" "${COSMOS_PROJECT_DIR}" \
    >"${EVIDENCE_DIR}/cosmos-clone.log" 2>&1
fi
git -C "${COSMOS_PROJECT_DIR}" fetch origin "${COSMOS_PROJECT_COMMIT}" \
  >>"${EVIDENCE_DIR}/cosmos-clone.log" 2>&1
git -C "${COSMOS_PROJECT_DIR}" checkout --detach "${COSMOS_PROJECT_COMMIT}" \
  >>"${EVIDENCE_DIR}/cosmos-clone.log" 2>&1
if [[ "$(git -C "${COSMOS_PROJECT_DIR}" rev-parse HEAD)" != "${COSMOS_PROJECT_COMMIT}" ]]; then
  echo "Unexpected COSMOS project checkout" >&2
  exit 2
fi

(
  cd "${COSMOS_PROJECT_DIR}"
  ./openc3.sh cleanup local force
) >"${EVIDENCE_DIR}/cosmos-preclean.log" 2>&1 || true

log "starting isolated COSMOS runtime"
(
  cd "${COSMOS_PROJECT_DIR}"
  ./openc3.sh run
) >"${EVIDENCE_DIR}/cosmos-start.log" 2>&1

if ! wait_for_http http://localhost:2900 120; then
  (
    cd "${COSMOS_PROJECT_DIR}"
    ./openc3.sh status || true
    docker compose logs --tail=200 || true
  ) >"${EVIDENCE_DIR}/cosmos-failure.log" 2>&1
  echo "COSMOS did not become reachable" >&2
  exit 1
fi

log "initializing isolated COSMOS API password"
set_password_ok=0
for _ in {1..30}; do
  if cosmos_cli "${COSMOS_PROJECT_DIR}" setpassword \
    >"${EVIDENCE_DIR}/setpassword.log" 2>&1; then
    set_password_ok=1
    break
  fi
  sleep 2
done
if [[ "${set_password_ok}" != "1" ]]; then
  echo "COSMOS password initialization failed" >&2
  exit 1
fi

PLUGIN_DIR="${COSMOS_PROJECT_DIR}/openc3-cosmos-ofdemo"
rm -rf "${PLUGIN_DIR}"

log "generating OFDEMO acceptance plugin with native COSMOS tooling"
{
  cosmos_cli "${COSMOS_PROJECT_DIR}" generate plugin OFDEMO --python
  cosmos_cli "${PLUGIN_DIR}" generate target OFDEMO --python
} >"${EVIDENCE_DIR}/plugin-generate.log" 2>&1

"${PYTHON}" - "${ROOT}/acceptance/cosmos/plugin-overlay/plugin.txt.in" \
  "${PLUGIN_DIR}/plugin.txt" "${SIMULATOR_HOST}" <<'PY'
from pathlib import Path
import sys

template = Path(sys.argv[1]).read_text(encoding="utf-8")
rendered = template.replace("__OFDEMO_HOST__", sys.argv[3])
if "__OFDEMO_HOST__" in rendered:
    raise SystemExit("OFDEMO plugin host placeholder was not resolved")
Path(sys.argv[2]).write_text(rendered, encoding="utf-8")
PY

cp "${ROOT}/acceptance/cosmos/plugin-overlay/targets/OFDEMO/target.txt" \
  "${PLUGIN_DIR}/targets/OFDEMO/target.txt"
cp "${ROOT}/acceptance/cosmos/plugin-overlay/targets/OFDEMO/cmd_tlm/cmd.txt" \
  "${PLUGIN_DIR}/targets/OFDEMO/cmd_tlm/cmd.txt"
cp "${ROOT}/acceptance/cosmos/plugin-overlay/targets/OFDEMO/cmd_tlm/tlm.txt" \
  "${PLUGIN_DIR}/targets/OFDEMO/cmd_tlm/tlm.txt"
cp "${PROCEDURE}" "${PLUGIN_DIR}/targets/OFDEMO/procedures/verification.py"
cp "${SUITE}" "${PLUGIN_DIR}/targets/OFDEMO/procedures/verification_suite.py"

log "building and validating OFDEMO plugin"
cosmos_cli "${PLUGIN_DIR}" rake build VERSION="${PLUGIN_VERSION}" \
  >"${EVIDENCE_DIR}/plugin-build.log" 2>&1
GEM_PATH="${PLUGIN_DIR}/openc3-cosmos-ofdemo-${PLUGIN_VERSION}.gem"
GEM_NAME="$(basename "${GEM_PATH}")"
if [[ ! -f "${GEM_PATH}" ]]; then
  echo "Expected OFDEMO plugin gem was not produced: ${GEM_PATH}" >&2
  exit 1
fi
cosmos_cli "${PLUGIN_DIR}" validate "${GEM_NAME}" DEFAULT \
  >"${EVIDENCE_DIR}/plugin-validate.log" 2>&1

log "starting external OFDEMO simulator"
"${PYTHON}" "${ROOT}/acceptance/cosmos/simulator/ofdemo_simulator.py" \
  >"${EVIDENCE_DIR}/simulator.jsonl" 2>"${EVIDENCE_DIR}/simulator.stderr" &
SIMULATOR_PID=$!
if ! wait_for_log_event "${EVIDENCE_DIR}/simulator.jsonl" simulator_ready 20; then
  echo "OFDEMO simulator did not start" >&2
  exit 1
fi

log "loading OFDEMO plugin into COSMOS"
cosmos_cli "${PLUGIN_DIR}" load "${GEM_NAME}" DEFAULT \
  >"${EVIDENCE_DIR}/plugin-load.log" 2>&1
if ! wait_for_log_event "${EVIDENCE_DIR}/simulator.jsonl" command_client_connected 60; then
  echo "COSMOS command interface did not connect to OFDEMO simulator" >&2
  exit 1
fi
if ! wait_for_log_event "${EVIDENCE_DIR}/simulator.jsonl" telemetry_client_connected 60; then
  echo "COSMOS telemetry interface did not connect to OFDEMO simulator" >&2
  exit 1
fi

log "running canonical generated suite through COSMOS Script Runner"

: >"${EVIDENCE_DIR}/script-runner.stdout"
: >"${EVIDENCE_DIR}/script-runner.stderr"

SCRIPT_ID="$(
  cosmos_cli "${COSMOS_PROJECT_DIR}" script spawn \
    OFDEMO/procedures/verification_suite.py \
    --suite OrbitFabricVerificationSuite \
    --group OrbitFabricVerificationGroup \
    --script test_scenario \
    2>>"${EVIDENCE_DIR}/script-runner.stderr" \
    | tee "${EVIDENCE_DIR}/script-runner.stdout" \
    | tail -n 1
)"

if [[ ! "${SCRIPT_ID}" =~ ^[0-9]+$ ]]; then
  echo "Unexpected COSMOS Script Runner id: ${SCRIPT_ID}" >&2
  exit 1
fi

printf '%s\n' "${SCRIPT_ID}" >"${EVIDENCE_DIR}/script-id.txt"
log "spawned COSMOS Script Runner id ${SCRIPT_ID}"

terminal_state_seen=0
for _ in {1..20}; do
  cosmos_cli "${COSMOS_PROJECT_DIR}" script status "${SCRIPT_ID}" --verbose \
    >"${EVIDENCE_DIR}/script-status.txt" 2>&1 || true

  if grep -qE \
    '"state"[[:space:]]*=>[[:space:]]*"(completed|completed_errors|crashed|killed|stopped)"' \
    "${EVIDENCE_DIR}/script-status.txt"; then
    terminal_state_seen=1
    break
  fi

  sleep 2
done

if [[ "${terminal_state_seen}" != "1" ]]; then
  cat "${EVIDENCE_DIR}/script-status.txt" >&2 || true
  echo "COSMOS Script Runner did not reach a terminal persistent state" >&2
  exit 1
fi

if ! grep -qE \
  '"state"[[:space:]]*=>[[:space:]]*"completed"' \
  "${EVIDENCE_DIR}/script-status.txt"; then
  cat "${EVIDENCE_DIR}/script-status.txt" >&2
  echo "COSMOS Script Runner did not complete successfully" >&2
  exit 1
fi

REPORT_PATH="$(
  "${PYTHON}" - "${EVIDENCE_DIR}/script-status.txt" <<'PY_STATUS'
from pathlib import Path
import re
import sys

text = Path(sys.argv[1]).read_text(encoding="utf-8")
match = re.search(r'"report"\s*=>\s*"([^"]+)"', text)
if match:
    print(match.group(1))
PY_STATUS
)"

if [[ -z "${REPORT_PATH}" ]]; then
  cat "${EVIDENCE_DIR}/script-status.txt" >&2
  echo "Completed COSMOS Script Runner state has no persisted report" >&2
  exit 1
fi

printf '%s\n' "${REPORT_PATH}" >"${EVIDENCE_DIR}/script-report-path.txt"

log "converting persisted COSMOS Script Runner report to CTRF"
cosmos_report_to_ctrf "${REPORT_PATH}" \
  >"${EVIDENCE_DIR}/script-report-ctrf.stdout" \
  2>"${EVIDENCE_DIR}/script-report-ctrf.stderr"

"${PYTHON}" "${ROOT}/tools/validate_cosmos_ctrf.py" \
  --input "${EVIDENCE_DIR}/script-report-ctrf.stdout" \
  --output "${EVIDENCE_DIR}/ctrf.json" \
  >"${EVIDENCE_DIR}/ctrf-validation.log" 2>&1

if ! wait_for_log_event "${EVIDENCE_DIR}/simulator.jsonl" command_received 10; then
  echo "No STOP_ACQUISITION command reached the external OFDEMO simulator" >&2
  exit 1
fi
if ! wait_for_log_event "${EVIDENCE_DIR}/simulator.jsonl" telemetry_sent 10; then
  echo "No STATUS telemetry returned from the external OFDEMO simulator" >&2
  exit 1
fi

cat >"${EVIDENCE_DIR}/runtime-baseline.json" <<EOF
{
  "adapter_source_commit": "${ADAPTER_SOURCE_COMMIT}",
  "cosmos_project_commit": "${COSMOS_PROJECT_COMMIT}",
  "cosmos_version": "${COSMOS_BASELINE}",
  "plugin_version": "${PLUGIN_VERSION}",
  "simulator_host": "${SIMULATOR_HOST}",
  "suite": "OrbitFabricVerificationSuite",
  "group": "OrbitFabricVerificationGroup",
  "script": "test_scenario"
}
EOF

log "building canonical joined runtime evidence"
"${PYTHON}" "${ROOT}/tools/build_native_runtime_evidence.py" \
  --integration-result "${OUTPUT}/integration_result.json" \
  --plan "${PLAN}" \
  --procedure "${PROCEDURE}" \
  --suite "${SUITE}" \
  --ctrf "${EVIDENCE_DIR}/ctrf.json" \
  --simulator-log "${EVIDENCE_DIR}/simulator.jsonl" \
  --runtime-baseline "${EVIDENCE_DIR}/runtime-baseline.json" \
  --wheel "${WHEEL}" \
  --output "${EVIDENCE_DIR}/native-runtime-evidence.json" \
  >"${EVIDENCE_DIR}/evidence-build.log" 2>&1

cp "${OUTPUT}/integration_result.json" "${EVIDENCE_DIR}/integration-result.json"
cp "${PLAN}" "${EVIDENCE_DIR}/verification-projection-plan.json"
cp "${PROCEDURE}" "${EVIDENCE_DIR}/verification.py"
cp "${SUITE}" "${EVIDENCE_DIR}/verification_suite.py"
cp "${SCENARIO}" "${EVIDENCE_DIR}/scenario.yaml"
cp "${PROFILE}" "${EVIDENCE_DIR}/profile.yaml"
sha256sum \
  "${WHEEL}" \
  "${EVIDENCE_DIR}/integration-result.json" \
  "${EVIDENCE_DIR}/verification-projection-plan.json" \
  "${EVIDENCE_DIR}/verification.py" \
  "${EVIDENCE_DIR}/verification_suite.py" \
  "${EVIDENCE_DIR}/ctrf.json" \
  "${EVIDENCE_DIR}/native-runtime-evidence.json" \
  >"${EVIDENCE_DIR}/SHA256SUMS"

log "canonical native COSMOS acceptance PASS"
log "adapter commit: ${ADAPTER_SOURCE_COMMIT}"
log "evidence: ${EVIDENCE_DIR}"
