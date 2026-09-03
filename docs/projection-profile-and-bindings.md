# Projection Profile and Bindings

The Projection Profile is where adapter users express target-specific projection choices without editing the OrbitFabric Mission Model.

OrbitFabric owns the generic Profile envelope. The adapter owns the schema and semantics of its target-specific settings and binding configuration.

## Template files

```text
src/orbitfabric_dummy_adapter/schemas/profile-0.1.schema.json
examples/profile.yaml
src/orbitfabric_dummy_adapter/profile.py
src/orbitfabric_dummy_adapter/projection.py
```

A real adapter should replace the Dummy schema and projection semantics while preserving the generic OrbitFabric envelope expected by Core.

## Settings

The Dummy adapter defines one setting:

```yaml
settings:
  target_prefix: DUMMY_
```

This is intentionally target-specific. OrbitFabric Core does not assign meaning to `target_prefix`.

A real adapter can define settings such as target naming policy, target namespace, output grouping or other choices that belong to the downstream projection.

Keep settings focused on projection behavior. Do not use them to redefine Mission Model semantics.

## Bindings

A binding connects one or more OrbitFabric source entities to target projection intent.

The Dummy example is:

```yaml
bindings:
  - id: telemetry.battery_voltage
    intent: project
    sources:
      - domain: telemetry
        id: eps.battery.voltage
    config:
      target_name: BATTERY_VOLTAGE
```

The adapter resolves the source against the Core Integration Input Set, then applies its target-specific mapping rules.

For the Dummy adapter:

```text
source
    telemetry / eps.battery.voltage
        -> resolve in Entity Index
        -> apply target_name or generated default
        -> emit dummy target telemetry identity
        -> retain mapping in Integration Result
```

## Project and do_not_project

The Dummy schema supports:

```text
project
do_not_project
```

A `do_not_project` decision requires a reason. This makes an intentional omission distinguishable from an implementation gap or unresolved source.

A real adapter should use the generic binding intent model supported by the applicable Core contract and add only target-specific configuration that it genuinely needs.

## Supported Core input surfaces

The Integration Package Manifest declares which Core input surfaces the adapter consumes.

The Dummy adapter currently declares the Entity Index surface because `project` resolves telemetry identity from it.

Do not declare a Core surface only because it exists. Declare the surfaces that an operation actually consumes and test them against real Core-produced input where practical.

## Operation inputs

Operation inputs are separate from the main Core Integration Input Set.

The Dummy `verification_projection` operation declares one required file-backed role:

```text
scenario
```

The CLI receives it as:

```bash
--operation-input scenario PATH
```

The adapter records availability, identity and SHA-256 provenance for that operation input in the Integration Result.

Do not invent another execution mechanism for adapter-specific files. Use the Core-defined operation-input boundary when it applies.

## What a real adapter should test

At minimum:

```text
valid Profile accepted
invalid target-specific configuration rejected
source binding resolves
missing source fails closed
unsupported source domain fails closed
intentional do_not_project remains explicit
projected mapping appears in Integration Result
operation-input requirements match the Manifest
```

If the downstream has a native parser, compiler, validator, simulator or runtime acceptance path, add a compatibility test for the generated target artifact as a separate layer.
