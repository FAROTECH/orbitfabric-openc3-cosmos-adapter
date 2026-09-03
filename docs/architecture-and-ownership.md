# Architecture and Ownership

```text
OrbitFabric Core
    -> Integration Input Set
    -> Scenario operation input

Projection Profile
    -> COSMOS binding and observation policy

OpenC3 COSMOS adapter
    -> validate inputs
    -> project Scenario semantics
    -> retain explicit non-projection / blocked accounting
    -> materialize COSMOS-native procedure and suite
    -> emit Core-conformant Integration Result

OpenC3 COSMOS
    -> parse / load / execute generated target artifacts
    -> produce downstream runtime evidence
```

The target-owned Verification Projection Plan is an adapter artifact, not a new Core contract.

Scenario time remains provenance/order unless a target policy explicitly maps it. The adapter does not infer real waits from Scenario `t` values.
