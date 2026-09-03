# Adapter Readiness Checklist

This checklist separates stable source acceptance from immutable publication.

## A. Stable source identity

- [x] repository / distribution / package identity fixed;
- [x] adapter and integration ids fixed;
- [x] declared initial operation surface fixed;
- [x] source version set to `0.1.0`;
- [x] logical key set to `orbitfabric/openc3-cosmos`;
- [x] Source Coordinate frozen as `github.com/FAROTECH:orbitfabric/openc3-cosmos`.

## B. Product scope

- [x] 21 / 21 semantic areas analyzed;
- [x] no `NOT_IMPLEMENTED` gap inside declared initial scope;
- [x] `PARTIAL` and `TARGET_UNSUPPORTED` dispositions documented;
- [x] out-of-scope semantic breadth explicitly preserved as non-blocking.

## C. Product surface

- [x] consumer-first Getting Started;
- [x] CI-backed Scenario Verification Projection product example;
- [x] Developer / Contributor path;
- [x] Maintainer / Publisher path;
- [x] Integration Coverage matrix visible from the repository landing page.

## D. Permanent source evidence

Require green on the exact accepted stable main commit:

- [ ] Python 3.11 checks;
- [ ] Python 3.12 checks;
- [ ] Ruff;
- [ ] adapter consistency and product hygiene;
- [ ] unit and negative tests;
- [ ] wheel/package validation;
- [ ] strict MkDocs build;
- [ ] exact OpenC3 COSMOS source/API compatibility;
- [ ] installed Adapter Manager lifecycle;
- [ ] consumer product example;
- [ ] provider-neutral release proof.

PR CI proves a candidate merge result. The release gate is the exact accepted main source commit, not a synthetic pull-request merge ref.

## E. Exact-source native acceptance

Before tagging:

- [ ] run `tools/run_native_cosmos_acceptance.sh` from the exact accepted stable main commit;
- [ ] require native OpenC3 COSMOS `v7.3.0`;
- [ ] require `cosmos-project` `9eb454f06fe0113d05aa6945d88b627155a2aa47`;
- [ ] require external OFDEMO command and telemetry events;
- [ ] require native Script Runner completion;
- [ ] require CTRF tests 1 / passed 1 / failed 0;
- [ ] retain adapter source commit, wheel digest and target baseline provenance.

A previous candidate PASS is supporting evidence but does not satisfy this exact-source gate.

## F. Tag and definitive release construction

Only after sections D and E are complete:

- [ ] create exact `v0.1.0` tag on the accepted stable commit;
- [ ] build definitive `orbitfabric_openc3_cosmos_adapter-0.1.0-py3-none-any.whl`;
- [ ] build release-only `adapter-release.json` with the frozen Source Coordinate;
- [ ] build `SHA256SUMS`;
- [ ] verify descriptor and digests locally.

## G. Publication and external acceptance

- [ ] decide and prepare repository visibility / publication provider;
- [ ] create verified draft release;
- [ ] attach only definitive publisher release membership;
- [ ] verify uploaded/downloaded asset digests;
- [ ] publish under immutable-release policy;
- [ ] verify tag points to the accepted stable commit;
- [ ] external greenfield install through Adapter Manager from published bytes;
- [ ] run the consumer product example from the published adapter;
- [ ] repeat native acceptance as required by the release claim;
- [ ] retain final Architecture Lab publication evidence.

The repository is currently private. Public greenfield acceptance requires an explicit visibility decision before publication.
