# OrbitFabric OpenC3 COSMOS Adapter

Canonical OrbitFabric adapter for projecting mission verification intent toward OpenC3 COSMOS.

This repository is the productized successor of the historical `FAROTECH/OrbitFabric-OpenC3-COSMOS-PoC`. The PoC remains engineering evidence and a regression reference; this repository owns the reusable adapter product.

## Current scope

The initial adapter product focuses on Scenario-driven verification projection:

```text
OrbitFabric Scenario
    + Core Integration Input Set
    + OpenC3 COSMOS Projection Profile
        -> verification_projection
        -> resolved COSMOS verification plan
        -> native COSMOS Python procedure / suite
        -> Core-conformant Integration Result
```

The initial canonical operation is:

```text
verification_projection
    required operation input: scenario
```

A broader `project` operation is not declared merely for symmetry. It will be added only when concrete Ground integration evidence justifies a coherent mission-data projection surface.

## Target baseline

The first productization baseline preserves the downstream version already validated by the PoC:

```text
OpenC3 COSMOS v7.3.0
```

Target-native validation and release evidence remain separate from OrbitFabric Core contract conformance.

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

## Ownership boundary

```text
OrbitFabric Core
    owns generic integration contracts and Adapter Manager lifecycle semantics

This adapter
    owns OpenC3 COSMOS projection semantics, bindings, generated target artifacts,
    target compatibility controls and target-specific evidence

OpenC3 COSMOS
    owns downstream execution semantics and runtime acceptance
```

The adapter does not promote COSMOS-specific plan or runtime semantics into OrbitFabric Core.

## Development status

The canonical repository bootstrap is active. Product code is being extracted from the historical PoC deliberately, without importing experiment/G6/G9 scaffolding as permanent product structure.

Integration Coverage is a release-readiness obligation and is tracked separately in `FAROTECH/OrbitFabric-Architecture-Lab#22`; it is intentionally not a bootstrap blocker.

## Reference baselines

The repository follows the canonical adapter patterns proven by:

- `FAROTECH/orbitfabric-adapter-template`
- `FAROTECH/orbitfabric-openobsw-opensvf-adapter`

The exact OrbitFabric Core development/conformance baseline is:

```text
4377d6656c62aa1dc19a7ed81d2de872b6b22ccd
```
