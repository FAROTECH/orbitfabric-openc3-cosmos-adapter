# Integration Coverage

Integration Coverage describes which OrbitFabric semantics are applicable to the OpenC3 COSMOS Ground integration role, which subset this adapter deliberately claims, and the disposition of each analyzed area.

It is not a count of OpenC3 COSMOS product features and it is not a generic OrbitFabric Core conformance contract.

The complete user-facing matrix is visible directly in the repository [README](../README.md). The detailed maintainer declaration, rationale and roadmap are stored at:

```text
coverage/integration-coverage.md
```

## Coverage model

```text
OrbitFabric Semantic Surface
        -> Target Applicable Surface
        -> Adapter Declared Scope
```

### OrbitFabric Semantic Surface

The semantics available through the current OrbitFabric contracts and integration surfaces. Core remains authoritative for their meaning.

### Target Applicable Surface

The subset that makes architectural sense for an OpenC3 COSMOS Ground integration.

A semantic area can be valid OrbitFabric meaning and target-applicable while still being deliberately outside the current adapter product.

### Adapter Declared Scope

The subset the current product explicitly promises to implement.

This keeps two questions separate:

```text
Scope Completeness
    how completely does the adapter implement what it promises?

Applicable Surface Coverage
    how broadly does the release cover the semantics that could make sense for COSMOS?
```

## Dispositions

The matrix uses:

```text
FULL
PARTIAL
NOT_IMPLEMENTED
TARGET_UNSUPPORTED
OUT_OF_SCOPE
NOT_APPLICABLE
NOT_ANALYZED
```

`OUT_OF_SCOPE` means a meaningful COSMOS mapping could exist, but the current adapter deliberately does not claim it.

`TARGET_UNSUPPORTED` is reserved for a semantic mismatch demonstrated by analysis rather than unfinished implementation.

## Current `0.1.0.dev0` summary

```text
Total rows:                         21
Analyzed rows:                      21
NOT_ANALYZED:                        0
Analysis Coverage:                 100%

Known target-applicable rows:       19
NOT_APPLICABLE:                      2

Declared initial scope:              6
FULL:                                4
PARTIAL:                             1
TARGET_UNSUPPORTED:                  1
NOT_IMPLEMENTED in declared scope:   0

Known applicable but OUT_OF_SCOPE:  13
```

The current declared scope therefore has **no known `NOT_IMPLEMENTED` hole**.

The single `PARTIAL` area is Scenario step ordering / `t` semantics. Source order and `t` provenance are preserved, but the adapter deliberately does not convert Scenario time into real waits or scheduling without an explicit target-owned policy.

The `TARGET_UNSUPPORTED` area preserves a deliberate semantic distinction between OrbitFabric host-side command dispatch/status evidence and COSMOS command invocation or downstream acknowledgement. The adapter refuses to manufacture an equivalence that has not been defined.

## Initial product breadth

The current product is intentionally a Scenario verification adapter:

```text
Core Integration Input Set
    + OrbitFabric Scenario
    + OpenC3 COSMOS Projection Profile
        -> no-argument COSMOS cmd() projection
        -> telemetry wait_check() projection
        -> Python procedure / suite artifacts
        -> Core-conformant Integration Result
```

It does **not** declare a generic mission-data `project` operation merely for symmetry with another adapter.

Target-applicable areas such as command/telemetry dictionary generation, target/plugin generation, subsystem topology, mode initialization, FDIR behavior, mission policy, command argument encoding, telemetry injection, event expectation and mode expectation remain visible as `OUT_OF_SCOPE`.

## Evidence layers

The evidence model is intentionally separated:

```text
Canonical adapter CI
    Core conformance and input integrity
    projection tests
    exact COSMOS v7.3.0 source/API compatibility
    generated Python syntax
    Adapter Manager installed lifecycle
    provider-neutral release proof

Canonical native acceptance harness
    product wheel -> canonical generated procedure / suite
    native COSMOS plugin build / validate / load
    external OFDEMO TCP command + telemetry path
    persistent Script Runner completion
    persisted native report -> OpenC3 CTRF conversion
    joined adapter-owned runtime evidence

Historical COSMOS PoC
    previous native v7.3.0 runtime evidence
    retained as engineering evidence and regression reference
```

## Canonical native acceptance status

The product-owned native harness has now produced a clean PASS on exact adapter commit:

```text
44915686358da7334540d4fa1aca9e204d8a4ac9
```

against:

```text
OpenC3 COSMOS  v7.3.0
cosmos-project 9eb454f06fe0113d05aa6945d88b627155a2aa47
```

The accepted run proved in one execution:

```text
real STOP_ACQUISITION transport to the external OFDEMO target
real STATUS telemetry return with acquisition_active=false
native COSMOS Script Runner state completed
persisted native Script Runner report
OpenC3-native report -> CTRF conversion
CTRF tests 1 / passed 1 / failed 0
joined native-runtime-evidence status passed
```

The full runtime remains intentionally separate from mandatory GitHub-hosted CI while the required host/container topology is environment-dependent. Hosted CI proves source/API compatibility; the native harness proves the target runtime claim.

Historical PoC evidence remains useful as regression evidence but is not substituted for this canonical product-owned acceptance.

## Release-readiness implication

Integration Coverage analysis is complete for the current baseline and the canonical native runtime path has passed on the current candidate source commit.

Before release freeze, the same native acceptance must be repeated against the exact accepted source commit after merge so release evidence is tied to the source that will actually be published.

This is an evidence and provenance gate, not a reason to widen the semantic scope.

## Evidence rule

Every non-trivial disposition should remain explainable through one or more of:

```text
Core contract semantics
adapter implementation/tests
target-native compatibility evidence
explicit ownership boundary
explicit target limitation
```

Future versions should widen one semantic family at a time, first defining the target-owned meaning, then adding implementation, negative behavior and downstream-native evidence.
