# OrbitFabric OpenC3 COSMOS Adapter

This adapter projects OrbitFabric verification intent into target-owned artifacts consumable by OpenC3 COSMOS.

The initial product lane is deliberately narrow:

```text
Scenario
    + Core Integration Input Set
    + COSMOS Projection Profile
        -> verification_projection
        -> COSMOS verification plan
        -> COSMOS Python procedure / suite
        -> Integration Result
```

The adapter owns projection and traceability. OpenC3 COSMOS owns runtime execution. OrbitFabric Core remains authoritative for generic contracts.
