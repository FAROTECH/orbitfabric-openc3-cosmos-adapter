# Architecture and Ownership

The repository boundary is:

```text
OrbitFabric Core
    contracts
    schemas
    conformance
    Adapter Manager lifecycle

Adapter Developer Template
    repository pattern
    executable examples
    tests
    developer guidance
    recommended coverage method

Concrete Adapter
    target-specific schema
    target-specific projection
    target compatibility
    declared scope
    native evidence
```

## Know which kind of rule you are reading

The Template uses several kinds of guidance. Keep them distinct.

| Kind | Meaning | Example |
| --- | --- | --- |
| Core-owned normative contract | Generic OrbitFabric integration meaning | Integration Package Manifest, `orbitfabric.adapter_cli.v1`, Integration Result |
| Template convention | Recommended repository pattern demonstrated here | source layout, developer docs structure, local consistency checker |
| Python backend-specific convention | Required only by the current Python wheel managed-environment backend | exactly one distribution-owned `integration_package.json` |
| Adapter-specific target behavior | Meaning owned by one concrete integration | target Profile settings, target artifact format, mapping rules |
| Recommended community practice | Useful but not required by generic Core conformance | publishing an Integration Coverage Matrix |
| OrbitFabric-maintained adapter policy | Stricter project policy for adapters maintained as official OrbitFabric integrations | analyze full Target Applicable Surface before maturity decision |

Do not promote a Template convention into a universal OrbitFabric contract merely because the Dummy example uses it.

## Core wins

The Template must never become an alternative specification.

Do not copy Core schemas into a concrete adapter to modify their meaning.

Do not invent a second adapter execution protocol.

Do not parse Mission Model YAML as a semantic fallback when Core Integration Input Set surfaces are available.

When a generic rule belongs in Core, change Core deliberately and then update the Template to consume the promoted rule.

## Adapter owns projection

The adapter owns the translation from OrbitFabric intent to downstream representation.

That includes:

```text
target-specific Profile schema
target settings
target binding configuration
target naming and mapping rules
generated artifact formats
target-specific diagnostics
target-native compatibility evidence
```

The adapter does not acquire authority to reinterpret Core semantic facts.

## Python packaging

The Python wheel backend identifies the exact installed adapter distribution and requires exactly one `integration_package.json` owned by that distribution.

The Template therefore places the manifest inside the namespaced adapter package:

```text
src/orbitfabric_dummy_adapter/
    integration_package.json
```

The filename and distribution discovery mechanics are Python backend policy. Manifest contents remain governed by Core.

A future non-Python backend may use a different materialization and discovery mechanism without changing the generic adapter lifecycle contract.

## Runtime dependency ownership

An adapter declares the runtime dependencies required by its own implementation.

The installation backend materializes those dependencies.

Adapter Manager does not silently inject missing dependencies from the host Core process.

The Dummy adapter deliberately avoids importing the OrbitFabric Python package at runtime because it can consume public machine-readable surfaces directly.

## Release source versus execution

Where release bytes are found is separate from how an installed adapter executes.

```text
publication or release source
    -> exact resolved release
    -> Adapter Manager installation
    -> installed execution endpoint
    -> orbitfabric.adapter_cli.v1
```

GitHub, PyPI, a future OrbitFabric registry or a local explicit source must not become a second execution protocol.
