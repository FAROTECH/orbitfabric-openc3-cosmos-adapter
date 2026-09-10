# Evidence and Traceability

Each execution retains:

```text
Core Input Set identity and digest
Scenario identity and digest
Projection Profile identity and digest
resolved COSMOS operations
source-to-target mapping records
generated artifact digests
explicit non-projected and blocked Scenario atoms

Successful projections additionally emit the generic Result-owned
`orbitfabric.scenario_projection_accounting` `0.1-candidate` artifact. It
contains complete exact-atom accounting using producer-owned disposition,
reason and parent-local mapping ids. The COSMOS Verification Projection Plan
remains the target-specific authority used to construct those claims.
```

The Core-owned Integration Result is the primary adapter execution evidence surface.

OpenC3 COSMOS runtime evidence, including CTRF when available, is downstream evidence and remains separate from the generic Integration Result contract.
