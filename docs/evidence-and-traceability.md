# Evidence and Traceability

An adapter should not only generate target files. It should retain enough evidence to explain what was consumed, what was projected and which exact bytes were produced.

OrbitFabric Integration Result is the primary execution evidence surface demonstrated by this Template.

## Execution evidence

Every successful Dummy operation writes:

```text
integration_result.json
```

alongside the generated target artifact.

The result retains, as applicable:

```text
adapter identity and version
operation identity
Core Integration Input Set provenance
Projection Profile provenance
operation-input provenance
generated artifact identity and SHA-256
mapping disposition and target identity
result status
```

The exact fields and semantics are governed by Core. The adapter fills them with target-specific evidence.

## Mapping traceability

For the `project` operation, the Dummy adapter emits mapping records that connect an OrbitFabric source entity to the generated target identity.

Conceptually:

```text
OrbitFabric source
    -> binding
    -> target projection
    -> Integration Result mapping
```

A real adapter should retain enough mapping evidence to answer:

```text
which source concept produced this target element?
was it projected, omitted or blocked?
which target identifier or artifact contains it?
```

## Operation-input provenance

For `verification_projection`, the Scenario is a required operation input.

The Dummy result records:

```text
role
availability status
Scenario id
SHA-256
```

This distinguishes the main Core Integration Input Set from additional operation-scoped inputs while preserving traceability for both.

## Artifact byte identity

Generated artifacts include SHA-256 evidence in the Integration Result.

The installed lifecycle proof validates the result after executing the adapter from its isolated managed environment.

The release proof separately retains byte identity for:

```text
adapter wheel
Integration Package Manifest
Adapter Release Descriptor
Adapter Project Lock
```

Release evidence and execution evidence answer different questions. Do not collapse them into one generic trust flag.

## CI evidence bundles

The Template CI uploads evidence from two stronger controls.

### Installed lifecycle evidence

Produced by:

```text
.github/scripts/installed-lifecycle.sh
```

It proves the adapter can be installed, verified and executed after source checkout artifacts used for installation are removed.

### Release proof evidence

Produced by:

```text
.github/scripts/release-proof.sh
```

It proves exact release construction and Project Lock state transitions.

The evidence bundle is not a new OrbitFabric contract. It is retained engineering evidence built from Core-owned contracts and Adapter Manager reports.

## Target-native evidence

A real downstream may provide stronger acceptance mechanisms such as:

```text
compiler
schema validator
native parser
simulator
runtime smoke test
project build
mission database import
```

Use the strongest meaningful target-native control available and retain its result separately from generic OrbitFabric conformance.

A generated artifact can be perfectly Core-conformant as an Integration Result and still be rejected by the target. Both layers matter.
