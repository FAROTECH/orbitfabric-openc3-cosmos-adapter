# Developer / Contributor Guide

This page describes the source-development path. It is intentionally separate from the normal Adapter Manager consumer lifecycle.

## Development setup

```bash
git clone https://github.com/FAROTECH/orbitfabric-openc3-cosmos-adapter.git
cd orbitfabric-openc3-cosmos-adapter

python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Run the normal source checks:

```bash
ruff check .
python tools/check_adapter_consistency.py
pytest -q
python -m build --wheel
mkdocs build --strict
```

## Direct adapter CLI

The direct console command:

```text
orbitfabric-openc3-cosmos
```

is primarily a contributor surface.

Example direct execution:

```bash
orbitfabric-openc3-cosmos run \
  --operation verification_projection \
  --input-set-manifest <integration_input_manifest.json> \
  --profile <projection-profile.yaml> \
  --operation-input "scenario=<scenario.yaml>" \
  --output-dir <output-directory>
```

Do not present this editable-development flow as the normal installed user lifecycle.

## Ownership rules

Preserve the boundary:

```text
OrbitFabric Core
    generic contracts and lifecycle semantics

OpenC3 COSMOS adapter
    target-specific projection, materialization, compatibility and evidence

OpenC3 COSMOS
    downstream execution semantics
```

Do not parse OrbitFabric source YAML as a private semantic API when the corresponding Core integration surface exists.

Do not widen Integration Coverage merely to increase a percentage.

## Native target work

The downstream-native acceptance surface is:

```text
tools/run_native_cosmos_acceptance.sh
```

See [Native COSMOS Acceptance](native-cosmos-acceptance.md) before changing target compatibility assumptions or the pinned OpenC3 baseline.

## Related documentation

- [Architecture and Ownership](architecture-and-ownership.md)
- [Integration Contracts](integration-contracts.md)
- [Testing and Conformance](testing-and-conformance.md)
- [Projection Profile and Bindings](projection-profile-and-bindings.md)
- repository `CONTRIBUTING.md`
