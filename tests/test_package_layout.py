from __future__ import annotations

from importlib.resources import files


def test_package_owns_required_contract_assets() -> None:
    package = files("orbitfabric_openc3_cosmos_adapter")

    assert package.joinpath("integration_package.json").is_file()
    assert package.joinpath("schemas/profile-0.1.schema.json").is_file()
    assert package.joinpath("schemas/verification-projection-plan-0.1.schema.json").is_file()
