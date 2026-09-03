# Integration Contracts

The adapter consumes Core-owned candidate contracts and declares them in `integration_package.json`.

Initial operation:

```text
verification_projection
    protocol: orbitfabric.adapter_cli.v1
    required operation input: scenario
```

The adapter requires the current Integration Input Set surfaces used by the verified projector:

```text
entity_index
lint_report
mission_snapshot
relationship_manifest
```

Generic contract validity belongs to OrbitFabric Core. COSMOS-specific Profile schema, projection plan semantics and target artifact formats belong to this adapter.
