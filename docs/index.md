# OrbitFabric OpenC3 COSMOS Adapter

This adapter projects selected OrbitFabric verification intent into target-owned artifacts consumable by OpenC3 COSMOS.

The product lane is deliberately focused:

```text
Scenario
    + Core Integration Input Set
    + COSMOS Projection Profile
        -> verification_projection
        -> COSMOS verification plan
        -> COSMOS Python procedure / suite
        -> Integration Result
```

OrbitFabric Core owns generic contracts, the adapter owns projection, and OpenC3 COSMOS owns downstream execution semantics.

## Choose your path

### User

Start here when consuming an installed adapter:

- [Getting Started](getting-started.md)
- [Product Example](examples.md)
- [Projection Profile and Bindings](projection-profile-and-bindings.md)
- [Runtime Dependencies](runtime-dependencies.md)
- [Integration Coverage](integration-coverage.md)

### Developer / Contributor

Start here when changing source or target projection behavior:

- [Developer / Contributor Guide](development.md)
- [Architecture and Ownership](architecture-and-ownership.md)
- [Integration Contracts](integration-contracts.md)
- [Testing and Conformance](testing-and-conformance.md)

### Maintainer / Publisher

Start here when accepting source, constructing release artifacts or retaining evidence:

- [Maintainer / Publisher Guide](publishing.md)
- [Release Lifecycle](release-lifecycle.md)
- [Native COSMOS Acceptance](native-cosmos-acceptance.md)
- [Evidence and Traceability](evidence-and-traceability.md)
- [Adapter Identity](adapter-identity.md)

The current source version is `0.1.0.dev0`; stable publication is not yet claimed.
