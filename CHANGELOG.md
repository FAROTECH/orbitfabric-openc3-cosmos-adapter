# Changelog

## Unreleased

### Added

- Executable OrbitFabric Adapter Developer Template.
- Namespaced Dummy Adapter package with packaged Integration Package Manifest.
- Dummy `project` operation for telemetry identity projection.
- Dummy `verification_projection` operation with required Scenario input.
- Core conformance tests for Integration Package Manifest and Integration Result.
- Developer-first documentation for repository anatomy, identity, projection, evidence, testing, release lifecycle and Integration Coverage.
- Adapter identity initializer with separate distribution, package, console script and execution identities.
- Identity-agnostic Template consistency checks.
- Positive and negative adapter tests.
- Explicit traceability for intentionally non-projected bindings.
- Isolated installed lifecycle proof using a real Core-produced Integration Input Set and Adapter Manager managed environment.
- Provider-neutral release bundle builder for exact Adapter Release Descriptor and Adapter Project Lock construction.
- Release proof covering MISSING, exact install from lock, MATCH, repeated NOOP and final removal.
- Reusable Integration Coverage method with explicit target representation, declared scope and disposition.
- Adapter Readiness Checklist for concrete adapter maintainers.
- Strict MkDocs documentation build.

### Compatibility

This repository is a developer pattern, not a normative replacement for OrbitFabric Core contracts.

Publication provider selection remains separate from release identity and release construction.

Integration Coverage remains recommended documentation for community adapters and is not a generic Core conformance requirement.
