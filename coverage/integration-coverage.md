# Dummy Adapter Integration Coverage

Status: template example.

The Dummy Target is intentionally small. This matrix demonstrates that declared scope and total applicable surface are different dimensions.

The Dummy Target exists only to teach the adapter pattern. Its target representations are synthetic and are not OrbitFabric contracts.

| OrbitFabric capability area | Target applicable | Target representation or constraint | Adapter declared scope | Disposition | Evidence or rationale | Roadmap |
| --- | --- | --- | --- | --- | --- | --- |
| Telemetry entity identity | yes | `dummy.telemetry` item with source and target identity | in scope | FULL | `project` positive test and T4 installed lifecycle | complete |
| Telemetry scalar type | yes | Dummy telemetry item could carry a scalar type | out of scope | OUT_OF_SCOPE | deliberate narrow Dummy purpose | none |
| Telemetry engineering unit | yes | Dummy telemetry item could carry an engineering unit | out of scope | OUT_OF_SCOPE | deliberate narrow Dummy purpose | none |
| Scenario identity and provenance | yes | `dummy.verification_plan` with Scenario identity plus Integration Result input provenance | in scope | FULL | `verification_projection` tests and T4 real Core Scenario proof | complete |
| Commands | no | Dummy Target has no command model | out of scope | NOT_APPLICABLE | target role definition | none |
| Events | no | Dummy Target has no event model | out of scope | NOT_APPLICABLE | target role definition | none |
| Faults | no | Dummy Target has no fault model | out of scope | NOT_APPLICABLE | target role definition | none |
| Modes | no | Dummy Target has no mode model | out of scope | NOT_APPLICABLE | target role definition | none |
| Packets | no | Dummy Target has no packet model | out of scope | NOT_APPLICABLE | target role definition | none |

## Summary

```text
Total rows:                 9
Analyzed rows:              9
NOT_ANALYZED:               0

Target applicable rows:     4
Target unsupported rows:    0

Declared in-scope rows:     2
FULL:                       2
PARTIAL:                    0
NOT_IMPLEMENTED:            0

Applicable but OUT_OF_SCOPE: 2
NOT_APPLICABLE:               5
```

Interpretation:

```text
Analysis Coverage
    all candidate rows are classified

Scope Completeness
    2 FULL / 2 declared in scope

Applicable Surface Coverage
    2 FULL capability areas out of 4 applicable areas
    with 2 additional applicable areas deliberately OUT_OF_SCOPE
```

The example does not collapse these results into one maturity percentage.

The Dummy Adapter is complete within its intentionally narrow declared scope. It does not claim complete coverage of every capability that could be represented by the Dummy Target.
