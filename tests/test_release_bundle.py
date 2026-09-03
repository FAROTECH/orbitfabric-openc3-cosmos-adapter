from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

from orbitfabric.adapter_manager import ProjectLockService
from orbitfabric.conformance.adapter_release import load_release_descriptor


def test_release_bundle_builder_produces_core_conformant_exact_identity(tmp_path: Path) -> None:
    wheel = tmp_path / "dummy-adapter.whl"
    wheel.write_bytes(b"exact-template-wheel-bytes")
    output = tmp_path / "release"

    subprocess.run(
        [
            sys.executable,
            "tools/build_release_bundle.py",
            "--wheel",
            str(wheel),
            "--authority",
            "template.local",
            "--publisher",
            "orbitfabric",
            "--name",
            "dummy-adapter",
            "--output-dir",
            str(output),
        ],
        check=True,
    )

    descriptor_path = output / "adapter-release.json"
    lock_path = output / "adapter-project-lock.json"
    sums_path = output / "SHA256SUMS"

    descriptor = load_release_descriptor(descriptor_path)
    lock = ProjectLockService().load(lock_path)

    wheel_sha = hashlib.sha256(wheel.read_bytes()).hexdigest()
    descriptor_sha = hashlib.sha256(descriptor_path.read_bytes()).hexdigest()

    assert descriptor["source_coordinate"] == {
        "authority": "template.local",
        "publisher": "orbitfabric",
        "name": "dummy-adapter",
    }
    assert descriptor["artifacts"][0]["sha256"] == wheel_sha
    assert lock.adapters[0].release_descriptor.sha256 == descriptor_sha
    assert lock.adapters[0].artifact.sha256 == wheel_sha
    assert lock.adapters[0].installation_backend.id == "python-wheel-managed-env"

    sums = sums_path.read_text(encoding="utf-8")
    assert wheel_sha in sums
    assert descriptor_sha in sums


def test_release_only_builder_omits_project_lock_and_sums_publisher_assets(
    tmp_path: Path,
) -> None:
    wheel = tmp_path / "dummy-adapter.whl"
    wheel.write_bytes(b"publisher-release-wheel")
    output = tmp_path / "release"

    subprocess.run(
        [
            sys.executable,
            "tools/build_release_bundle.py",
            "--wheel",
            str(wheel),
            "--authority",
            "release.example",
            "--publisher",
            "orbitfabric",
            "--name",
            "dummy-adapter",
            "--release-only",
            "--output-dir",
            str(output),
        ],
        check=True,
    )

    descriptor_path = output / "adapter-release.json"
    sums_path = output / "SHA256SUMS"

    descriptor = load_release_descriptor(descriptor_path)
    wheel_sha = hashlib.sha256(wheel.read_bytes()).hexdigest()
    descriptor_sha = hashlib.sha256(descriptor_path.read_bytes()).hexdigest()

    assert descriptor["source_coordinate"] == {
        "authority": "release.example",
        "publisher": "orbitfabric",
        "name": "dummy-adapter",
    }
    assert not (output / "adapter-project-lock.json").exists()
    assert sums_path.read_text(encoding="utf-8").splitlines() == [
        f"{wheel_sha}  {wheel.name}",
        f"{descriptor_sha}  {descriptor_path.name}",
    ]


def test_release_bundle_builder_rejects_missing_artifact(tmp_path: Path) -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "tools/build_release_bundle.py",
            "--wheel",
            str(tmp_path / "missing.whl"),
            "--authority",
            "template.local",
            "--publisher",
            "orbitfabric",
            "--name",
            "dummy-adapter",
            "--output-dir",
            str(tmp_path / "release"),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode != 0
    assert "Wheel does not exist" in completed.stderr


def test_release_bundle_is_json_serializable(tmp_path: Path) -> None:
    wheel = tmp_path / "dummy.whl"
    wheel.write_bytes(b"wheel")
    output = tmp_path / "release"

    subprocess.run(
        [
            sys.executable,
            "tools/build_release_bundle.py",
            "--wheel",
            str(wheel),
            "--authority",
            "template.local",
            "--publisher",
            "orbitfabric",
            "--name",
            "dummy-adapter",
            "--output-dir",
            str(output),
        ],
        check=True,
    )

    json.loads((output / "adapter-release.json").read_text(encoding="utf-8"))
    json.loads((output / "adapter-project-lock.json").read_text(encoding="utf-8"))
