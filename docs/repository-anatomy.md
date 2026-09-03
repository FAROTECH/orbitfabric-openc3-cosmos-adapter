# Repository Anatomy

This page maps the responsibilities expected in a well-structured OrbitFabric adapter repository to the concrete files in this Template.

The goal is not to force every community adapter to implement the same breadth. The goal is to make repository responsibilities explicit and reviewable.

## Identity

Purpose:

```text
say which adapter this is
separate execution identity from release-source identity
make version ownership deliberate
```

Template locations:

```text
pyproject.toml
src/orbitfabric_dummy_adapter/integration_package.json
docs/adapter-identity.md
tools/build_release_bundle.py
tools/check_template_consistency.py
```

A real adapter must deliberately choose its distribution name, package namespace, console script, `adapter.id`, `integration.id`, release version and Source Coordinate.

## Packaging

Purpose:

```text
build an installable artifact
retain the Integration Package Manifest inside the distribution
construct exact release identity
```

Template locations:

```text
pyproject.toml
src/orbitfabric_dummy_adapter/integration_package.json
tools/build_release_bundle.py
.github/workflows/ci.yml
```

The Python backend requires exactly one `integration_package.json` owned by the installed distribution. That discovery behavior is backend-specific. The manifest contents remain Core-owned.

## Integration contract

Purpose:

```text
declare supported Core input surfaces
expose promoted adapter execution protocol
declare operations and operation inputs
emit Core-conformant Integration Results
```

Template locations:

```text
src/orbitfabric_dummy_adapter/integration_package.json
src/orbitfabric_dummy_adapter/cli.py
src/orbitfabric_dummy_adapter/result.py
tests/test_contracts.py
tests/test_project.py
tests/test_verification.py
```

Core owns the generic contract. A concrete adapter owns only its declared compatibility and target-specific behavior.

## Projection

Purpose:

```text
describe target-specific choices
bind OrbitFabric source entities to target intent
project those bindings into target artifacts
```

Template locations:

```text
src/orbitfabric_dummy_adapter/schemas/profile-0.1.schema.json
examples/profile.yaml
src/orbitfabric_dummy_adapter/profile.py
src/orbitfabric_dummy_adapter/projection.py
```

See [Projection Profile and Bindings](projection-profile-and-bindings.md).

## Implementation

Purpose:

```text
load declared inputs
validate adapter-owned constraints
perform target projection
write artifacts
emit Integration Result
fail closed when required semantics are unavailable
```

Template locations:

```text
src/orbitfabric_dummy_adapter/cli.py
src/orbitfabric_dummy_adapter/input_set.py
src/orbitfabric_dummy_adapter/profile.py
src/orbitfabric_dummy_adapter/projection.py
src/orbitfabric_dummy_adapter/result.py
src/orbitfabric_dummy_adapter/io.py
```

When adapting this repository, keep Core contract interpretation separate from target-specific mapping logic.

## Conformance

Purpose:

```text
prove valid paths
prove invalid paths fail closed
validate Core-owned contracts
validate packaged behavior
validate installed behavior
validate target compatibility when a real target exists
```

Template locations:

```text
tests/
tests/compatibility/README.md
.github/scripts/installed-lifecycle.sh
.github/scripts/release-proof.sh
.github/workflows/ci.yml
```

The Dummy target has no external native validator, so real target-native compatibility is intentionally not simulated. The reserved compatibility area explains what a concrete adapter should add. Concrete adapters must use the strongest meaningful downstream validation available.

## Evidence

Purpose:

```text
retain what was consumed
retain what was projected
retain artifact byte identity
retain mapping and operation-input provenance
retain release and lifecycle proof
```

Template locations:

```text
integration_result.json produced by each execution
.github/scripts/installed-lifecycle.sh
.github/scripts/release-proof.sh
GitHub Actions evidence artifacts
```

See [Evidence and Traceability](evidence-and-traceability.md).

## Developer experience

Purpose:

```text
make the adapter understandable without historical project context
show what to change
show how to run locally
show how to debug contract, package and lifecycle failures
keep identity and package metadata consistent while renaming
```

Template locations:

```text
README.md
docs/
examples/
CONTRIBUTING.md
tools/check_template_consistency.py
```

## Automation

Purpose:

```text
lint
unit and negative tests
Core conformance
wheel build
package asset verification
documentation build
isolated installed lifecycle
release construction
Project Lock proof
evidence retention
```

Template locations:

```text
.github/workflows/ci.yml
.github/scripts/installed-lifecycle.sh
.github/scripts/release-proof.sh
tools/build_release_bundle.py
```

Publication is intentionally separate. GitHub Releases, PyPI or a future OrbitFabric registry can transport an already identified release without redefining Core release identity.

## Readiness rule for a concrete adapter

A repository is not complete merely because one projection path works.

For a general-purpose OrbitFabric-maintained adapter, review all nine areas above and also publish an Integration Coverage Matrix that answers:

```text
what OrbitFabric semantics are applicable to this target?
what target representation exists for each applicable area?
what does this adapter declare in scope?
what is FULL, PARTIAL, NOT_IMPLEMENTED or otherwise dispositioned?
what evidence supports each conclusion?
```

A focused community adapter may declare a much smaller scope. Its documentation should still make that scope explicit.

Use the [Adapter Readiness Checklist](adapter-readiness-checklist.md) before deciding that a concrete adapter is ready for reuse or release.
