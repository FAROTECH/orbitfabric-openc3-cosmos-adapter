# Adapter Identity

A real adapter has several identities. Keep them separate instead of forcing one string to mean everything.

## Start from the initializer

On a fresh repository created from this Template, initialize developer-owned identity with:

```bash
python tools/initialize_adapter.py \
  --adapter-name my-target \
  --python-package orbitfabric_my_target_adapter \
  --console-script orbitfabric-my-target
```

The initializer keeps distribution, Python package namespace, console script and execution identity as distinct concepts. Optional `--distribution-name` and `--adapter-id` overrides let a maintainer choose them independently.

It does not choose official publisher identity, Source Coordinate, release maturity, compatibility or coverage claims.

## Python distribution identity

The Template package is:

```text
orbitfabric-dummy-adapter
```

and the Python import namespace is:

```text
orbitfabric_dummy_adapter
```

These are packaging identities.

For a real adapter, choose a package name that is unique and clear. The initializer updates `pyproject.toml`, the source package directory and imports consistently.

## Console script identity

The Template installs:

```text
orbitfabric-dummy-adapter
```

as its console entry point.

This is the executable name used by the Python packaging backend and recorded in the Manifest `execution.argv_prefix`.

The console script does not have to equal the Python distribution name or `adapter.id`.

## Execution identity

The Integration Package Manifest contains:

```text
adapter.id = orbitfabric-dummy
```

This is the identity used by the Core-defined integration execution contract.

Do not reinterpret `adapter.id` as a registry key, GitHub repository name or publisher identity.

A real adapter should choose a stable execution identity and preserve it across releases unless an intentional compatibility break requires otherwise.

## Integration identity

The Dummy Profile and Manifest use:

```text
integration.id = orbitfabric-dummy
```

This identifies the integration whose Profile schema and target-specific projection semantics are being used.

For this small Template the execution and integration identifiers are equal. That equality is convenient, not a universal rule.

The initializer currently keeps them aligned as a safe starting point. A concrete integration may separate them later only with deliberate contract and compatibility review.

## Source Coordinate

Release identity uses a separate logical coordinate:

```text
authority
publisher
name
```

Together these form the Adapter Source Coordinate.

Example used only by the local release proof:

```text
template.local
orbitfabric
dummy-adapter
```

A real adapter must choose these values deliberately. A GitHub repository URL, package filename or executable path is not the Source Coordinate.

The publication provider can change without changing what the release logically represents.

The initializer intentionally does not assign these values.

## Version ownership

The Template currently carries version `0.1.0.dev0` in `pyproject.toml` and in the Dummy Integration Package Manifest.

`tools/build_release_bundle.py` uses `project.version` as the default `release_version` unless the developer supplies `--release-version` explicitly.

These version values serve different contracts. Keep them intentionally aligned when that is the adapter release policy, but do not invent a universal equality rule unless Core defines one.

Before a release, review at least:

```text
pyproject.toml project.version
Integration Package Manifest adapter.version
Adapter Release Descriptor release_version
Projection Profile compatibility versions
supported Core input versions
Integration Result versions
```

## What to review after initialization

The initializer removes the mechanical identity drift, but it does not complete the adapter. Review these locations together:

```text
pyproject.toml
    project.name
    project.version
    project.scripts
    wheel package namespace

src/<your_package>/integration_package.json
    adapter.id
    adapter.version
    integration.id
    execution argv_prefix
    compatibility declarations

src/<your_package>/schemas/profile-*.schema.json
    integration.id constraint
    target-specific settings and bindings

examples/profile.yaml
    integration.id
    target-specific example choices

release construction
    authority
    publisher
    name
    release_version

coverage/integration-coverage.md
    actual target applicability and declared scope
```

Run `python tools/check_template_consistency.py` after identity changes so mechanical drift fails during normal development instead of appearing during publication.
