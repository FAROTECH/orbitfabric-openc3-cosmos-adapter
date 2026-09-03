# Contributing

This repository contains the OrbitFabric OpenC3 COSMOS adapter product.

Changes should preserve the ownership boundary:

```text
OrbitFabric Core
    generic integration contracts and lifecycle semantics

OpenC3 COSMOS adapter
    target-specific projection, materialization, compatibility and evidence

OpenC3 COSMOS
    downstream execution semantics
```

Before opening a pull request, run:

```bash
python -m pip install -e ".[dev]"
ruff check .
python tools/check_adapter_consistency.py
pytest -q
python -m build --wheel
mkdocs build --strict
```

Do not copy historical PoC scaffolding into the product unless it remains technically necessary. Keep experiment history and architecture investigation in the PoC or Architecture Lab.

Do not widen the declared adapter scope merely to increase Integration Coverage. Coverage should describe the implementation, not drive unsupported implementation claims.
