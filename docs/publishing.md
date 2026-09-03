# Maintainer / Publisher Guide

Release construction is a maintainer responsibility and is separate from normal adapter consumption.

The current `0.1.0.dev0` source is not a published stable release.

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

From an accepted source commit:

```bash
python -m build --wheel

python tools/build_release_bundle.py \
  --wheel dist/orbitfabric_openc3_cosmos_adapter-<version>-py3-none-any.whl \
  --authority github.com/FAROTECH \
  --publisher orbitfabric \
  --name openc3-cosmos \
  --release-only
```

Publisher release material is:

```text
wheel
adapter-release.json
SHA256SUMS
```

The default tool mode additionally builds an Adapter Project Lock for lifecycle proof. That lock is consumer selection evidence and is not publisher release membership.

## Stable Source Coordinate candidate

The first stable release is expected to use:

```text
authority = github.com/FAROTECH
publisher = orbitfabric
name      = openc3-cosmos
```

Rendered:

```text
github.com/FAROTECH:orbitfabric/openc3-cosmos
```

The stable release-preparation change must freeze this identity together with `0.1.0`; this development document does not perform that version freeze.

## Required source gates

Before tagging a stable release require:

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
    -> exact v0.1.0 tag
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

The repository is currently private. If `v0.1.0` follows the public OpenOBSW/OpenSVF publication model, repository visibility must be changed before the public publication and greenfield phase.

## No source provenance shortcuts

Do not use a synthetic pull-request merge ref as normative release provenance.

The stable tag, definitive release bytes and final native acceptance must all refer to the exact accepted stable source commit.

See [Release Lifecycle](release-lifecycle.md) and [Evidence and Traceability](evidence-and-traceability.md).
