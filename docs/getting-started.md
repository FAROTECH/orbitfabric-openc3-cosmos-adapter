# Getting Started

This page describes the **consumer** path.

The normal OrbitFabric user installs a released adapter through Adapter Manager and executes it through Core. Editable source installs and the direct adapter CLI belong to the contributor workflow documented in [Development](development.md).

> The source is prepared as version `0.1.0`, but `v0.1.0` publication is not yet claimed. Until the immutable release exists, the commands below describe the managed lifecycle already proven by CI and the path that published release assets will expose.

## 1. Install OrbitFabric Core

Install a compatible OrbitFabric Core environment first.

The current adapter baseline is validated against exact Core commit:

```text
4377d6656c62aa1dc19a7ed81d2de872b6b22ccd
```

## 2. Obtain adapter release assets

The stable release membership is:

```text
orbitfabric_openc3_cosmos_adapter-0.1.0-py3-none-any.whl
adapter-release.json
SHA256SUMS
```

The Release Descriptor defines publisher-owned release identity. The wheel is the managed installation artifact.

## 3. Install through Adapter Manager

Verify the descriptor digest and install the exact wheel:

```bash
DESCRIPTOR_SHA256="$(sha256sum adapter-release.json | awk '{print $1}')"

orbitfabric adapter install adapter-release.json \
  --artifact orbitfabric_openc3_cosmos_adapter-0.1.0-py3-none-any.whl \
  --descriptor-sha256 "$DESCRIPTOR_SHA256" \
  --json > install.json
```

Capture the returned adapter instance id and verify the managed installation:

```bash
ORBITFABRIC_ADAPTER_INSTANCE_ID="$(python - <<'PY'
import json
print(json.load(open('install.json'))['instance_id'])
PY
)"

orbitfabric adapter verify "$ORBITFABRIC_ADAPTER_INSTANCE_ID" --json
```

A normal consumer does not need `pip install -e`, the adapter source package or the direct `orbitfabric-openc3-cosmos` command.

## 4. Run the product example

The repository contains one focused consumer-facing example:

```bash
bash examples/01-scenario-verification-projection/run.sh \
  "$ORBITFABRIC_ADAPTER_INSTANCE_ID"
```

The runner:

```text
exports a Core Integration Input Set from the example Mission Model
    -> verifies the installed adapter instance
    -> executes verification_projection through Adapter Manager
    -> writes disposable projection output
```

See [Product Example](examples.md) for the expected artifacts and evidence boundary.

## 5. Use your own inputs

The public operation is:

```text
verification_projection
    required operation input: scenario
```

Execute it through Core:

```bash
orbitfabric adapter execute "$ORBITFABRIC_ADAPTER_INSTANCE_ID" \
  --operation verification_projection \
  --input-set-manifest <integration_input_manifest.json> \
  --profile <projection-profile.yaml> \
  --operation-input "scenario=<scenario.yaml>" \
  --output-dir <output-directory>
```

Representative outputs:

```text
integration_result.json
verification_projection/verification_projection_plan.json
verification_projection/cosmos/verification.py
verification_projection/cosmos/verification_suite.py
```

The generated Python files are COSMOS-facing target artifacts. The Integration Result remains the primary OrbitFabric execution evidence surface.

## Next

- [Product Example](examples.md)
- [Projection Profile and Bindings](projection-profile-and-bindings.md)
- [Integration Coverage](integration-coverage.md)
- [Runtime Dependencies](runtime-dependencies.md)
