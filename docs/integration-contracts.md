# Integration Contracts

Use OrbitFabric Core documentation and Core-owned schemas as the normative reference for generic adapter contracts.

This Template demonstrates how to consume those surfaces, but it does not redefine them.

## Core-owned surfaces used by the Template

```text
Core Integration Input Set
Projection Profile generic envelope
Integration Package Manifest
orbitfabric.adapter_cli.v1
Integration Result
Adapter Release Descriptor
Adapter Project Lock
Adapter Manager lifecycle
```

If a Core-owned field, version or semantic rule changes, update the Template and its declared compatibility. Do not fork the generic contract locally.

## Integration Package Manifest

The packaged manifest is:

```text
src/orbitfabric_dummy_adapter/integration_package.json
```

It declares:

```text
adapter identity and version
integration identity
capabilities
supported Core input-set versions
supported Core surfaces
Profile compatibility
execution protocol and argv prefix
operations and operation-input requirements
Integration Result compatibility
```

The Python managed-environment backend locates exactly one `integration_package.json` owned by the installed distribution. That discovery rule is backend-specific. Manifest contents remain Core-owned.

## Supported Core input surfaces

The Dummy adapter declares one Core surface:

```text
role: entity_index
kind: orbitfabric.entity_index
format version: 0.1
```

The `project` operation uses that surface to resolve telemetry entity identity.

A real adapter must review this declaration deliberately. Declare the surfaces that the implementation actually consumes, with compatible versions, instead of copying every Core surface into the Manifest.

A Scenario used by `verification_projection` is not smuggled into the main Integration Input Set. It is declared as an operation input with role `scenario`.

## Execution protocol

The Manifest declares the Core-defined protocol:

```text
orbitfabric.adapter_cli.v1
```

The Dummy console entry point is:

```text
orbitfabric-dummy-adapter
```

The implementation in `src/orbitfabric_dummy_adapter/cli.py` supports:

```text
run
--operation
--input-set-manifest
--profile
--operation-input ROLE PATH
--output-dir
```

Do not introduce another adapter execution protocol for target-specific convenience. Adapt target logic behind the Core-defined protocol.

## Operations

The Dummy Manifest declares:

```text
project
    no operation inputs

verification_projection
    one required role: scenario
```

Operation-input declaration, CLI binding and Integration Result provenance must remain consistent. Tests should fail if those three views drift.

## Integration Result

Every operation writes:

```text
integration_result.json
```

The result is validated through Core-owned conformance. It retains operation status, consumed input provenance, generated artifact identity, mappings and operation-input provenance as applicable.

See [Evidence and Traceability](evidence-and-traceability.md).

## Template integration identity

The Dummy example uses:

```text
integration.id = orbitfabric-dummy
adapter.id     = orbitfabric-dummy
```

Those values are examples only. They do not define the logical Source Coordinate or publisher identity for real adapters.

See [Adapter Identity](adapter-identity.md) before changing them.

## Projection Profile ownership

The generic Profile envelope is governed by OrbitFabric.

The integration-specific schema in:

```text
src/orbitfabric_dummy_adapter/schemas/profile-0.1.schema.json
```

owns only Dummy target choices.

A real adapter replaces that target-specific schema and mapping behavior while preserving the generic envelope and declared compatibility.

See [Projection Profile and Bindings](projection-profile-and-bindings.md).
