# OrbitFabric OpenC3 COSMOS Adapter

Canonical OrbitFabric adapter for projecting selected mission verification intent toward [OpenC3 COSMOS](https://github.com/OpenC3/cosmos).

OrbitFabric and OpenC3 COSMOS remain independent systems. OrbitFabric Core owns generic mission and integration contracts, this adapter owns COSMOS-specific projection, and COSMOS owns downstream execution semantics and runtime behavior.

> **Product status:** `0.1.0.dev0` is the active productization baseline. Canonical native COSMOS acceptance has passed on exact adapter commit `44915686358da7334540d4fa1aca9e204d8a4ac9` against OpenC3 COSMOS `v7.3.0`. Stable release publication and post-publication greenfield acceptance are separate lifecycle gates and are not yet claimed.

## Choose your path

### I want to use the adapter

The intended normal consumer lifecycle is through **OrbitFabric Adapter Manager** once a stable release is published.

```text
OrbitFabric Core
    -> published adapter release
    -> Adapter Manager install
    -> verify
    -> execute verification_projection
    -> COSMOS-native artifacts
```

A normal consumer should not need an editable source install, direct repository tooling or publisher release construction.

For the current development baseline, start with **[Getting Started](docs/getting-started.md)** and **[Projection Profile and Bindings](docs/projection-profile-and-bindings.md)**.

### I want to try the adapter

The current product focuses on one coherent operation:

```text
OrbitFabric Scenario
    + Core Integration Input Set
    + OpenC3 COSMOS Projection Profile
        -> verification_projection
        -> resolved verification plan
        -> native COSMOS Python procedure / suite
        -> Core-conformant Integration Result
```

The repository includes a reference Profile at [`examples/profile.yaml`](examples/profile.yaml).

The generated COSMOS procedure and suite can also be exercised through the canonical native runtime acceptance path described in **[Native OpenC3 COSMOS Acceptance](docs/native-cosmos-acceptance.md)**.

### I want to develop or contribute

Clone the repository and use the development environment:

```bash
git clone https://github.com/FAROTECH/orbitfabric-openc3-cosmos-adapter.git
cd orbitfabric-openc3-cosmos-adapter

python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"

ruff check .
python tools/check_adapter_consistency.py
pytest -q
```

The direct adapter console command:

```text
orbitfabric-openc3-cosmos
```

is primarily a contributor and development surface. See **[Architecture and Ownership](docs/architecture-and-ownership.md)**, **[Integration Contracts](docs/integration-contracts.md)**, **[Testing and Conformance](docs/testing-and-conformance.md)** and [CONTRIBUTING.md](CONTRIBUTING.md).

### I maintain or publish the adapter

Release construction is a separate maintainer and publisher responsibility:

```text
accepted source commit
    -> exact version tag
    -> wheel
    -> adapter-release.json
    -> SHA256SUMS
    -> local proof
    -> immutable publication
    -> published-asset verification
    -> external greenfield acceptance
```

A normal consumer must not need to perform these steps.

See **[Release Lifecycle](docs/release-lifecycle.md)** and **[Evidence and Traceability](docs/evidence-and-traceability.md)**.

## What the adapter does

The current product baseline:

- consumes a coherent OrbitFabric Core Integration Input Set;
- validates an OpenC3 COSMOS-specific Projection Profile;
- consumes one required file-backed `scenario` operation input;
- validates Scenario semantics through OrbitFabric Core;
- preserves Scenario atom accounting, ordering and provenance;
- maps supported no-argument Scenario command intent to native COSMOS `cmd()` calls;
- maps supported telemetry expectations to native COSMOS `wait_check()` calls;
- materializes a native COSMOS Python procedure and Suite;
- emits a Core-conformant Integration Result with provenance and coverage;
- fails explicitly when a requested semantic mapping is unsupported or outside the declared contract.

The adapter deliberately does **not** declare a generic mission-data `project` operation merely for symmetry with other adapters. Broader Ground integration surfaces should be added only when target-owned semantics and evidence justify them.

## Integration boundary

```text
OrbitFabric Mission Model
        |
        v
OrbitFabric Core
Integration Input Set
        |
        + OrbitFabric Scenario
        + COSMOS Projection Profile
        |
        v
OpenC3 COSMOS Adapter
        |
        v
Verification Projection Plan
        |
        v
COSMOS Python procedure / suite
        |
        v
OpenC3 COSMOS
        |
        v
native runtime evidence
```

The ownership rule is simple:

```text
OrbitFabric owns intent and generic contract.
The adapter owns projection.
OpenC3 COSMOS owns downstream execution semantics.
Evidence retains provenance across the boundary.
```

## Consumer execution model

The canonical operation is:

```text
verification_projection
    required operation input: scenario
```

Current direct development execution:

```bash
orbitfabric-openc3-cosmos run \
  --operation verification_projection \
  --input-set-manifest <core-input>/integration_input_manifest.json \
  --profile examples/profile.yaml \
  --operation-input scenario <scenario.yaml> \
  --output-dir /tmp/orbitfabric-cosmos
```

Representative outputs:

```text
verification_projection/verification_projection_plan.json
verification_projection/cosmos/verification.py
verification_projection/cosmos/verification_suite.py
integration_result.json
```

The generated COSMOS files are downstream artifacts. The Integration Result remains the primary OrbitFabric execution evidence surface.

## Integration Coverage

Integration Coverage answers a simple product question:

> **How much of the analyzed OrbitFabric semantic surface is currently mapped toward OpenC3 COSMOS, and with what semantic disposition?**

It is not a count of COSMOS features and it is not an OrbitFabric Core conformance score.

The coverage model separates:

```text
OrbitFabric Semantic Surface
        -> Target Applicable Surface
        -> Adapter Declared Scope
```

Current `0.1.0.dev0` summary:

```text
Analyzed semantic areas:              21 / 21
Analysis Coverage:                    100%

Target-applicable areas:              19
NOT_APPLICABLE:                        2

Declared initial scope:                6
  FULL:                                4
  PARTIAL:                             1
  TARGET_UNSUPPORTED:                  1
  NOT_IMPLEMENTED:                     0

Applicable but OUT_OF_SCOPE:          13
```

The current declared scope therefore contains **no known `NOT_IMPLEMENTED` hole**. The product is deliberately narrow rather than accidentally incomplete.

### Coverage matrix

| OrbitFabric capability | OpenC3 COSMOS mapping or target surface | Status | Current interpretation |
| --- | --- | --- | --- |
| Mission identity and Core input provenance | Integration Result plus Verification Projection Plan provenance | `FULL` | Mission identity, Core input identity and digests are validated and retained |
| Telemetry definition / parameter projection | COSMOS target `cmd_tlm` telemetry definitions | `OUT_OF_SCOPE` | Existing telemetry identity is consumed for Scenario bindings; dictionaries are not generated |
| Command definition projection | COSMOS command definitions under target `cmd_tlm` | `OUT_OF_SCOPE` | Existing COSMOS commands are bound through the Profile; command dictionaries are not generated |
| Event / log definition projection | COSMOS logs, events or observable telemetry conventions | `OUT_OF_SCOPE` | No generic OrbitFabric event-to-COSMOS observation contract is claimed |
| Packet / target definition projection | COSMOS target/plugin packet and target configuration | `OUT_OF_SCOPE` | Target identity is referenced, but target/plugin configuration is not a product projection surface |
| Spacecraft and subsystem topology | COSMOS targets, plugins and operational grouping | `OUT_OF_SCOPE` | OrbitFabric subsystem topology is not projected into COSMOS structure |
| Scenario initial mode state | Target initialization or observable mode state | `OUT_OF_SCOPE` | Retained as not projected; no initialization behavior is inferred |
| Scenario initial telemetry state | Simulator/target initialization or injected telemetry | `OUT_OF_SCOPE` | Retained as not projected; no target initialization contract is inferred |
| Fault / FDIR runtime behavior | COSMOS monitoring, limits, procedures, events and downstream behavior | `OUT_OF_SCOPE` | Generating FDIR or operations behavior exceeds the current projection boundary |
| Mission policies / operations sequencing | COSMOS scripts, procedures and suites | `OUT_OF_SCOPE` | Current sequencing is Scenario verification projection, not a generic operations policy engine |
| Relationship Manifest as a direct projection surface | No independent COSMOS relationship-graph artifact | `NOT_APPLICABLE` | Relationship Manifest remains a Core coherence surface rather than a target artifact |
| Scenario validation and provenance | Core `ScenarioLoader` plus Verification Projection Plan provenance | `FULL` | Scenario semantics are Core-validated and source identity is retained |
| Scenario step ordering and `t` semantics | Generated Python statement order plus `scenario_t` provenance | `PARTIAL` | Order and `t` are preserved, but `t` is not converted into real waits or wall-clock scheduling |
| Scenario command action without arguments | Native COSMOS `cmd()` | `FULL` | Profile-resolved command mapping is implemented and native runtime accepted |
| Scenario command arguments | COSMOS command argument encoding | `OUT_OF_SCOPE` | Commands with arguments fail closed until an explicit target encoder exists |
| Scenario telemetry expectation | Native COSMOS `wait_check()` | `FULL` | Profile-resolved telemetry binding, encoding and timeout are implemented and native runtime accepted |
| Scenario telemetry injection | Target or simulator-specific injection mechanisms | `OUT_OF_SCOPE` | OrbitFabric telemetry mutation is not assumed equivalent to COSMOS injection |
| Scenario event expectation | COSMOS log/event/telemetry observation | `OUT_OF_SCOPE` | No event observability binding is currently defined |
| Scenario mode expectation | COSMOS telemetry/state observation | `OUT_OF_SCOPE` | No target mode observation binding is currently defined |
| Core host-side command dispatch / `command_status` expectations | COSMOS invocation, history or downstream acknowledgement | `TARGET_UNSUPPORTED` | These surfaces are not considered semantically equivalent to Core host command evidence |
| Aggregate host expectations (`data_flow`, `payload_lifecycle`, `scenario_status`) | No primitive COSMOS runtime equivalent | `NOT_APPLICABLE` | These remain OrbitFabric host-side aggregate evidence semantics |

### Status legend

| Status | Meaning |
| --- | --- |
| `FULL` | Mapped with the intended semantics and evidence for the declared scope |
| `PARTIAL` | Valid mapping exists, with an explicit semantic limitation |
| `NOT_IMPLEMENTED` | Applicable and declared in scope, but implementation is missing |
| `TARGET_UNSUPPORTED` | Analysis found no adequate downstream semantic equivalent for the claimed meaning |
| `OUT_OF_SCOPE` | A meaningful target mapping could exist, but the current adapter deliberately does not promise it |
| `NOT_APPLICABLE` | The semantic area is not meaningful as a target projection for this adapter role |
| `NOT_ANALYZED` | The semantic disposition has not yet been analyzed |

The detailed maintainer declaration, rationale and roadmap for every row remain in [`coverage/integration-coverage.md`](coverage/integration-coverage.md). See also **[Integration Coverage](docs/integration-coverage.md)** for the coverage model and interpretation rules.

## Validated compatibility baselines

| System | Validated baseline |
| --- | --- |
| OrbitFabric Core | `4377d6656c62aa1dc19a7ed81d2de872b6b22ccd` |
| OpenC3 COSMOS | `v7.3.0` |
| `cosmos-project` | `9eb454f06fe0113d05aa6945d88b627155a2aa47` |

Changing a pinned downstream baseline is an evidence change, not a documentation-only change.

## Native validation model

The canonical source baseline is accepted through independent evidence layers:

```text
Core contract conformance
        +
adapter-owned tests
        +
OpenC3 COSMOS source/API compatibility
        +
installed Adapter Manager lifecycle
        +
release proof
        +
native COSMOS runtime acceptance
```

The canonical native harness:

```text
tools/run_native_cosmos_acceptance.sh
```

builds the adapter wheel, generates the exact canonical projection, starts pinned COSMOS `v7.3.0`, loads the `OFDEMO` fixture plugin, executes the generated Suite through native Script Runner, retrieves the persisted native report, converts it with OpenC3's CTRF implementation and joins runtime provenance into adapter-owned evidence.

Accepted local native evidence on commit `44915686358da7334540d4fa1aca9e204d8a4ac9` proved:

```text
STOP_ACQUISITION command received by the external target
STATUS telemetry returned with acquisition_active=false
COSMOS Script Runner state completed
CTRF tests 1 / passed 1 / failed 0
joined native-runtime-evidence status passed
```

The full runtime harness is intentionally not claimed as a mandatory GitHub-hosted CI job while its external host/container topology remains environment-dependent.

## Product identity

```text
repository       orbitfabric-openc3-cosmos-adapter
distribution     orbitfabric-openc3-cosmos-adapter
python package   orbitfabric_openc3_cosmos_adapter
console command  orbitfabric-openc3-cosmos
adapter.id       orbitfabric-openc3-cosmos
integration.id   orbitfabric-openc3-cosmos
version          0.1.0.dev0
```

## Repository structure

```text
src/
    adapter implementation and packaged resources

examples/
    reference product-facing configuration

acceptance/
    native COSMOS acceptance fixtures

coverage/
    detailed Integration Coverage declaration

tests/
    adapter, contract and acceptance regression controls

docs/
    user, developer, evidence and release documentation

tools/
    consistency, lifecycle and native acceptance tooling

.github/
    CI, target compatibility and lifecycle controls
```

## Documentation

The documentation is organized by role and purpose.

### User

- [Getting Started](docs/getting-started.md)
- [Projection Profile and Bindings](docs/projection-profile-and-bindings.md)
- [Runtime Dependencies](docs/runtime-dependencies.md)
- [Integration Coverage](docs/integration-coverage.md)

### Developer / Contributor

- [Architecture and Ownership](docs/architecture-and-ownership.md)
- [Integration Contracts](docs/integration-contracts.md)
- [Testing and Conformance](docs/testing-and-conformance.md)
- [Native OpenC3 COSMOS Acceptance](docs/native-cosmos-acceptance.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)

### Maintainer / Publisher

- [Release Lifecycle](docs/release-lifecycle.md)
- [Evidence and Traceability](docs/evidence-and-traceability.md)
- [Adapter Identity](docs/adapter-identity.md)

Documentation is built with MkDocs and validated with `mkdocs build --strict` in CI.

## Historical PoC

The preceding `FAROTECH/OrbitFabric-OpenC3-COSMOS-PoC` remains historical engineering evidence and a regression reference.

PoC experiment numbering and temporary investigation scaffolding are intentionally not product architecture. Durable projection behavior, target compatibility facts and evidence requirements are retained in this canonical repository.

## Project relationships

OpenC3 COSMOS is an independent upstream project. This adapter integrates with its native interfaces without transferring ownership of COSMOS execution semantics to OrbitFabric.

The repository follows the cross-adapter productization shape recorded in the non-normative OrbitFabric Architecture Lab Adapter Product Model and pressure-tested first by the OpenOBSW/OpenSVF adapter.

## License

Apache-2.0.
