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

For a successful Scenario projection, the Result registers
`orbitfabric.scenario_projection_accounting` `0.1-candidate` as a
generated JSON artifact. The generic payload is complete for the exact
consumed Scenario. Its mapping ids resolve only in that parent Result. The
adapter derives it directly from its projection plan before writing the Result.
