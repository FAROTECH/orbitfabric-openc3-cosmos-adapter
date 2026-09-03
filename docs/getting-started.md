# Getting Started

This guide starts from a fresh checkout and ends with a working local Dummy Adapter. It then shows how to initialize developer-owned identity and adapt the Template to a real downstream target.

## Development baseline

The Template CI currently tests against this exact OrbitFabric Core commit:

```text
4377d6656c62aa1dc19a7ed81d2de872b6b22ccd
```

The package version reported by that Core commit is still `1.2.0`, but the Adapter Manager surfaces used by this Template were promoted after the public `v1.2.0` release. Template development therefore pins the exact Core commit instead of implying that every `orbitfabric==1.2.0` installation contains the required lifecycle surface.

This is a development and conformance baseline. It is not a generic runtime dependency requirement for every adapter.

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m pip install "orbitfabric @ git+https://github.com/FAROTECH/orbitfabric.git@4377d6656c62aa1dc19a7ed81d2de872b6b22ccd"
```

Run the safe local checks:

```bash
ruff check .
python tools/check_template_consistency.py
pytest -q
python -m build --wheel
mkdocs build --strict
```

## Try the Dummy Adapter

The checked-in `examples/input-set/` directory is a coherent synthetic fixture. It follows the documented Core Integration Input Set envelope, canonical roles, surface digests and input-set fingerprint algorithm.

It exists to keep the first developer path small and reviewable.

Project operation:

```bash
orbitfabric-dummy-adapter run \
  --operation project \
  --input-set-manifest examples/input-set/integration_input_manifest.json \
  --profile examples/profile.yaml \
  --output-dir /tmp/orbitfabric-dummy-project
```

Inspect:

```text
/tmp/orbitfabric-dummy-project/dummy_projection.json
/tmp/orbitfabric-dummy-project/integration_result.json
```

Scenario operation:

```bash
orbitfabric-dummy-adapter run \
  --operation verification_projection \
  --input-set-manifest examples/input-set/integration_input_manifest.json \
  --profile examples/profile.yaml \
  --operation-input scenario examples/scenario.yaml \
  --output-dir /tmp/orbitfabric-dummy-verification
```

Inspect:

```text
/tmp/orbitfabric-dummy-verification/dummy_verification_plan.json
/tmp/orbitfabric-dummy-verification/integration_result.json
```

Each operation writes a Core-conformant Integration Result plus one synthetic target artifact.

## Creation mode: initialize your adapter identity

Run the initializer only on a fresh repository created from the Template.

Example:

```bash
python tools/initialize_adapter.py \
  --adapter-name my-target \
  --python-package orbitfabric_my_target_adapter \
  --console-script orbitfabric-my-target
```

Optional overrides let you keep distribution, console and execution identities separate:

```bash
python tools/initialize_adapter.py \
  --adapter-name my-target \
  --python-package my_company_orbitfabric_adapter \
  --console-script my-of-adapter \
  --distribution-name my-company-orbitfabric-adapter \
  --adapter-id my-company-orbitfabric
```

The initializer updates only developer-owned starting identity and packaging locations. It also resets `coverage/integration-coverage.md` to the unclaimed coverage template so a new adapter cannot inherit Dummy coverage claims accidentally.

It does not decide:

```text
official publisher identity
official Source Coordinate
release version policy
target compatibility
supported Core surface claims
coverage claims
```

Those are maintainer decisions.

The initializer refuses to run again after the Template package identity has already been replaced.

After initialization, reinstall the editable package because its distribution and console entry point have changed:

```bash
python -m pip install -e ".[dev]"
python tools/check_template_consistency.py
pytest -q
```

Then review the remaining Dummy teaching semantics and replace them deliberately rather than treating initialization as a complete adapter migration.

## Build exact release identity locally

Build a wheel:

```bash
python -m build --wheel
```

Then construct a local Release Descriptor and Project Lock:

```bash
python tools/build_release_bundle.py \
  --wheel dist/orbitfabric_dummy_adapter-0.1.0.dev0-py3-none-any.whl \
  --authority template.local \
  --publisher orbitfabric \
  --name dummy-adapter
```

This writes:

```text
generated/release/adapter-release.json
generated/release/adapter-project-lock.json
generated/release/SHA256SUMS
```

The provider-neutral release proof in CI validates these contract shapes and then exercises exact Project Lock installation.

For an initialized real adapter, choose the release identity values deliberately. The local Template values above are examples only.

## Strong CI controls

The repository CI performs two controls beyond the normal local smoke path.

### Installed lifecycle proof

The installed lifecycle control uses a real Core-produced Integration Input Set, installs the exact wheel through Adapter Manager, removes the source package and installation inputs, then verifies and executes the installed adapter.

The script deliberately deletes `src/` inside the ephemeral CI checkout to prove isolation. It is guarded against local execution and must not be used as a normal developer command.

### Release proof

The release proof builds exact release identity, checks initial Project Lock state, installs the exact release, proves `MATCH`, proves repeated installation is `NOOP`, verifies the adapter and removes it.

The release-proof script is also a CI control. Use `tools/build_release_bundle.py` for local release construction.

## Adapt the Template to a real target

Initialization changes identity. It does not create target semantics.

Use this order:

```text
1. define the adapter purpose
2. analyze the Target Applicable Surface
3. declare the initial adapter scope
4. initialize developer-owned identity
5. review version and release policy
6. replace Integration Package Manifest compatibility declarations
7. replace Projection Profile schema and example
8. implement target-specific projection
9. add positive and negative tests
10. add target-native compatibility tests
11. retain Integration Result and target evidence
12. build exact release identity
13. publish the Integration Coverage Matrix
```

Read these pages next:

- [Repository Anatomy](repository-anatomy.md)
- [Adapter Identity](adapter-identity.md)
- [Projection Profile and Bindings](projection-profile-and-bindings.md)
- [Testing and Conformance](testing-and-conformance.md)
- [Evidence and Traceability](evidence-and-traceability.md)
- [Integration Coverage](integration-coverage.md)
- [Adapter Readiness Checklist](adapter-readiness-checklist.md)

## Before calling an adapter mature

A working projection is only the beginning.

For an OrbitFabric-maintained general-purpose adapter, review the full repository anatomy and the full Target Applicable Surface before deciding maturity or version. A focused community adapter can intentionally declare a smaller scope, but that scope should remain explicit.
