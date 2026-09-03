# OrbitFabric Adapter Developer Template

Executable starting point for building, testing, packaging, releasing and documenting an OrbitFabric adapter.

Use this repository when you want to create an adapter that consumes OrbitFabric integration surfaces and projects them toward a concrete downstream target.

OrbitFabric Core remains the normative authority for generic contracts, schemas, conformance and Adapter Manager lifecycle semantics. This Template demonstrates how an adapter repository can consume those contracts correctly.

## Start here

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m pip install "orbitfabric @ git+https://github.com/FAROTECH/orbitfabric.git@4377d6656c62aa1dc19a7ed81d2de872b6b22ccd"

ruff check .
python tools/check_template_consistency.py
pytest -q
python -m build --wheel
mkdocs build --strict
```

Then follow [Getting Started](docs/getting-started.md) and [Repository Anatomy](docs/repository-anatomy.md).

The developer guide is authored in `docs/`, built with MkDocs and validated with `mkdocs build --strict` in CI.

## Two ways to use the Template

### Learning mode

Clone the repository unchanged, run the Dummy Adapter and inspect the full lifecycle. This is the fastest way to understand the contract and repository shape before targeting a real downstream.

### Creation mode

Start from a fresh repository created from this Template, then initialize only developer-owned identity:

```bash
python tools/initialize_adapter.py \
  --adapter-name my-target \
  --python-package orbitfabric_my_target_adapter \
  --console-script orbitfabric-my-target
```

The initializer updates packaging and execution identity consistently, but it deliberately does not choose official publisher identity, Source Coordinate, release maturity, supported target claims or Integration Coverage claims. Those remain maintainer decisions.

Read [Adapter Identity](docs/adapter-identity.md) before using overrides such as a custom distribution name or `adapter.id`.

## What the Dummy Adapter demonstrates

The included Dummy Adapter deliberately has a small declared scope:

- project telemetry entity identity into a synthetic target representation;
- project Scenario identity and provenance into a synthetic verification plan.

It exercises both supported execution shapes:

```text
project
    zero operation inputs

verification_projection
    one required file-backed role: scenario
```

The Dummy target is synthetic. Its semantics are examples only and do not extend OrbitFabric Core.

The Template also proves:

```text
Core contract conformance
    -> Python wheel build
    -> Adapter Manager isolated install
    -> installed verify
    -> installed execute
    -> Integration Result validation
    -> remove
    -> empty inventory

exact release artifact
    -> Adapter Release Descriptor
    -> Adapter Project Lock
    -> MISSING
    -> exact install from lock
    -> MATCH
    -> repeated request NOOP
```

## Adapter repository anatomy

A concrete adapter repository normally needs these areas:

```text
identity
packaging
integration contract
projection
implementation
conformance
evidence
developer experience
automation
```

This Template provides a working example of each area. See [Repository Anatomy](docs/repository-anatomy.md) for the exact files and responsibilities.

## What you replace for a real adapter

At minimum, review and deliberately replace:

```text
Python distribution name and package namespace
console script name
adapter.id and integration.id
release Source Coordinate
adapter version
Integration Package Manifest
supported Core input surfaces
Projection Profile schema
Projection Profile example and bindings
target-specific projection code
target artifact formats
examples and fixtures
target compatibility tests
Integration Coverage Matrix
release identity values
```

Do not rename fields or change semantics that belong to Core-owned contracts. If this Template and OrbitFabric Core disagree, Core wins.

Read [Adapter Identity](docs/adapter-identity.md) before changing identifiers, and [Projection Profile and Bindings](docs/projection-profile-and-bindings.md) before changing projection semantics.

## Repository map

```text
src/orbitfabric_dummy_adapter/
    adapter implementation
    integration_package.json
    schemas/profile-0.1.schema.json

examples/
    synthetic input set, Projection Profile and Scenario

tests/
    positive, negative, contract and package checks

coverage/
    completed Dummy Integration Coverage Matrix
    reusable coverage template

docs/
    developer guidance

tools/
    adapter identity initializer
    template consistency check
    release bundle builder

.github/
    CI
    isolated installed lifecycle proof
    provider-neutral release proof
```

## Developer documentation

Recommended reading order:

1. [Getting Started](docs/getting-started.md)
2. [Repository Anatomy](docs/repository-anatomy.md)
3. [Adapter Identity](docs/adapter-identity.md)
4. [Architecture and Ownership](docs/architecture-and-ownership.md)
5. [Integration Contracts](docs/integration-contracts.md)
6. [Projection Profile and Bindings](docs/projection-profile-and-bindings.md)
7. [Testing and Conformance](docs/testing-and-conformance.md)
8. [Evidence and Traceability](docs/evidence-and-traceability.md)
9. [Runtime Dependencies](docs/runtime-dependencies.md)
10. [Release Lifecycle](docs/release-lifecycle.md)
11. [Integration Coverage](docs/integration-coverage.md)
12. [Adapter Readiness Checklist](docs/adapter-readiness-checklist.md)

## Validation baseline

The repository continuously validates the complete developer pattern against the pinned OrbitFabric Core baseline.

CI verifies:

```text
Python 3.11 and 3.12
Ruff
Template identity and package consistency
positive and negative adapter tests
Core Integration Package conformance
Core Integration Result conformance
wheel build and packaged assets
strict MkDocs build
isolated Adapter Manager install, verify, execute and remove
exact Adapter Release Descriptor construction
Adapter Project Lock MISSING -> MATCH behavior
repeated install request NOOP behavior
release and lifecycle evidence retention
```

A concrete adapter should add the strongest meaningful downstream-native compatibility control available for its target. Core conformance and downstream acceptance are separate checks.
