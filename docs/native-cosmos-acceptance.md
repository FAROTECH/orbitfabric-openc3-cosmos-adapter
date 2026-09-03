# Native OpenC3 COSMOS Acceptance

The canonical adapter includes a reproducible native runtime acceptance harness for the Scenario verification lane.

This control is deliberately separate from mandatory hosted CI.

## What it proves

The harness exercises this exact chain:

```text
clean canonical adapter checkout
    -> build wheel
    -> install wheel in isolated virtual environment
    -> exact OrbitFabric Core fixture baseline
    -> Core Integration Input Set
    -> canonical verification_projection
    -> generated COSMOS procedure / suite
    -> native COSMOS plugin build / validation / load
    -> external OFDEMO simulator
    -> real TCP command transport
    -> real telemetry transport and decommutation
    -> native Script Runner
    -> CTRF one-test PASS
    -> adapter-owned joined runtime evidence
```

The generated COSMOS procedure and suite come from the adapter execution under test. The harness does not keep a hand-authored duplicate procedure that could drift away from product behavior.

## Fixture boundary

`OFDEMO` is an acceptance fixture, not adapter product identity.

```text
adapter.id       orbitfabric-openc3-cosmos
integration.id   orbitfabric-openc3-cosmos
fixture target   OFDEMO
```

The fixture implements only the target behavior required by the canonical smoke Scenario:

```text
STOP_ACQUISITION command
    -> external simulator sets acquisition_active = false
    -> STATUS.ACQUISITION_ACTIVE telemetry = 0
```

This does not add a new OrbitFabric semantic capability and does not widen Integration Coverage.

## Pinned baselines

```text
OrbitFabric Core
4377d6656c62aa1dc19a7ed81d2de872b6b22ccd

OpenC3 COSMOS
v7.3.0

cosmos-project runtime baseline
9eb454f06fe0113d05aa6945d88b627155a2aa47
```

The runtime baseline is inherited from the native acceptance already proven by the historical COSMOS PoC. The canonical harness replaces PoC identity and artifacts with the product adapter, `OFDEMO`, and the canonical generated verification assets.

## Prerequisites

The acceptance host must provide:

```text
git
python with venv support
Docker
Docker Compose v2
curl
network access for Python dependencies and pinned GitHub repositories
```

Port `2900` must be free before the isolated COSMOS runtime starts.

The default topology expects COSMOS containers to reach the host simulator as:

```text
host.docker.internal
```

That topology is known to work with the historical WSL + Docker Desktop acceptance environment. Other Docker environments can override it:

```bash
COSMOS_SIMULATOR_HOST=<host-visible-from-containers> \
  bash tools/run_native_cosmos_acceptance.sh
```

The override changes target transport location only. It does not change adapter semantics or evidence identity.

## Run

Use a clean checkout of the exact commit to be accepted:

```bash
bash tools/run_native_cosmos_acceptance.sh
```

The harness refuses a dirty checkout by default so the resulting evidence can name one exact source commit. `ALLOW_DIRTY_ACCEPTANCE=1` exists only for local debugging and should not be used for release evidence.

## Output

Generated work and evidence remain under the ignored `generated/` tree by default:

```text
generated/native-cosmos-acceptance/evidence/
    adapter-projection.log
    core-input.log
    ctrf.json
    evidence-build.log
    integration-result.json
    native-runtime-evidence.json
    profile.yaml
    runtime-baseline.json
    scenario.yaml
    script-runner.stdout
    script-runner.stderr
    simulator.jsonl
    verification-projection-plan.json
    verification.py
    verification_suite.py
    SHA256SUMS
    ... build / plugin / COSMOS logs
```

`native-runtime-evidence.json` joins:

```text
exact adapter source commit and wheel digest
Scenario identity and digest
Core input-set identity and digest
Projection Profile identity and digest
Verification Projection Plan digest and operation provenance
Integration Result digest
generated procedure / suite digests
exact COSMOS runtime baseline
CTRF summary and digest
external target command / telemetry events
simulator log digest
```

The evidence kind is adapter-owned:

```text
orbitfabric.openc3_cosmos.native_runtime_evidence
0.1-candidate
```

It is not a generic OrbitFabric Core contract.

## PASS criteria

A native acceptance PASS requires all of the following in one run:

```text
canonical adapter wheel builds and installs
Core Integration Input Set exports successfully
verification_projection succeeds and Result conforms
COSMOS plugin builds and validates
COSMOS connects command and telemetry interfaces to OFDEMO
STOP_ACQUISITION reaches the external simulator
inactive STATUS telemetry returns to COSMOS
generated Script Runner suite produces exactly one CTRF PASS
joined runtime evidence validates and is written
```

## Why this is not mandatory hosted CI

The historical PoC showed that the full runtime path can pass locally while GitHub-hosted Ubuntu cannot reproduce the same host/container connection through `host.docker.internal`.

The repository therefore keeps two distinct controls:

```text
mandatory hosted CI
    exact COSMOS v7.3.0 source/API compatibility
    generated Python syntax
    Core conformance
    installed lifecycle
    release proof

native acceptance harness
    real target runtime execution and CTRF evidence
    run in a topology that can actually support the external simulator path
```

A hosted CI environment may be added later if it can provide equivalent native topology without weakening or mocking the acceptance meaning.
