# Getting Started

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"

ruff check .
python tools/check_adapter_consistency.py
pytest -q
```

The adapter currently pins the exact OrbitFabric Core development/conformance baseline:

```text
4377d6656c62aa1dc19a7ed81d2de872b6b22ccd
```

## Execute verification projection

The canonical operation is `verification_projection` and requires one file-backed operation input with role `scenario`:

```bash
orbitfabric-openc3-cosmos run \
  --operation verification_projection \
  --input-set-manifest <core-input>/integration_input_manifest.json \
  --profile examples/profile.yaml \
  --operation-input scenario <scenario.yaml> \
  --output-dir /tmp/orbitfabric-cosmos
```

A successful execution produces:

```text
verification_projection/verification_projection_plan.json
verification_projection/cosmos/verification.py
verification_projection/cosmos/verification_suite.py
integration_result.json
```

The generated COSMOS files are target artifacts. The Integration Result is the primary OrbitFabric execution evidence surface.
