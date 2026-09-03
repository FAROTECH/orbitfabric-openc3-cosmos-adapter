# Contributing

This repository is a developer template for OrbitFabric adapters.

Changes should improve a reusable adapter-development pattern, not encode special assumptions from one downstream integration.

## Preserve these boundaries

1. OrbitFabric Core remains the normative authority for generic contracts and conformance.
2. Target-specific semantics belong in the adapter package, not in Core.
3. Tests must exercise packaged or installed behavior when the relevant lifecycle control exists.
4. Do not rely on ambient `PYTHONPATH`, ambient executable discovery or undeclared runtime dependencies.
5. Keep the Dummy adapter small. Add examples only when they teach a reusable adapter-development pattern.
6. Do not introduce a generic Adapter SDK until repeated real-adapter use proves shared implementation code.
7. Keep release construction provider-neutral. Publication provider details must not redefine release identity.
8. Keep Integration Coverage guidance non-normative for community adapters unless Core deliberately promotes a future contract.

## Before changing the Template

Ask which layer owns the proposed change:

```text
Core contract
Template convention
Python backend convention
adapter target semantics
developer guidance
project policy
```

If the change modifies generic contract meaning, it probably belongs in OrbitFabric Core rather than here.

## Local checks

Run before opening a pull request:

```bash
ruff check .
python tools/check_template_consistency.py
pytest -q
python -m build --wheel
mkdocs build --strict
```

The stronger installed lifecycle and release-proof shell scripts are CI controls. The installed lifecycle control deliberately removes the source package inside the ephemeral CI checkout to prove installed isolation, so it is guarded against local execution.

Use `tools/build_release_bundle.py` when you want to exercise provider-neutral release construction locally.

## Documentation changes

Write for a developer who has no knowledge of how this Template was originally designed.

Prefer:

```text
what the developer needs to decide
which file they change
which contract owns the rule
which command verifies the result
```

Keep design history and architecture investigation outside the developer documentation. The repository should describe the current supported pattern.
