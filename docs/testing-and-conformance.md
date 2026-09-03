# Testing and Conformance

A useful adapter test stack separates different questions instead of treating one green test as proof of the whole integration.

```text
unit tests
    does target-specific logic work?

negative tests
    do invalid inputs and unsupported cases fail closed?

Core conformance
    are Manifest, Profile bindings and Integration Results valid?

package tests
    does the built wheel contain the required assets and entry point?

installed lifecycle
    can Adapter Manager install, verify, execute and remove it in isolation?

release proof
    do exact Release Descriptor and Project Lock bytes identify what was tested?

target compatibility
    does the downstream ecosystem accept the generated output?
```

## Positive tests

The Dummy adapter includes successful execution tests for:

```text
project
verification_projection
Core Integration Result validation
release bundle construction
```

These prove that the happy path works against the declared contract.

## Negative tests

Negative controls are part of the Template, not optional cleanup.

Examples include:

```text
tampered Core Integration Input Set fingerprint rejected
missing required Scenario binding rejected
invalid release construction input rejected
zero or multiple installed manifests rejected by the Core Python backend controls
```

A real adapter should add target-specific negative cases such as unresolved bindings, invalid configuration, unsupported source variants and target constraints that must fail closed.

## Core conformance

The Template uses Core-owned validators for the Integration Package Manifest and Integration Result instead of copying those schemas into the adapter repository.

The release proof also loads the generated Adapter Release Descriptor and Adapter Project Lock through Core-owned contract surfaces.

If Core rejects a generic contract, fix the adapter or update the declared compatibility. Do not locally redefine the Core schema.

## Synthetic fixture versus real Core producer

The checked-in input-set fixture is synthetic but coherent. It keeps unit and smoke tests fast and reviewable.

The installed lifecycle control adds a stronger check using the real Core Integration Input Set producer from the demo mission. Both layers are useful:

```text
synthetic fixture
    fast deterministic developer tests

real Core producer
    integration boundary falsification
```

Do not let the synthetic fixture become the only proof for a maintained adapter.

## Installed lifecycle

The permanent CI proves:

```text
exact wheel
    -> managed environment install
    -> remove source and installation inputs
    -> verify installed state
    -> execute project
    -> execute verification_projection
    -> validate Integration Results
    -> remove
    -> inventory empty
```

This control is intentionally stronger than an editable install or a shared development environment.

The installed lifecycle script is CI-only because it deliberately deletes the source package in the ephemeral checkout.

## Release proof

The permanent release proof verifies:

```text
build exact wheel
    -> build Release Descriptor
    -> build Project Lock
    -> initial NOT_SATISFIED / MISSING
    -> install exact release
    -> MATCH
    -> repeated request NOOP
    -> verify
    -> remove
```

This proves exact desired state, not just a matching version string.

## Target-native compatibility

The Dummy target is synthetic and therefore has no independent downstream validator.

A concrete adapter should add the strongest target-native control that exists. Depending on the target, that might be:

```text
compiler
project build
native schema validation
parser/import test
simulator load
runtime smoke
mission database import
```

Keep target-native acceptance separate from generic Core conformance. Both are valuable and they answer different questions.

## Debugging by layer

When a test fails, identify the layer before changing contracts.

### Manifest or Result conformance failure

Check:

```text
declared versions
operation id
operation-input roles
Profile compatibility
supported Core surfaces
result provenance and mappings
```

### Projection failure

Check the Profile, source resolution and target-specific projection code. Inspect the failed `integration_result.json` before adding fallbacks.

### Package or install failure

Check the built wheel, declared runtime dependencies, unique packaged `integration_package.json` and console-script entry point.

Do not fix missing runtime dependencies by relying on the host Core environment.

### Installed verification failure

Use the Adapter Manager JSON report to identify the failing dimension:

```text
release_descriptor_integrity
manifest_integrity
manifest_conformance
execution_binding
backend_materialization
```

### Project Lock mismatch

Inspect the exact mismatch dimension instead of reinstalling blindly. Release version, Release Descriptor digest, artifact identity, artifact digest and backend identity are intentionally distinct.

### Target-native failure

If Core conformance passes but the target rejects the artifact, treat that as target compatibility evidence. Fix target projection semantics or narrow the declared compatibility. Do not weaken Core evidence to hide the target failure.

## Isolation rules

Tests should not rely on:

```text
ambient PYTHONPATH
accidental imports from the repository checkout
host-global executable discovery
undeclared runtime dependencies
provider availability during normal adapter execution
```

Isolation failures are useful findings because they expose hidden coupling before release.
