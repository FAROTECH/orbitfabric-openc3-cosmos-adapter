# Runtime Dependencies

Unlike a pure file-to-file adapter, the initial COSMOS verification projector intentionally uses the OrbitFabric Scenario loader at runtime so that Scenario semantics are interpreted by the Core implementation that owns them.

The Python package therefore declares the exact current OrbitFabric Core development baseline as a runtime dependency while the adapter contract remains candidate-level.

OpenC3 COSMOS itself is not imported by the adapter during projection. The adapter generates COSMOS-native artifacts; downstream execution remains target-owned.
