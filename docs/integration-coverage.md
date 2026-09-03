# Integration Coverage

Integration Coverage describes which OrbitFabric semantics are applicable to the OpenC3 COSMOS Ground integration role, which subset this adapter deliberately claims, and the disposition of each analyzed area.

It is not a count of OpenC3 COSMOS product features and it is not a generic OrbitFabric Core conformance contract.

The complete user-facing matrix is visible directly in the repository README on GitHub. The detailed maintainer declaration, rationale and roadmap are stored at:

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

The README intentionally presents the complete matrix in a compact four-column product view. The file under `coverage/` remains the detailed engineering declaration with target applicability, scope, evidence and roadmap columns.

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

## Current `0.1.0` summary

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
    consumer product example
    provider-neutral release proof

Canonical native acceptance harness
    product wheel -> canonical generated procedure / suite
    native COSMOS plugin build / validate / load
    external OFDEMO TCP command + telemetry path
    persistent Script Runner completion
    persisted native report -> OpenC3 CTRF conversion
    joined adapter-owned runtime evidence
```

## Canonical native acceptance status

The product-owned native harness produced a clean PASS on candidate adapter commit:

```text
44915686358da7334540d4fa1aca9e204d8a4ac9
```

against:

```text
OpenC3 COSMOS  v7.3.0
cosmos-project 9eb454f06fe0113d05aa6945d88b627155a2aa47
```

That run proved real command and telemetry transport, native Script Runner completion, persisted native report conversion and CTRF 1 / 1 PASS.

The stable release gate now requires the same native acceptance on the exact accepted `0.1.0` main source commit after release-preparation merge.

This is a provenance gate, not a semantic coverage gap.

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
