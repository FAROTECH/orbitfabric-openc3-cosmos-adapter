# OrbitFabric Adapter Developer Template

This documentation is for developers building an OrbitFabric adapter.

The Template is executable. The included Dummy Adapter builds, runs, emits Core-conformant Integration Results, installs through Adapter Manager, proves exact Project Lock state and demonstrates an Integration Coverage Matrix.

OrbitFabric Core remains authoritative for generic integration contracts. The Template explains how to consume those contracts correctly inside a maintainable adapter repository.

## Recommended path

```text
Getting Started
    -> Repository Anatomy
    -> Adapter Identity
    -> Architecture and Ownership
    -> Integration Contracts
    -> Projection Profile and Bindings
    -> Testing and Conformance
    -> Evidence and Traceability
    -> Runtime Dependencies
    -> Release Lifecycle
    -> Integration Coverage
    -> Adapter Readiness Checklist
```

If you are extracting an adapter from an existing experiment, read [Migrating from a PoC](migrating-from-poc.md) after the main developer path.

## One rule to remember

```text
Core defines what is valid.
The Template demonstrates how to build it well.
The adapter owns target-specific projection and evidence.
```
