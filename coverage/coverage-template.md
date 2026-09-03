# Adapter Integration Coverage Matrix

Status: maintainer declaration.

This file is a recommended starting point for documenting what an OrbitFabric adapter intends to integrate and how completely it does so.

It is not a Core conformance contract.

## Adapter intent

Describe the adapter in one or two sentences.

```text
Target:
Adapter purpose:
Declared scope:
```

A narrow declared scope is valid. Do not claim coverage that the adapter does not intend to provide.

## Coverage model

```text
OrbitFabric Semantic Surface
    -> Target Applicable Surface
    -> Adapter Declared Scope
```

The denominator is not the complete feature set of the downstream product.

The question is:

> Of the OrbitFabric semantics that are applicable and meaningfully projectable toward this target, what does this adapter declare and implement?

## Matrix

| OrbitFabric capability area | Target applicable | Target representation or constraint | Adapter declared scope | Disposition | Evidence or rationale | Roadmap |
| --- | --- | --- | --- | --- | --- | --- |
| Example capability | yes | Target construct or API | in scope | FULL | Test or generated evidence | complete |
| Example capability | yes | Target construct or API | in scope | PARTIAL | Known semantic gap | close gap |
| Example capability | yes | Target construct or API | in scope | NOT_IMPLEMENTED | Mapping is possible but absent | planned |
| Example capability | yes | No adequate target representation | in scope | TARGET_UNSUPPORTED | Compatibility analysis | none unless target evolves |
| Example capability | yes | Target construct or API | out of scope | OUT_OF_SCOPE | Deliberate adapter purpose | none |
| Example capability | no | Outside target role | out of scope | NOT_APPLICABLE | Applicability analysis | none |
| Example capability | unknown | Not assessed yet | undecided | NOT_ANALYZED | Analysis pending | investigate |

Remove the example rows when adapting this file to a real target.

## Disposition meanings

### FULL

The adapter implements the intended mapping for this capability area without a known semantic gap inside its declared scope, and the mapping has supporting evidence.

### PARTIAL

The adapter implements part of the intended mapping, but a known semantic gap, unsupported variant or incomplete projection remains.

### NOT_IMPLEMENTED

The capability is applicable, is inside the adapter declared scope, and has a meaningful target representation, but the adapter does not implement it yet.

### TARGET_UNSUPPORTED

The OrbitFabric concept is relevant to the target role, but the current target does not provide an adequate representation for the required semantics.

This disposition should be supported by compatibility analysis. It is not a substitute for work that has simply not been implemented.

### OUT_OF_SCOPE

The capability is applicable and could be mapped, but this adapter deliberately does not claim it as part of its purpose.

This is a legitimate disposition for focused adapters.

### NOT_APPLICABLE

The OrbitFabric concept does not belong to the role represented by this downstream target.

For example, a flight software adapter does not automatically need to own every ground scheduling concept merely because OrbitFabric can model it.

### NOT_ANALYZED

Applicability or target representation has not yet been assessed.

This is an analysis gap and should not silently be treated as unsupported or out of scope.

## Summary

Prefer counts and explicit dispositions over a single maturity percentage.

```text
Total rows:
Analyzed rows:
NOT_ANALYZED:

Target applicable rows:
Target unsupported rows:

Declared in-scope rows:
FULL:
PARTIAL:
NOT_IMPLEMENTED:

Applicable but OUT_OF_SCOPE:
NOT_APPLICABLE:
```

Useful interpretations:

```text
Analysis Coverage
    how much of the candidate OrbitFabric surface has been classified

Scope Completeness
    how completely the adapter implements what it explicitly promises

Applicable Surface Coverage
    how broadly the adapter covers the OrbitFabric surface applicable to this target
```

These are different questions. Do not collapse them into one number when that would hide meaningful gaps.

## Policy note

For community adapters, publishing this matrix is recommended, not required by generic Core conformance.

For OrbitFabric-maintained adapters, project policy requires an explicit matrix before maturity and version decisions are made.
