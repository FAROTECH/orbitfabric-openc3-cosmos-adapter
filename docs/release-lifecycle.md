# Release Lifecycle

This repository separates release construction, project selection and publication.

The adapter publisher owns the exact release definition and installable artifact bytes. A consuming project owns its exact Project Lock. A publication provider transports already identified release bytes.

## Three distinct objects

```text
Adapter Release Descriptor
    publisher-owned immutable release definition

Adapter Project Lock
    consumer-project exact selected resolution

Publication backend
    storage, discovery and transport
```

Do not treat these as one generic release bundle.

## What you build for lifecycle proof

For a Python adapter, the complete Template proof path is:

```text
clean checkout
    -> build wheel
    -> compute wheel SHA-256
    -> compute Integration Package Manifest SHA-256
    -> build Adapter Release Descriptor
    -> compute Release Descriptor SHA-256
    -> derive Adapter Project Lock
    -> Core conformance
    -> Adapter Manager install from lock
    -> MATCH
    -> evidence bundle
```

The Template provides:

```text
tools/build_release_bundle.py
```

Its default mode generates the complete developer/lifecycle proof material:

```text
adapter-release.json
adapter-project-lock.json
SHA256SUMS
```

This mode is useful when testing exact selection and Adapter Manager lifecycle behavior.

## What you build for publisher release material

A published adapter release should not include a canonical project lock because the lock belongs to a consuming project.

Use:

```bash
python tools/build_release_bundle.py \
  --wheel dist/orbitfabric_dummy_adapter-0.1.0.dev0-py3-none-any.whl \
  --authority <release-source-authority> \
  --publisher <publisher> \
  --name <adapter-name> \
  --release-only
```

This mode generates:

```text
adapter-release.json
SHA256SUMS
```

The release-only `SHA256SUMS` contains only publisher-side release assets produced or selected by the command:

```text
adapter wheel
adapter-release.json
```

The Integration Package Manifest is already integrity-bound by digest from inside the Release Descriptor and is packaged inside the wheel. It is not listed as a separate publication asset unless a concrete release policy deliberately publishes it separately.

## Build the wheel

From a clean checkout:

```bash
python -m build --wheel
```

The wheel must contain exactly one namespaced `integration_package.json` that belongs to the installed Python distribution.

## Build exact release identity

For the Dummy Adapter developer proof:

```bash
python tools/build_release_bundle.py \
  --wheel dist/orbitfabric_dummy_adapter-0.1.0.dev0-py3-none-any.whl \
  --authority template.local \
  --publisher orbitfabric \
  --name dummy-adapter
```

For a real adapter, replace all identity fields deliberately.

Do not infer logical publisher identity or Source Coordinate authority merely from repository hosting or package-manager account names.

The tool reads `project.version` from `pyproject.toml` unless `--release-version` is supplied explicitly.

The default Python installation backend is:

```text
python-wheel-managed-env
```

This is a backend-specific Template convention. It is not a universal adapter contract.

## Derive and validate Project Lock

The Project Lock contains exact project-selected identity:

```text
Source Coordinate
release version
Release Descriptor SHA-256
artifact id
artifact SHA-256
installation backend id
```

The default tool mode derives a lock immediately so the Template can prove the complete lifecycle.

A real consuming project may instead derive or retain its own lock after selecting a published release. That project-specific lock is not part of the publisher's immutable release membership.

The Template CI proves:

```text
initial state MISSING
    -> install exact release from lock
    -> MATCH
    -> second identical request NOOP
```

A nominal version match is not sufficient when byte identity differs.

## Validate before publishing

With the exact OrbitFabric Core baseline installed, validate the Release Descriptor and any project lock through Core-owned readers and conformance surfaces.

Also run target-native compatibility controls appropriate to the concrete downstream. Core conformance and downstream acceptance answer different questions.

## Publication is separate

The Template does not require GitHub Releases, PyPI or a future OrbitFabric registry.

A provider-specific publication step may later resolve and transport the exact publisher release material into the Core source-neutral `ResolvedAdapterRelease` seam.

Provider URLs are transport metadata. Do not insert them into Project Lock identity merely because one provider is used for publication.

If a backend supports immutable releases, attestations or signatures, retain those as release/trust evidence without redefining the generic OrbitFabric Release Descriptor.

## Evidence

The `release-proof` CI job intentionally uses the full default mode and retains:

```text
Adapter Release Descriptor
Project Lock used by the proof
SHA-256 summary
Adapter Manager reports
```

That evidence proves exact selection and lifecycle behavior.

It does not imply that the proof's Project Lock should be published as a canonical release artifact.
