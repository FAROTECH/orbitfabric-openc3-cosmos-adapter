from __future__ import annotations

from importlib.resources import files


def test_namespaced_package_owns_manifest_and_profile_schema() -> None:
    package = files("orbitfabric_dummy_adapter")

    assert package.joinpath("integration_package.json").is_file()
    assert package.joinpath("schemas/profile-0.1.schema.json").is_file()
