# Release Lifecycle

The adapter follows the same product boundary proven by the first canonical OpenOBSW/OpenSVF adapter:

```text
Adapter Release Descriptor
    publisher-owned exact release identity

Adapter Project Lock
    consuming-project exact desired state

publication provider
    transport and distribution
```

Development version `0.1.0.dev0` does not imply stable publication readiness.

## Current readiness state

The declared initial semantic scope is functionally complete and canonical native COSMOS acceptance has passed on a candidate source commit.

The remaining path to `v0.1.0` is product and release closure:

```text
consumer product example
    -> role-separated product docs
    -> stable version / Source Coordinate freeze
    -> permanent CI on exact stable source
    -> native COSMOS acceptance on exact stable source
    -> exact v0.1.0 tag
    -> definitive release assets
    -> immutable publication
    -> external greenfield acceptance
```

Do not widen semantic scope to make the release appear more complete.

## Stable release membership

The stable publisher release is expected to contain only the normative adapter release material:

```text
v0.1.0 tag
orbitfabric_openc3_cosmos_adapter-0.1.0-py3-none-any.whl
adapter-release.json
SHA256SUMS
release notes
```

GitHub-generated source archives are provider conveniences and are not OrbitFabric adapter release membership.

## Evidence boundary

Core conformance does not substitute for target-native acceptance.

Hosted CI proves source checks, contract behavior, managed lifecycle, product-example execution and exact COSMOS source/API compatibility. The external native harness separately proves the runtime command/telemetry and Script Runner claim.

## Publication state

No immutable `v0.1.0` release is currently claimed.

See [Maintainer / Publisher Guide](publishing.md) for the construction and publication sequence.
