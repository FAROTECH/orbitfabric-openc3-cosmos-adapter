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

Source version `0.1.0` does not imply that immutable publication has already occurred.

## Current readiness state

The declared initial semantic scope is functionally complete, the consumer product surface is CI-backed, and canonical native COSMOS acceptance has passed on a candidate source commit.

The release-preparation source now freezes:

```text
version:          0.1.0
logical key:      orbitfabric/openc3-cosmos
source authority: github.com/FAROTECH
publisher:        orbitfabric
name:             openc3-cosmos
```

The remaining pre-tag gate is exact-source acceptance:

```text
merge the release-preparation source
    -> permanent CI green on exact main commit
    -> native COSMOS acceptance PASS on that exact commit
    -> retain source / wheel / target provenance
```

Only then is the source eligible for the `v0.1.0` tag.

## Stable release membership

The publisher release membership is:

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

See [Release Readiness Checklist](adapter-readiness-checklist.md) and [Maintainer / Publisher Guide](publishing.md).
