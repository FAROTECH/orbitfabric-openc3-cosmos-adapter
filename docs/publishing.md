# Maintainer / Publisher Guide

Current worktree: unpublished `0.2.1` post-migration candidate. See [release notes](releases/0.2.1.md). Prior release versions below describe historical baselines; new descriptors use `github.com/OrbitFabric`.

Release construction is a maintainer responsibility and is separate from normal adapter consumption.

The source version is `0.2.0`. The immutable `v0.1.0` release remains
published under its historical Source Coordinate. The next release is `v0.2.0`
and must complete all release gates before publication.

## Release ownership

Keep three objects distinct:

```text
Adapter Release Descriptor
    publisher-owned exact release definition

Adapter Project Lock
    consumer-project exact desired state

publication provider
    storage, immutability and transport
```

## Build provider-neutral release material

From the exact accepted stable source commit:

```bash
python -m build --wheel

python tools/build_release_bundle.py \
  --wheel dist/orbitfabric_openc3_cosmos_adapter-0.2.0-py3-none-any.whl \
  --authority github.com/OrbitFabric \
  --publisher orbitfabric \
  --name openc3-cosmos \
  --release-only
```

Publisher release material is exactly:

```text
orbitfabric_openc3_cosmos_adapter-0.2.0-py3-none-any.whl
adapter-release.json
SHA256SUMS
```

The default tool mode additionally builds an Adapter Project Lock for lifecycle proof. That lock is consumer selection evidence and is not publisher release membership.

## Source Coordinate lineage

The historical first stable release remains:

```text
v0.1.0

authority = github.com/OrbitFabric
publisher = orbitfabric
name      = openc3-cosmos
```

Rendered:

```text
github.com/OrbitFabric:orbitfabric/openc3-cosmos
```

The first post-migration release shall use:

```text
v0.2.0

authority = github.com/OrbitFabric
publisher = orbitfabric
name      = openc3-cosmos
```

Rendered:

```text
github.com/OrbitFabric:orbitfabric/openc3-cosmos
```

The logical key remains `orbitfabric/openc3-cosmos`. Historical release identity is not rewritten when repository ownership changes.

## Required source gates

Before tagging require all items in the [Release Readiness Checklist](adapter-readiness-checklist.md), including:

```text
Python 3.11 / 3.12 checks
adapter consistency
unit and negative tests
wheel/package ownership
strict documentation build
exact COSMOS source/API compatibility
installed Adapter Manager lifecycle
consumer product example
provider-neutral release proof
exact-source native COSMOS acceptance
```

Core conformance and downstream-native acceptance remain separate evidence layers.

## Publication sequence

After exact stable source acceptance:

```text
accepted stable main commit
    -> exact v0.2.0 tag
    -> definitive wheel
    -> adapter-release.json
    -> SHA256SUMS
    -> local digest and descriptor verification
    -> immutable publication
    -> published-byte verification
    -> external greenfield Adapter Manager install
    -> consumer product example execution
    -> native acceptance required by the release claim
    -> final Architecture Lab publication evidence
```

The repository is public and now lives under the OrbitFabric GitHub Organization.

## No source provenance shortcuts

Do not use a synthetic pull-request merge ref as normative release provenance.

The stable tag, definitive release bytes and final native acceptance must all refer to the exact accepted stable source commit.

See [Release Lifecycle](release-lifecycle.md) and [Evidence and Traceability](evidence-and-traceability.md).
