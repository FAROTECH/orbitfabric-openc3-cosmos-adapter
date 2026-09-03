from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from orbitfabric import __version__ as orbitfabric_version
from orbitfabric.model.scenario_loader import ScenarioLoader

from orbitfabric_openc3_cosmos_adapter import __version__ as adapter_version

from .core_input import CoreInputSet, load_core_input_set
from .io import sha256_file
from .profile import (
    INTEGRATION_ID,
    INTEGRATION_SCHEMA_VERSION,
    ProjectionBinding,
    ProjectionProfile,
    load_projection_profile,
)

PLAN_KIND = "orbitfabric.openc3_cosmos.verification_projection_plan"
PLAN_VERSION = "0.1-candidate"
COSMOS_BASELINE = "v7.3.0"


NOT_PROJECTED_REASONS = {
    "initial_mode": (
        "Initial mode is Core host-side Scenario state; no COSMOS initialization or "
        "observation policy is defined in the initial adapter scope."
    ),
    "initial_telemetry": (
        "Initial telemetry is Core host-side Scenario state; the initial adapter scope "
        "does not project target initialization."
    ),
    "telemetry_injection": (
        "Core telemetry injection has no target injection semantic in the initial "
        "OpenC3 COSMOS adapter scope."
    ),
    "expect_mode": (
        "No explicit Core mode to OpenC3 COSMOS observation binding is defined in the "
        "initial adapter scope."
    ),
    "expect_event": (
        "No explicit Core event to OpenC3 COSMOS observation binding is defined in the "
        "initial adapter scope."
    ),
    "expect_command": (
        "Core host-side command dispatch history is not treated as OpenC3 COSMOS "
        "runtime evidence."
    ),
    "expect_command_status": (
        "Core CommandRouter status is not equivalent to OpenC3 COSMOS command "
        "invocation or target acknowledgement."
    ),
    "expect_payload_lifecycle": (
        "No explicit payload lifecycle observability contract is defined for OpenC3 COSMOS."
    ),
    "expect_data_flow": (
        "OrbitFabric data-flow expectation is host-side Mission Data Contract evidence, "
        "not OpenC3 COSMOS runtime evidence."
    ),
    "expect_scenario_status": (
        "OrbitFabric scenario_status is aggregate Core host-side state, not a target "
        "runtime observation."
    ),
}

KNOWN_EXPECT_KEYS = {
    "command_status": "expect_command_status",
    "payload_lifecycle": "expect_payload_lifecycle",
    "data_flow": "expect_data_flow",
    "scenario_status": "expect_scenario_status",
}


@dataclass
class PlanBuilder:
    atoms: list[dict[str, Any]] = field(default_factory=list)
    operations: list[dict[str, Any]] = field(default_factory=list)
    diagnostics: list[dict[str, Any]] = field(default_factory=list)

    def add_atom(
        self,
        *,
        kind: str,
        role: str,
        step_index: int | None,
        scenario_t: int | float | None,
        disposition: str,
        source: dict[str, str] | None,
        binding_id: str | None = None,
        reason: str | None = None,
        source_value: Any = None,
    ) -> dict[str, Any]:
        atom = {
            "id": f"atom-{len(self.atoms) + 1:04d}",
            "kind": kind,
            "role": role,
            "step_index": step_index,
            "scenario_t": scenario_t,
            "disposition": disposition,
            "source": source,
            "binding_id": binding_id,
            "operation_ids": [],
            "reason": reason,
            "source_value": source_value,
        }
        self.atoms.append(atom)
        return atom

    def add_operation(
        self,
        atom: dict[str, Any],
        *,
        operation: str,
        binding_id: str,
        origin: str,
        resolved: dict[str, Any],
    ) -> dict[str, Any]:
        record = {
            "id": f"op-{len(self.operations) + 1:04d}",
            "order": len(self.operations),
            "operation": operation,
            "source_atom_id": atom["id"],
            "binding_id": binding_id,
            "origin": origin,
            "resolved": resolved,
        }
        self.operations.append(record)
        atom["operation_ids"].append(record["id"])
        return record

    def block(self, atom: dict[str, Any], code: str, message: str) -> None:
        atom["disposition"] = "blocked"
        atom["reason"] = message
        self.diagnostics.append(
            {
                "id": f"diag-{len(self.diagnostics) + 1:03d}",
                "owner": "integration",
                "producer": INTEGRATION_ID,
                "phase": "verification_projection",
                "severity": "ERROR",
                "code": code,
                "message": message,
                "atom_id": atom["id"],
            }
        )


def project_verification_scenario(
    scenario_path: Path,
    input_set_manifest: Path,
    profile_path: Path,
) -> dict[str, Any]:
    core = load_core_input_set(input_set_manifest)
    profile = load_projection_profile(profile_path)
    loaded = ScenarioLoader().load(scenario_path)

    if orbitfabric_version != core.orbitfabric_version:
        raise ValueError(
            "OrbitFabric runtime version does not match the Core Integration Input Set "
            "producer version"
        )
    if loaded.mission_model.spacecraft.id != core.mission_id:
        raise ValueError("Scenario mission id does not match Core Integration Input Set")
    if loaded.mission_model.spacecraft.model_version != core.model_version:
        raise ValueError("Scenario mission model_version does not match Core Integration Input Set")

    scenario_path = scenario_path.resolve()
    scenario = loaded.scenario
    builder = PlanBuilder()

    builder.add_atom(
        kind="scenario_metadata",
        role="metadata",
        step_index=None,
        scenario_t=None,
        disposition="projected",
        source=None,
        source_value={
            "id": scenario.scenario.id,
            "name": scenario.scenario.name,
            "description": scenario.scenario.description,
        },
    )

    builder.add_atom(
        kind="initial_mode",
        role="initial_state",
        step_index=None,
        scenario_t=None,
        disposition="not_projected",
        source=_core_source(core, "modes", scenario.initial_state.mode),
        reason=NOT_PROJECTED_REASONS["initial_mode"],
        source_value=scenario.initial_state.mode,
    )

    for telemetry_id in sorted(scenario.initial_state.telemetry):
        builder.add_atom(
            kind="initial_telemetry",
            role="initial_state",
            step_index=None,
            scenario_t=None,
            disposition="not_projected",
            source=_core_source(core, "telemetry", telemetry_id),
            reason=NOT_PROJECTED_REASONS["initial_telemetry"],
            source_value=scenario.initial_state.telemetry[telemetry_id],
        )

    for step_index, step in enumerate(scenario.steps):
        _project_step(builder, core, profile, step, step_index)

    accounting = _accounting(builder)
    status = "blocked" if accounting["blocked_atoms"] else "executable_subset"

    return {
        "kind": PLAN_KIND,
        "plan_version": PLAN_VERSION,
        "status": status,
        "source": {
            "scenario_id": scenario.scenario.id,
            "scenario_name": scenario.scenario.name,
            "scenario_description": scenario.scenario.description,
            "scenario_sha256": sha256_file(scenario_path),
            "orbitfabric_version": orbitfabric_version,
        },
        "core_input": {
            "kind": core.manifest["kind"],
            "input_set_version": core.manifest["input_set_version"],
            "input_set_sha256": core.input_set_sha256,
            "mission_id": core.mission_id,
            "model_version": core.model_version,
        },
        "profile": {
            "kind": profile.document["kind"],
            "profile_version": profile.document["profile_version"],
            "id": profile.id,
            "version": profile.version,
            "sha256": profile.sha256,
        },
        "integration": {
            "id": INTEGRATION_ID,
            "schema_version": INTEGRATION_SCHEMA_VERSION,
            "adapter_version": adapter_version,
        },
        "target": {
            "ecosystem": "OpenC3 COSMOS",
            "baseline": COSMOS_BASELINE,
            "target_name": profile.target_name,
        },
        "accounting": accounting,
        "atoms": builder.atoms,
        "operations": builder.operations,
        "diagnostics": builder.diagnostics,
    }


def _project_step(
    builder: PlanBuilder,
    core: CoreInputSet,
    profile: ProjectionProfile,
    step: Any,
    step_index: int,
) -> None:
    scenario_t = step.t

    if step.command is not None:
        _project_command(builder, core, profile, step, step_index, scenario_t)

    if step.inject is not None:
        builder.add_atom(
            kind="telemetry_injection",
            role="action",
            step_index=step_index,
            scenario_t=scenario_t,
            disposition="not_projected",
            source=_core_source(core, "telemetry", step.inject.telemetry),
            reason=NOT_PROJECTED_REASONS["telemetry_injection"],
            source_value=step.inject.value,
        )

    if step.expect_event is not None:
        builder.add_atom(
            kind="expect_event",
            role="expectation",
            step_index=step_index,
            scenario_t=scenario_t,
            disposition="not_projected",
            source=_core_source(core, "events", step.expect_event),
            reason=NOT_PROJECTED_REASONS["expect_event"],
            source_value=True,
        )

    if step.expect_mode is not None:
        builder.add_atom(
            kind="expect_mode",
            role="expectation",
            step_index=step_index,
            scenario_t=scenario_t,
            disposition="not_projected",
            source=_core_source(core, "modes", step.expect_mode),
            reason=NOT_PROJECTED_REASONS["expect_mode"],
            source_value=step.expect_mode,
        )

    if step.expect_command is not None:
        builder.add_atom(
            kind="expect_command",
            role="expectation",
            step_index=step_index,
            scenario_t=scenario_t,
            disposition="not_projected",
            source=_core_source(core, "commands", step.expect_command.id),
            reason=NOT_PROJECTED_REASONS["expect_command"],
            source_value={"dispatch": step.expect_command.dispatch},
        )

    if step.expect_telemetry is not None:
        for telemetry_id in sorted(step.expect_telemetry):
            _project_telemetry_expectation(
                builder,
                core,
                profile,
                telemetry_id,
                step.expect_telemetry[telemetry_id],
                step_index,
                scenario_t,
            )

    if step.expect is not None:
        for key in sorted(step.expect):
            _account_nested_expectation(
                builder,
                core,
                key,
                step.expect[key],
                step_index,
                scenario_t,
            )


def _project_command(
    builder: PlanBuilder,
    core: CoreInputSet,
    profile: ProjectionProfile,
    step: Any,
    step_index: int,
    scenario_t: int | float,
) -> None:
    source = _core_source(core, "commands", step.command)
    binding = profile.binding_for("commands", step.command)
    atom = builder.add_atom(
        kind="command",
        role="action",
        step_index=step_index,
        scenario_t=scenario_t,
        disposition="projected",
        source=source,
        binding_id=binding.id if binding else None,
        source_value={"args": dict(step.args)},
    )

    if binding is None:
        builder.block(atom, "OF-COSMOS-PROJ-001", f"missing command binding for {step.command}")
        return
    if binding.intent == "do_not_project":
        atom["disposition"] = "not_projected"
        atom["reason"] = binding.reason
        return

    if step.args:
        builder.block(
            atom,
            "OF-COSMOS-PROJ-002",
            (
                "command arguments require an explicit COSMOS encoder; unsupported in "
                f"initial scope: {step.command}"
            ),
        )
        for arg_name in sorted(step.args):
            builder.add_atom(
                kind="command_argument",
                role="action",
                step_index=step_index,
                scenario_t=scenario_t,
                disposition="blocked",
                source=source,
                binding_id=binding.id,
                reason=(
                    "Command argument encoding is not defined in the initial OpenC3 COSMOS "
                    "adapter scope."
                ),
                source_value={"name": arg_name, "value": step.args[arg_name]},
            )
        return

    builder.add_operation(
        atom,
        operation="send_command",
        binding_id=binding.id,
        origin="profile_mapping",
        resolved={
            "target": profile.target_name,
            "command": binding.config["cosmos_command"],
            "arguments": {},
        },
    )


def _project_telemetry_expectation(
    builder: PlanBuilder,
    core: CoreInputSet,
    profile: ProjectionProfile,
    telemetry_id: str,
    expected_value: Any,
    step_index: int,
    scenario_t: int | float,
) -> None:
    source = _core_source(core, "telemetry", telemetry_id)
    binding = profile.binding_for("telemetry", telemetry_id)
    atom = builder.add_atom(
        kind="expect_telemetry",
        role="expectation",
        step_index=step_index,
        scenario_t=scenario_t,
        disposition="projected",
        source=source,
        binding_id=binding.id if binding else None,
        source_value=expected_value,
    )

    if binding is None:
        builder.block(atom, "OF-COSMOS-PROJ-003", f"missing telemetry binding for {telemetry_id}")
        return
    if binding.intent == "do_not_project":
        atom["disposition"] = "not_projected"
        atom["reason"] = binding.reason
        return

    try:
        encoded = _encode_expected_value(expected_value, binding)
    except ValueError as exc:
        builder.block(atom, "OF-COSMOS-PROJ-004", str(exc))
        return

    builder.add_operation(
        atom,
        operation="wait_telemetry",
        binding_id=binding.id,
        origin="scenario_expectation_plus_profile_observation_policy",
        resolved={
            "target": profile.target_name,
            "packet": binding.config["cosmos_packet"],
            "item": binding.config["cosmos_item"],
            "operator": "==",
            "source_expected_value": expected_value,
            "expected_value": encoded,
            "value_encoding": binding.config.get("value_encoding", "identity"),
            "timeout_s": profile.telemetry_wait_timeout_s,
        },
    )


def _account_nested_expectation(
    builder: PlanBuilder,
    core: CoreInputSet,
    key: str,
    value: Any,
    step_index: int,
    scenario_t: int | float,
) -> None:
    kind = KNOWN_EXPECT_KEYS.get(key)
    if kind is None:
        builder.add_atom(
            kind="unknown_expectation",
            role="expectation",
            step_index=step_index,
            scenario_t=scenario_t,
            disposition="blocked",
            source=None,
            reason=f"Scenario expect key is not understood by this integration: {key}",
            source_value={"key": key, "value": value},
        )
        return

    source: dict[str, str] | None = None
    if key == "payload_lifecycle" and isinstance(value, dict):
        payload = value.get("payload")
        if isinstance(payload, str):
            source = _core_source(core, "payloads", payload)
    elif key == "data_flow" and isinstance(value, dict):
        product = value.get("data_product")
        if isinstance(product, str):
            source = _core_source(core, "data_products", product)

    builder.add_atom(
        kind=kind,
        role="expectation",
        step_index=step_index,
        scenario_t=scenario_t,
        disposition="not_projected",
        source=source,
        reason=NOT_PROJECTED_REASONS[kind],
        source_value=value,
    )


def _encode_expected_value(value: Any, binding: ProjectionBinding) -> Any:
    encoding = binding.config.get("value_encoding", "identity")
    if encoding == "identity":
        if isinstance(value, (dict, list)):
            raise ValueError(
                "identity encoding only supports scalar telemetry expectations in initial scope"
            )
        return value
    if encoding == "boolean_01":
        if not isinstance(value, bool):
            raise ValueError("boolean_01 encoding requires a boolean Scenario expectation")
        return 1 if value else 0
    raise ValueError(f"unsupported telemetry value encoding: {encoding}")


def _core_source(core: CoreInputSet, domain: str, entity_id: str) -> dict[str, str]:
    core.require_entity(domain, entity_id)
    return {"domain": domain, "id": entity_id}


def _accounting(builder: PlanBuilder) -> dict[str, int]:
    atoms = builder.atoms
    return {
        "source_atoms": len(atoms),
        "projected_atoms": sum(a["disposition"] == "projected" for a in atoms),
        "not_projected_atoms": sum(a["disposition"] == "not_projected" for a in atoms),
        "blocked_atoms": sum(a["disposition"] == "blocked" for a in atoms),
        "source_actions": sum(a["role"] == "action" for a in atoms),
        "source_expectations": sum(a["role"] == "expectation" for a in atoms),
        "projected_source_actions": sum(
            a["role"] == "action" and a["disposition"] == "projected" for a in atoms
        ),
        "projected_source_expectations": sum(
            a["role"] == "expectation" and a["disposition"] == "projected" for a in atoms
        ),
        "resolved_operations": len(builder.operations),
    }
