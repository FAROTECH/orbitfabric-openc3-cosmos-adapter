# Integration Coverage

Integration coverage describes what an adapter intends to integrate toward a target and how completely it does so.

It is not a measure of how many features of the downstream product OrbitFabric controls.

A large target may expose hundreds of capabilities that are unrelated to OrbitFabric. Those capabilities do not belong in the denominator merely because they exist.

## The three surfaces

Use three distinct surfaces:

```text
OrbitFabric Semantic Surface
        -> Target Applicable Surface
        -> Adapter Declared Scope
```

### OrbitFabric Semantic Surface

This is the set of semantics OrbitFabric can express through its current contracts and integration surfaces.

The Template does not define this surface. OrbitFabric Core remains authoritative.

### Target Applicable Surface

This is the subset of OrbitFabric semantics that makes sense for the role of the downstream target.

Applicability is architectural, not numerical.

For example, a flight software framework may have meaningful representations for telemetry, commands and events while some ground scheduling concepts are outside its role. Those ground concepts can be `NOT_APPLICABLE` without making the flight software adapter incomplete.

For each applicable area, identify the target representation or target limitation explicitly.

### Adapter Declared Scope

This is what one specific adapter promises to implement.

A focused adapter may deliberately declare only one small applicable capability. That is valid when the purpose is explicit.

This gives two different questions:

```text
How completely does the adapter implement what it promises?
    -> Scope Completeness

How broadly does the adapter cover the OrbitFabric surface applicable to the target?
    -> Applicable Surface Coverage
```

Do not confuse them.

## Recommended dispositions

### FULL

The intended mapping is implemented within the declared scope, no known semantic gap remains for that capability area, and supporting evidence exists.

### PARTIAL

A mapping exists but a known semantic gap, unsupported variant or incomplete projection remains.

### NOT_IMPLEMENTED

The capability is applicable, is inside declared scope and has a meaningful target representation, but implementation is still absent.

### TARGET_UNSUPPORTED

The OrbitFabric concept is relevant to the target role, but the target does not provide an adequate representation for the required semantics.

Use this only after compatibility analysis. It must not become a substitute for `NOT_IMPLEMENTED`.

### OUT_OF_SCOPE

The capability is applicable and could be mapped, but this particular adapter deliberately does not claim it.

This is especially useful for small community adapters with intentionally focused goals.

### NOT_APPLICABLE

The OrbitFabric concept does not belong to the role represented by this target.

### NOT_ANALYZED

Applicability or target representation is still unresolved.

This is an analysis gap. Do not silently convert it into `TARGET_UNSUPPORTED`, `OUT_OF_SCOPE` or `NOT_APPLICABLE`.

## A practical workflow

Start from OrbitFabric concepts, not from the complete feature list of the downstream product.

```text
1. identify candidate OrbitFabric capability areas
2. decide whether each area is applicable to the target role
3. identify the target representation or limitation
4. declare what this adapter intends to cover
5. assign a disposition
6. link tests, generated evidence or rationale
7. turn remaining gaps into an explicit roadmap
```

The reusable matrix is:

```text
coverage/coverage-template.md
```

The completed Dummy example is:

```text
coverage/integration-coverage.md
```

## Reading completeness

Prefer counts and dispositions over a single maturity percentage.

Three useful views are:

### Analysis Coverage

How much of the candidate OrbitFabric surface has been explicitly classified.

For an OrbitFabric-maintained general-purpose adapter, `NOT_ANALYZED` should reach zero before a mature release is considered.

### Scope Completeness

How completely the adapter implements the capability areas it explicitly declares in scope.

A small community adapter can legitimately reach full Scope Completeness while covering only a small part of the Target Applicable Surface.

### Applicable Surface Coverage

How broadly the adapter covers the OrbitFabric semantics that are applicable to the downstream target.

This is the important breadth measure for OrbitFabric-maintained general-purpose adapters.

## Community adapters

Community authors are free to define a narrow purpose.

Publishing an Integration Coverage Matrix is recommended because it tells users exactly what the adapter promises. It is not a generic Core conformance requirement.

A telemetry-only adapter can therefore be complete within its declared purpose without pretending to be a complete integration for the entire target.

## OrbitFabric-maintained adapters

OrbitFabric project policy is intentionally stricter for adapters maintained as official OrbitFabric integrations.

Before maturity and version decisions, they should:

- publish an explicit coverage matrix;
- analyze the full Target Applicable Surface;
- drive `NOT_ANALYZED` to zero;
- drive projectable in-scope `NOT_IMPLEMENTED` gaps toward zero;
- close or explicitly justify `PARTIAL` mappings;
- support `TARGET_UNSUPPORTED` conclusions with target compatibility evidence;
- make deliberate `OUT_OF_SCOPE` decisions visible rather than implicit.

A conceptually complete OrbitFabric-maintained adapter does not need to implement unrelated features of the downstream product. It does need an explicit disposition for the OrbitFabric semantics applicable to that target, and all projectable semantics inside the intended general-purpose scope should be implemented.

## Coverage representation

The Template uses Markdown for Integration Coverage:

```text
coverage/coverage-template.md
coverage/integration-coverage.md
```

There is currently no generic Core-owned `adapter-coverage.yaml` contract. Do not invent a local machine-readable format and present it as OrbitFabric semantics.

If OrbitFabric Core later promotes a machine-readable coverage contract, that Core-owned contract becomes authoritative and the Template should consume it rather than maintain a competing definition.
