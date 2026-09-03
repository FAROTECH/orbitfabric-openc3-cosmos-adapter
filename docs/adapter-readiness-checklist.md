# Adapter Readiness Checklist

Use this checklist before calling a concrete OrbitFabric adapter ready for reuse or release.

It does not replace OrbitFabric Core conformance. It helps a maintainer verify that the adapter repository covers the responsibilities expected from a well-structured integration product.

## 1. Identity

Confirm that the repository deliberately separates and documents:

```text
Python distribution identity
Python package namespace
console script identity
adapter.id
integration.id
Adapter Source Coordinate
release version identity
```

Useful Template support:

```text
tools/initialize_adapter.py
docs/adapter-identity.md
tools/check_template_consistency.py
```

Do not treat initialization as a decision about official publisher identity, official Source Coordinate, release maturity, target compatibility or coverage claims.

## 2. Packaging

Confirm that:

```text
the adapter builds an installable artifact
the artifact owns exactly one integration_package.json
target-specific Profile schemas are packaged
the console entry point resolves from the installed distribution
runtime dependencies are declared explicitly
```

For the Python backend demonstrated by this Template, the Integration Package Manifest lives inside the namespaced adapter package and is discovered from the installed distribution.

## 3. Integration contract

Confirm that the adapter deliberately declares and implements:

```text
supported Core input surfaces
Integration Package Manifest
orbitfabric.adapter_cli.v1
supported operations
operation-input requirements
Core-conformant Integration Result
```

Core remains normative for generic contract semantics.

## 4. Projection

Confirm that target-specific projection is explicit and reviewable:

```text
Projection Profile schema
Profile example
source bindings
target-specific settings
target representation
mapping traceability
intentional non-projection behavior
```

Do not copy the Dummy target vocabulary into a real adapter unless it genuinely represents the downstream target.

## 5. Implementation

Confirm that implementation responsibilities are separated clearly enough to review:

```text
input-set loading and integrity checks
Profile loading and validation
CLI contract handling
operation-input validation
target projection
artifact generation
Integration Result construction
I/O and hashing
```

A concrete adapter may organize code differently, but Core contract interpretation and target-specific mapping logic should remain conceptually distinct.

## 6. Conformance and compatibility

Confirm that the repository contains appropriate positive and negative controls:

```text
successful operation tests
invalid input and binding tests
Core contract conformance
package-layout checks
installed lifecycle proof
release and Project Lock proof
target-native compatibility tests
fail-closed behavior
```

Use the strongest meaningful downstream-native validation available. A compiler, parser, simulator, schema validator, project build or runtime smoke can provide evidence that generic Core conformance cannot.

## 7. Evidence and traceability

Confirm that an execution retains enough information to answer:

```text
what Core input was consumed?
what Profile was used?
what operation inputs were used?
what target artifacts were generated?
what exact bytes were produced?
which source concepts map to which target elements?
what was intentionally not projected?
```

Use the Core-owned Integration Result as the primary execution evidence surface. Keep release evidence and target-native evidence as separate layers when they answer different questions.

## 8. Developer experience

Confirm that a developer with no project history can understand:

```text
what the adapter does
what it intentionally does not do
which files they normally change
how to run safe local checks
how to build the package
how to debug failures by layer
how to construct release identity
how to declare integration coverage
```

Recommended entry points:

```text
README.md
docs/getting-started.md
docs/repository-anatomy.md
docs/adapter-identity.md
docs/projection-profile-and-bindings.md
docs/testing-and-conformance.md
docs/evidence-and-traceability.md
docs/release-lifecycle.md
docs/integration-coverage.md
examples/
```

## 9. Automation

Confirm that CI verifies the parts of the lifecycle that should not depend on a maintainer running them manually:

```text
lint
unit and negative tests
Core conformance
wheel build
packaged-asset verification
strict documentation build
isolated installed lifecycle
release construction
Project Lock proof
evidence retention
```

Keep release construction separate from publication. GitHub Releases, PyPI or another provider may transport already identified release bytes without redefining OrbitFabric release identity.

## Integration Coverage

For a reusable adapter, analyze:

```text
OrbitFabric Semantic Surface
    -> Target Applicable Surface
    -> Adapter Declared Scope
```

Then record explicit dispositions such as:

```text
FULL
PARTIAL
NOT_IMPLEMENTED
TARGET_UNSUPPORTED
NOT_APPLICABLE
NOT_ANALYZED
OUT_OF_SCOPE
```

A focused community adapter may intentionally declare a narrow scope. An OrbitFabric-maintained general-purpose adapter should analyze the full Target Applicable Surface before a maturity or version decision.

## Readiness conclusion

A successful projection is necessary, but it is not enough by itself to establish adapter maturity.

Before release, review all nine responsibility areas, target compatibility, declared scope and Integration Coverage. The resulting version should reflect the actual maturity of that concrete adapter rather than the age of the repository or the amount of exploratory work that preceded it.
