# OpenC3 COSMOS Adapter Integration Coverage

Status: maintainer coverage declaration for the canonical `0.1.0.dev0` productization baseline.

This matrix describes the OrbitFabric semantic surface assessed against the OpenC3 COSMOS integration role, the subset deliberately claimed by this adapter, and the current implementation disposition.

It is not an OrbitFabric Core conformance contract and it does not measure the number of OpenC3 COSMOS features supported by the adapter.

The user-facing form of this matrix is also exposed directly in the repository `README.md`. This file retains the detailed rationale and roadmap.

## Adapter intent

```text
Target:
  OpenC3 COSMOS Ground System verification / operations tooling

Adapter purpose:
  project selected OrbitFabric Scenario verification intent
  into target-owned COSMOS Python procedure / suite artifacts
  without making OrbitFabric Core a Ground runtime or test framework

Declared initial scope:
  coherent Core Integration Input Set consumption and provenance
  Core-native Scenario validation
  Scenario atom accounting and traceability
  Scenario ordering / t provenance without implicit real-time scheduling
  no-argument Scenario command -> COSMOS cmd() projection
  Scenario telemetry expectation -> COSMOS wait_check() projection
  explicit refusal of non-equivalent Core host command evidence semantics
```

The initial product deliberately does **not** declare a generic mission-data `project` operation. A complete COSMOS feature mapping is therefore not the denominator.

The denominator is the OrbitFabric semantic surface applicable to the Ground integration role represented by this adapter.

## Coverage model

```text
OrbitFabric Semantic Surface
        ↓
Target Applicable Surface
        ↓
Adapter Declared Scope
```

The matrix separates three different questions:

```text
Does an OrbitFabric semantic area make sense for this target role?

If yes, does the current adapter explicitly claim it?

If claimed, how completely is that claim implemented and evidenced?
```

`OUT_OF_SCOPE` is not a defect. It means a meaningful target mapping could exist, but the initial product deliberately does not promise it.

## Matrix

| OrbitFabric capability area | Target applicable | Target representation or constraint | Adapter declared scope | Disposition | Evidence or rationale | Roadmap |
| --- | --- | --- | --- | --- | --- | --- |
| Mission identity and Core input provenance | yes | Integration Result plus Verification Projection Plan provenance | in scope | FULL | Mission id/model version, Core runtime version, `input_set_sha256`, required surface kind/version, portable paths and per-surface digests are checked before projection; Scenario/Profile digests are retained | complete for current Core contract |
| Telemetry definition / parameter projection | yes | COSMOS target `cmd_tlm` telemetry definitions | out of scope | OUT_OF_SCOPE | Current product consumes telemetry identity only when resolving Scenario expectations; it does not generate COSMOS telemetry dictionaries | consider only with a future evidence-backed `project` operation |
| Command definition projection | yes | COSMOS command definitions under target `cmd_tlm` | out of scope | OUT_OF_SCOPE | Current Profile binds an existing COSMOS command name; it does not generate command dictionaries | require separate command-contract design before widening scope |
| Event / log definition projection | yes | COSMOS logs, events or observable telemetry conventions | out of scope | OUT_OF_SCOPE | No generic OrbitFabric event -> COSMOS observation contract is claimed | define target-owned event observability first |
| Packet / target definition projection | yes | COSMOS target/plugin packet and target configuration | out of scope | OUT_OF_SCOPE | The adapter references a Profile target name but does not generate target/plugin configuration as a product contract | evaluate only with a broader Ground project lane |
| Spacecraft and subsystem topology | yes | COSMOS targets, plugins and operational grouping | out of scope | OUT_OF_SCOPE | OrbitFabric subsystem topology is not projected into COSMOS target/plugin structure | separate design investigation before widening scope |
| Scenario initial mode state | yes | target initialization or observable mode state | out of scope | OUT_OF_SCOPE | Initial mode is retained as `not_projected`; the adapter does not infer COSMOS initialization behavior | define explicit target initialization/observation semantics first |
| Scenario initial telemetry state | yes | simulator/target initialization or injected target telemetry | out of scope | OUT_OF_SCOPE | Initial telemetry is retained as `not_projected`; no target initialization contract is inferred | define explicit initialization mapping before adding scope |
| Fault / FDIR runtime behavior | yes | target monitoring, limits, procedures, events and downstream system behavior | out of scope | OUT_OF_SCOPE | Generating FDIR or operations behavior would exceed the current projection ownership boundary | require concrete downstream FDIR/operations contract before considering |
| Mission policies / operations sequencing | yes | COSMOS scripts, procedures and suites can implement operational policy | out of scope | OUT_OF_SCOPE | Current generated sequence is Scenario verification projection, not a generic mission-operations policy engine | investigate separately if a Ground operations lane is required |
| Relationship Manifest as a direct projection surface | no | no independent COSMOS relationship-graph artifact is owned by this adapter | out of scope | NOT_APPLICABLE | Relationship Manifest remains a required Core coherence surface; the current adapter does not manufacture a second target relationship graph | reassess only if a downstream-native relationship representation becomes part of scope |
| Scenario validation and provenance | yes | exact Core `ScenarioLoader` validation plus Verification Projection Plan provenance | in scope | FULL | Scenario semantics are validated by Core; mission identity/model version are cross-checked with the consumed Integration Input Set; Scenario digest is retained in plan and Result | complete for current operation contract |
| Scenario step ordering and `t` semantics | yes | generated Python statement order plus plan `scenario_t` provenance | in scope | PARTIAL | Source order and each `t` value are preserved for provenance, but `t` is deliberately **not** converted into real waits, scheduling or wall-clock behavior without explicit target policy | retain distinction; add timing only through reviewed target-owned policy |
| Scenario command action without arguments | yes | COSMOS `cmd()` with Profile-resolved target/command naming | in scope | FULL | Canonical projection generates `cmd(...)`; native acceptance on adapter commit `44915686358da7334540d4fa1aca9e204d8a4ac9` proved real `STOP_ACQUISITION` transport through COSMOS to the external OFDEMO target | complete for current declared scope; retain regression evidence |
| Scenario command arguments | yes | COSMOS command argument encoding | out of scope | OUT_OF_SCOPE | The projector blocks commands with arguments instead of inventing target encoding | define explicit target argument encoder before adding to declared scope |
| Scenario telemetry expectation | yes | COSMOS `wait_check()` with Profile-resolved packet/item, encoding and timeout | in scope | FULL | Canonical projection materializes `wait_check(...)`; `boolean_01` and scalar identity encoding are explicit; native acceptance on commit `44915686358da7334540d4fa1aca9e204d8a4ac9` proved real STATUS telemetry return with `acquisition_active=false` and CTRF PASS | complete for current declared scope; retain regression evidence |
| Scenario telemetry injection | yes | target/simulator-specific write or injection mechanisms | out of scope | OUT_OF_SCOPE | OrbitFabric telemetry mutation is not assumed equivalent to a COSMOS simulator/target input without an explicit mapping | design target injection contract before adding scope |
| Scenario event expectation | yes | target log/event/telemetry observation | out of scope | OUT_OF_SCOPE | Current operation records event expectation as `not_projected`; no event observability binding is defined | design event observation mapping before adding scope |
| Scenario mode expectation | yes | target telemetry/state observation | out of scope | OUT_OF_SCOPE | Current operation records mode expectation as `not_projected`; no target mode observation mapping is defined | design mode observation mapping before adding scope |
| Core host-side command dispatch / `command_status` expectations | yes | COSMOS command invocation/history or downstream acknowledgement can be related, but is not semantically identical | in scope | TARGET_UNSUPPORTED | Adapter explicitly preserves these as non-projected host-evidence semantics rather than claiming that COSMOS command invocation or protocol acknowledgement proves Core host command state | retain semantic distinction unless a future portable observation contract defines equivalence |
| Aggregate host expectations (`data_flow`, `payload_lifecycle`, `scenario_status`) | no | these are OrbitFabric host-side aggregate evidence semantics, not primitive COSMOS runtime facts | out of scope | NOT_APPLICABLE | Verification plan retains their disposition instead of manufacturing downstream evidence | none unless Core defines a portable observation contract |

## Current evidence

### Core and adapter contract evidence

The canonical adapter CI proves on Python 3.11 and 3.12:

```text
exact Core baseline installation
Ruff
adapter identity / product-hygiene consistency
Core Integration Package conformance
Core Integration Input Set integrity and compatibility
projection / negative regression tests
wheel build and packaged asset ownership
MkDocs strict build
```

The Core input control includes:

```text
RFC 8785/JCS input_set_sha256 recomputation
required role / availability / kind / format_version checks
portable relative-path containment
per-surface SHA-256 verification
mission identity consistency
negative tamper / incompatible-surface tests
```

### Canonical OpenC3 COSMOS compatibility evidence

The `target-compatibility-cosmos` job pins:

```text
OpenC3 COSMOS v7.3.0
```

and proves:

```text
Core Integration Input Set generation
canonical verification_projection execution
Core-conformant Integration Result
Verification Projection Plan generation
generated Python procedure / suite syntax compilation
presence of exact-baseline COSMOS cmd(), wait_check(), Group and Suite APIs
generated imports against the validated target source baseline
```

This hosted CI control is intentionally a target source/API compatibility gate. It does **not** claim live TCP command/telemetry execution or CTRF acceptance.

### Canonical native COSMOS acceptance harness

The product repository owns a reproducible native runtime harness:

```text
tools/run_native_cosmos_acceptance.sh
```

It proves, in one clean exact source commit:

```text
canonical wheel build and isolated installation
canonical Core Input Set + Scenario projection
use of the exact generated verification.py / verification_suite.py artifacts
native COSMOS plugin generation / build / validation / load
external OFDEMO command and telemetry TCP path
persistent Script Runner execution status
persisted native Script Runner report
OpenC3-native CTRF conversion
one-test CTRF PASS
adapter-owned joined runtime evidence
```

The harness itself is covered by normal CI for shell syntax, fixture identity, fail-closed CTRF parsing, persistent Script Runner evidence behavior and joined-evidence construction.

**Runtime status:** PASS on exact adapter source commit `44915686358da7334540d4fa1aca9e204d8a4ac9`.

Validated downstream baseline:

```text
OpenC3 COSMOS  v7.3.0
cosmos-project 9eb454f06fe0113d05aa6945d88b627155a2aa47
```

Observed native evidence in the accepted run:

```text
STOP_ACQUISITION command received by external OFDEMO
STATUS telemetry returned with acquisition_active=false
COSMOS Script Runner state completed
persisted native Script Runner report
CTRF tests 1
CTRF passed 1
CTRF failed 0
native-runtime-evidence status passed
```

The full runtime is intentionally not added to mandatory GitHub-hosted CI while the required host/container topology remains environment-dependent.

### Historical native COSMOS runtime evidence

The historical `FAROTECH/OrbitFabric-OpenC3-COSMOS-PoC` remains engineering evidence and regression reference.

Its accepted local native COSMOS `v7.3.0` Experiment 001 previously proved:

```text
COSMOS plugin and target generation
plugin build / validation / load
real TCP command transport to an external simulator
real telemetry transport back to COSMOS
native telemetry decommutation
native Script Runner verification
machine-readable CTRF PASS evidence
joined provenance back to Scenario, Core inputs, Profile and projected operations
```

This historical evidence remains useful for regression comparison, but canonical runtime claims are now supported by product-owned evidence rather than inherited from the PoC.

### Adapter Manager lifecycle and release evidence

The canonical installed-lifecycle and provider-neutral release-proof jobs establish:

```text
wheel installation through Adapter Manager
inventory and verify
source-tree removal before installed execution
verification_projection through the installed execution binding
Integration Result conformance
generated plan / procedure / suite artifact presence
remove -> empty inventory
Project Lock MISSING -> install -> MATCH
second install -> NOOP / MATCH
publisher-owned release material construction
```

## Summary

```text
Total rows:                         21
Analyzed rows:                      21
NOT_ANALYZED:                        0
Analysis Coverage:                 100%

Known target-applicable rows:       19
Target applicability unknown:        0
NOT_APPLICABLE:                      2

Declared initial scope:              6
FULL:                                4
PARTIAL:                             1
TARGET_UNSUPPORTED:                  1
NOT_IMPLEMENTED in declared scope:   0

Known applicable but OUT_OF_SCOPE:  13
```

Interpretation:

```text
Analysis Coverage
    complete for the current 21-area semantic inventory.

Scope Completeness
    there is no known NOT_IMPLEMENTED hole inside the declared initial scope.
    Scenario t/order is PARTIAL because ordering and provenance are preserved
    while real-time scheduling is intentionally not claimed.
    Core command host-evidence semantics remain an explicit non-equivalence.

Applicable Surface Coverage
    deliberately narrow.
    The current product is a focused Scenario verification adapter,
    not a generic OrbitFabric-to-COSMOS mission-data or operations generator.
```

No single maturity percentage is reported because it would hide the distinction between deliberate scope, partial semantic mapping and true target-semantic non-equivalence.

## Initial release-scope decision

The initial `0.1.x` line should **not** add a generic `project` operation merely to reduce `OUT_OF_SCOPE` rows.

The product currently proves a coherent integration chain:

```text
OrbitFabric Core Integration Input Set
    + OrbitFabric Scenario
    + OpenC3 COSMOS Projection Profile
        -> validated semantic atom accounting
        -> no-argument COSMOS command projection
        -> COSMOS telemetry expectation projection
        -> native Python procedure / suite artifacts
        -> Core-conformant Integration Result
        -> native COSMOS runtime acceptance
```

Later versions may widen one semantic family at a time. Each addition should first define the target-owned meaning, then add implementation, negative behavior and target-native evidence.

## Release-readiness implication

Integration Coverage itself is complete for this baseline. The architecture and target-evidence decisions exposed by the matrix have both been resolved on the current candidate commit: the canonical repository carries the native runtime acceptance path and that path has produced a clean PASS.

Before the first release freeze, native acceptance must be repeated against the exact accepted source commit after merge so that retained evidence is tied to the source that will actually be published.

That final provenance step must not be confused with a semantic coverage gap and is not a reason to widen OrbitFabric scope.

## Policy note

This matrix is maintained as a product maturity and transparency input. Integration Coverage is not a generic Core conformance requirement.
