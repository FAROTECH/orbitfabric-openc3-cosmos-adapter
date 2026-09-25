# Release Lifecycle

Current worktree: unpublished `0.2.1` post-migration candidate. See [release notes](releases/0.2.1.md). Prior release versions below describe historical baselines; new descriptors use `github.com/OrbitFabric`.

The adapter follows the same product boundary proven by the canonical public OrbitFabric adapters:

```text
Adapter Release Descriptor
    publisher-owned exact release identity

Adapter Project Lock
    consuming-project exact desired state

publication provider
    transport and distribution
```

Source version `0.2.0` does not by itself imply immutable `v0.2.0` publication.

## Release lineage

Historical published release:

```text
version:          0.1.0
logical key:      orbitfabric/openc3-cosmos
source authority: github.com/OrbitFabric
publisher:        orbitfabric
name:             openc3-cosmos
status:           published / immutable
```

Current release-preparation source:

```text
version:          0.2.0
logical key:      orbitfabric/openc3-cosmos
source authority: github.com/OrbitFabric
publisher:        orbitfabric
name:             openc3-cosmos
status:           pre-tag / acceptance pending
```

The logical key is continuous across the ownership migration. Historical Source Coordinate identity is not rewritten.

## Current readiness state

The 0.2.0 source adds generic Scenario Projection Accounting while preserving COSMOS-specific projection behavior and target baselines.

The remaining pre-tag gate is exact-source acceptance:

```text
merge release-preparation source
    -> permanent CI green on exact main commit
    -> native COSMOS acceptance PASS on that exact commit
    -> retain source / wheel / target provenance
```

Only then is the source eligible for the `v0.2.0` tag.

## Stable release membership

The publisher release membership for v0.2.0 is:

```text
v0.2.0 tag
orbitfabric_openc3_cosmos_adapter-0.2.0-py3-none-any.whl
adapter-release.json
SHA256SUMS
release notes
```

GitHub-generated source archives are provider conveniences and are not OrbitFabric adapter release membership.

## Evidence boundary

Core conformance does not substitute for target-native acceptance.

Hosted CI proves source checks, contract behavior, managed lifecycle, product-example execution and exact COSMOS source/API compatibility. The external native harness separately proves the runtime command/telemetry and Script Runner claim.

## Publication state

```text
v0.1.0  published / immutable / historical FAROTECH Source Coordinate
v0.2.0  published / immutable / OrbitFabric Source Coordinate
v0.2.1  unpublished patch candidate / OrbitFabric Source Coordinate
```

See [Release Readiness Checklist](adapter-readiness-checklist.md) and [Maintainer / Publisher Guide](publishing.md).
