from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

import yaml

TEXT_SUFFIXES = {".md", ".py", ".toml", ".json", ".yaml", ".yml", ".sh"}
IGNORED_PARTS = {".git", ".venv", "build", "dist", "generated", "site", "__pycache__"}

TEMPLATE_DISTRIBUTION = "orbitfabric-dummy-adapter"
TEMPLATE_PACKAGE = "orbitfabric_dummy_adapter"
TEMPLATE_ADAPTER_ID = "orbitfabric-dummy"
TEMPLATE_LOCAL_RELEASE_NAME = "dummy-adapter"


def _slug(value: str, *, label: str) -> str:
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", value):
        raise ValueError(f"{label} must use lowercase letters, digits and single hyphens")
    return value


def _python_package(value: str) -> str:
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", value):
        raise ValueError("python package must be one valid Python identifier")
    return value


def _console_script(value: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", value):
        raise ValueError("console script contains unsupported characters")
    return value


def _text_files(root: Path) -> list[Path]:
    template_only_files = {
        Path(__file__).resolve(),
        (root / "tests" / "test_initialize_adapter.py").resolve(),
    }
    result: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix not in TEXT_SUFFIXES:
            continue
        if path.resolve() in template_only_files:
            continue
        if any(part in IGNORED_PARTS for part in path.relative_to(root).parts):
            continue
        result.append(path)
    return sorted(result)


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return payload


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _replace(path: Path, old: str, new: str, *, required: bool = False) -> None:
    text = path.read_text(encoding="utf-8")
    if required and old not in text:
        raise ValueError(f"Expected Template identity not found in {path}: {old}")
    updated = text.replace(old, new)
    if updated != text:
        path.write_text(updated, encoding="utf-8")


def _preflight(root: Path) -> Path:
    package = root / "src" / TEMPLATE_PACKAGE
    if not package.is_dir():
        raise ValueError(
            "Template package was not found. The repository may already be initialized or modified."
        )
    pyproject = root / "pyproject.toml"
    if TEMPLATE_DISTRIBUTION not in pyproject.read_text(encoding="utf-8"):
        raise ValueError(
            "Template distribution identity was not found. Refusing to initialize an unknown state."
        )
    return package


def _update_pyproject(
    root: Path,
    *,
    distribution: str,
    python_package: str,
    console_script: str,
    adapter_name: str,
) -> None:
    path = root / "pyproject.toml"
    text = path.read_text(encoding="utf-8")
    required = (
        f'name = "{TEMPLATE_DISTRIBUTION}"',
        f'{TEMPLATE_DISTRIBUTION} = "{TEMPLATE_PACKAGE}.cli:main"',
        f'packages = ["src/{TEMPLATE_PACKAGE}"]',
    )
    for token in required:
        if token not in text:
            raise ValueError(f"Expected Template pyproject entry is missing: {token}")
    text = text.replace(
        f'name = "{TEMPLATE_DISTRIBUTION}"',
        f'name = "{distribution}"',
    )
    text = text.replace(
        f'{TEMPLATE_DISTRIBUTION} = "{TEMPLATE_PACKAGE}.cli:main"',
        f'{console_script} = "{python_package}.cli:main"',
    )
    text = text.replace(
        f'packages = ["src/{TEMPLATE_PACKAGE}"]',
        f'packages = ["src/{python_package}"]',
    )
    old_description = (
        'description = "Executable dummy adapter shipped with the OrbitFabric '
        'Adapter Developer Template."'
    )
    new_description = (
        f'description = "OrbitFabric adapter for {adapter_name}, initialized from the '
        'Adapter Developer Template."'
    )
    text = text.replace(old_description, new_description)
    path.write_text(text, encoding="utf-8")


def _replace_package_references(root: Path, *, python_package: str) -> None:
    for path in _text_files(root):
        _replace(path, TEMPLATE_PACKAGE, python_package)


def _replace_executable_identity_references(
    root: Path,
    *,
    console_script: str,
    adapter_id: str,
) -> None:
    for path in _text_files(root):
        if path.suffix == ".md":
            continue
        _replace(path, TEMPLATE_DISTRIBUTION, console_script)
        _replace(path, TEMPLATE_ADAPTER_ID, adapter_id)


def _update_manifest(package: Path, *, adapter_id: str, console_script: str) -> None:
    path = package / "integration_package.json"
    payload = _load_json(path)
    payload["adapter"]["id"] = adapter_id
    payload["integration"]["id"] = adapter_id
    payload["execution"]["argv_prefix"] = [console_script]
    _write_json(path, payload)


def _update_constants(package: Path, *, adapter_id: str) -> None:
    path = package / "constants.py"
    _replace(path, TEMPLATE_ADAPTER_ID, adapter_id, required=True)


def _update_profile_schema(package: Path, *, distribution: str, adapter_id: str) -> None:
    schema = package / "schemas" / "profile-0.1.schema.json"
    payload = _load_json(schema)
    payload["$id"] = f"https://example.invalid/{distribution}/profile-0.1.schema.json"
    payload["title"] = f"{adapter_id} Projection Profile"
    payload["properties"]["integration"]["properties"]["id"]["const"] = adapter_id
    _write_json(schema, payload)


def _update_example_profile(root: Path, *, adapter_name: str, adapter_id: str) -> None:
    path = root / "examples" / "profile.yaml"
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("examples/profile.yaml must contain a mapping")
    profile = payload.get("profile")
    integration = payload.get("integration")
    if not isinstance(profile, dict) or not isinstance(integration, dict):
        raise ValueError("examples/profile.yaml is missing profile or integration identity")
    profile["id"] = f"{adapter_name}-example"
    profile["description"] = f"Example Projection Profile for {adapter_id}."
    integration["id"] = adapter_id
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")


def _update_local_proof_name(root: Path, *, adapter_name: str) -> None:
    for rel in (
        ".github/scripts/installed-lifecycle.sh",
        ".github/scripts/release-proof.sh",
        "docs/release-lifecycle.md",
    ):
        path = root / rel
        if path.is_file():
            _replace(path, TEMPLATE_LOCAL_RELEASE_NAME, adapter_name)


def _update_developer_docs(
    root: Path,
    *,
    distribution: str,
    python_package: str,
    console_script: str,
    adapter_id: str,
) -> None:
    wheel_base = distribution.replace("-", "_")
    docs = [root / "README.md", *sorted((root / "docs").glob("*.md"))]
    for path in docs:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        text = text.replace(f"{TEMPLATE_DISTRIBUTION} run", f"{console_script} run")
        text = text.replace(f"dist/{TEMPLATE_PACKAGE}-", f"dist/{wheel_base}-")
        text = text.replace(TEMPLATE_DISTRIBUTION, distribution)
        text = text.replace(TEMPLATE_PACKAGE, python_package)
        text = text.replace(TEMPLATE_ADAPTER_ID, adapter_id)
        path.write_text(text, encoding="utf-8")


def _refresh_manifest_schema_digest(package: Path) -> None:
    manifest_path = package / "integration_package.json"
    manifest = _load_json(manifest_path)
    entries = manifest.get("profile_schemas")
    if not isinstance(entries, list) or len(entries) != 1 or not isinstance(entries[0], dict):
        raise ValueError("Template expects exactly one profile schema entry")
    rel = entries[0].get("path")
    if not isinstance(rel, str) or not rel:
        raise ValueError("Profile schema path is missing from Integration Package Manifest")
    schema = package / rel
    entries[0]["sha256"] = _sha256(schema)
    _write_json(manifest_path, manifest)


def _reset_coverage(root: Path) -> None:
    source = root / "coverage" / "coverage-template.md"
    target = root / "coverage" / "integration-coverage.md"
    target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")


def _assert_executable_template_identity_removed(root: Path) -> None:
    findings: list[str] = []
    for path in _text_files(root):
        if path.suffix == ".md":
            continue
        text = path.read_text(encoding="utf-8")
        for value in (TEMPLATE_DISTRIBUTION, TEMPLATE_PACKAGE, TEMPLATE_ADAPTER_ID):
            if value in text:
                findings.append(f"{path.relative_to(root)} still contains {value}")
    if findings:
        raise ValueError("Unexpected executable Template identity remains:\n" + "\n".join(findings))


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        description="Initialize developer-owned identity in a fresh OrbitFabric Adapter Template."
    )
    result.add_argument("--adapter-name", required=True)
    result.add_argument("--python-package", required=True)
    result.add_argument("--console-script", required=True)
    result.add_argument("--distribution-name")
    result.add_argument("--adapter-id")
    result.add_argument("--root", type=Path, default=Path.cwd(), help=argparse.SUPPRESS)
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    root = args.root.resolve()

    try:
        adapter_name = _slug(args.adapter_name, label="adapter name")
        python_package = _python_package(args.python_package)
        console_script = _console_script(args.console_script)
        distribution = args.distribution_name or f"orbitfabric-{adapter_name}-adapter"
        distribution = _slug(distribution, label="distribution name")
        adapter_id = args.adapter_id or f"orbitfabric-{adapter_name}"
        adapter_id = _slug(adapter_id, label="adapter id")
        old_package = _preflight(root)

        _update_pyproject(
            root,
            distribution=distribution,
            python_package=python_package,
            console_script=console_script,
            adapter_name=adapter_name,
        )
        _replace_package_references(root, python_package=python_package)
        _update_constants(old_package, adapter_id=adapter_id)
        _replace_executable_identity_references(
            root,
            console_script=console_script,
            adapter_id=adapter_id,
        )

        new_package = old_package.with_name(python_package)
        old_package.rename(new_package)

        _update_manifest(new_package, adapter_id=adapter_id, console_script=console_script)
        _update_profile_schema(new_package, distribution=distribution, adapter_id=adapter_id)
        _update_example_profile(root, adapter_name=adapter_name, adapter_id=adapter_id)
        _update_local_proof_name(root, adapter_name=adapter_name)
        _update_developer_docs(
            root,
            distribution=distribution,
            python_package=python_package,
            console_script=console_script,
            adapter_id=adapter_id,
        )
        _refresh_manifest_schema_digest(new_package)
        _reset_coverage(root)
        _assert_executable_template_identity_removed(root)
    except (OSError, ValueError, json.JSONDecodeError, yaml.YAMLError) as exc:
        raise SystemExit(str(exc)) from exc

    print("Adapter developer identity initialized.")
    print(f"Distribution: {distribution}")
    print(f"Python package: {python_package}")
    print(f"Console script: {console_script}")
    print(f"Adapter execution id: {adapter_id}")
    print()
    print("Still required from the maintainer:")
    print("- decide version and release policy")
    print("- choose any official Source Coordinate and publisher identity")
    print("- replace Dummy projection semantics and examples")
    print("- declare actual supported Core surfaces and target compatibility")
    print("- complete the Integration Coverage Matrix")
    print("- review authorship, description and documentation for the real adapter")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
