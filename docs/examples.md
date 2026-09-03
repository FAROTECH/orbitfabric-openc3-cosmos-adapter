# Product Example

The first product baseline intentionally carries one consumer-facing example rather than creating multiple examples for symmetry with other adapters.

## Example 01 - Scenario Verification Projection

Location:

```text
examples/01-scenario-verification-projection/
```

The example contains:

```text
mission/       self-contained OrbitFabric reference Mission Model
scenario.yaml authored verification intent
profile.yaml  COSMOS-specific bindings
run.sh        Adapter Manager consumer runner
```

Run it with an adapter instance already installed through Adapter Manager:

```bash
bash examples/01-scenario-verification-projection/run.sh \
  "$ORBITFABRIC_ADAPTER_INSTANCE_ID"
```

The runner generates a fresh Core Integration Input Set and executes:

```text
verification_projection
```

through:

```text
orbitfabric adapter execute
```

It does not call the direct adapter contributor CLI.

## Expected outputs

```text
generated/core-input/integration_input_manifest.json
generated/projection/integration_result.json
generated/projection/verification_projection/verification_projection_plan.json
generated/projection/verification_projection/cosmos/verification.py
generated/projection/verification_projection/cosmos/verification_suite.py
```

## Acceptance role

Permanent CI builds the adapter wheel, constructs a local Release Descriptor, installs the wheel through Adapter Manager, removes `src/` from the checkout and then executes the same example runner.

This proves that the example is a real managed-consumer surface rather than an editable-development shortcut.

## Evidence boundary

This example proves:

- authored Mission Model, Scenario and Profile consumption;
- Core Integration Input Set generation;
- installed Adapter Manager execution;
- Core-conformant Integration Result;
- Verification Projection Plan generation;
- COSMOS Python procedure and Suite generation.

It does **not** prove:

- a live COSMOS runtime;
- TCP command or telemetry transport;
- Script Runner execution;
- CTRF acceptance.

Those target-native claims belong to the separate [Native COSMOS Acceptance](native-cosmos-acceptance.md) gate.
