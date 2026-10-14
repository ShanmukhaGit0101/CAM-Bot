"""Pure-Python machine-tending plan loading and validation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable


REQUIRED_STATIONS = (
    "HOME",
    "S1_RAW",
    "S2_STAGING",
    "S3_MACHINE",
    "S4_OUTPUT",
    "S5_FINISHED",
)
REQUIRED_STEPS = (
    "HOME_START",
    "S1_APPROACH",
    "S1_GRASP",
    "S2_STAGE",
    "S3_LOAD",
    "S3_RELEASE",
    "MACHINE_DWELL",
    "S3_REGRASP",
    "S4_UNLOAD",
    "S5_PLACE",
    "S5_RELEASE",
    "HOME_END",
)


class WorkflowError(ValueError):
    """Raised when a machine-tending plan violates its safety contract."""


def _numbers(values: Any, count: int, field: str) -> None:
    if not isinstance(values, list) or len(values) != count:
        raise WorkflowError(f"{field} must contain {count} values")
    if any(isinstance(value, bool) or not isinstance(value, (int, float))
           for value in values):
        raise WorkflowError(f"{field} must contain only numbers")


def load_plan(path: Path | str, require_controller_ready: bool = False) -> Dict[str, Any]:
    """Load and validate a plan without requiring ROS or PyYAML."""
    plan_path = Path(path)
    try:
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise WorkflowError(f"cannot load plan {plan_path}: {exc}") from exc
    validate_plan(plan, require_controller_ready=require_controller_ready)
    return plan


def validate_plan(plan: Any, require_controller_ready: bool = False) -> None:
    """Validate structure, state continuity, limits, and controller readiness."""
    if not isinstance(plan, dict) or plan.get("schema_version") != "1.0":
        raise WorkflowError("schema_version must be '1.0'")

    carrier = plan.get("carrier")
    if not isinstance(carrier, dict):
        raise WorkflowError("carrier must be an object")
    joint_names = carrier.get("joint_names")
    if not isinstance(joint_names, list) or len(joint_names) != 6 or not all(
            isinstance(name, str) and name for name in joint_names):
        raise WorkflowError("carrier.joint_names must contain six names")
    for field in (
        "server_timeout_s",
        "goal_response_timeout_s",
        "result_margin_s",
        "feedback_timeout_s",
    ):
        value = carrier.get(field)
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 < value <= 120:
            raise WorkflowError(f"carrier.{field} must be in (0, 120]")

    stations = plan.get("stations")
    if not isinstance(stations, dict) or tuple(stations) != REQUIRED_STATIONS:
        raise WorkflowError("stations must contain HOME and S1_RAW through S5_FINISHED in order")
    for name, station in stations.items():
        if not isinstance(station, dict):
            raise WorkflowError(f"station {name} must be an object")
        _numbers(station.get("visual_xyz"), 3, f"stations.{name}.visual_xyz")
        joints = station.get("carrier_joints")
        if joints is not None:
            _numbers(joints, 6, f"stations.{name}.carrier_joints")
        if require_controller_ready and name != "HOME":
            if joints is None:
                raise WorkflowError(f"station {name} has no taught carrier target")
            if station.get("controller_validated") is not True:
                raise WorkflowError(f"station {name} target is not controller-validated")

    poses = plan.get("bimanual_poses")
    if not isinstance(poses, dict) or not poses:
        raise WorkflowError("bimanual_poses must be a non-empty object")
    for name, pose in poses.items():
        _numbers(pose, 4, f"bimanual_poses.{name}")
        if any(not -1.57 <= value <= 1.57 for value in pose):
            raise WorkflowError(f"bimanual pose {name} exceeds placeholder joint limits")

    workflow = plan.get("workflow")
    if not isinstance(workflow, list) or tuple(
            step.get("name") for step in workflow if isinstance(step, dict)) != REQUIRED_STEPS:
        raise WorkflowError("workflow names/order do not match the required machine-tending sequence")
    previous_to = None
    for index, step in enumerate(workflow):
        if not isinstance(step, dict):
            raise WorkflowError(f"workflow[{index}] must be an object")
        station = step.get("station")
        if station is not None and station not in stations:
            raise WorkflowError(f"workflow[{index}] references unknown station {station}")
        if step.get("bimanual_pose") not in poses:
            raise WorkflowError(f"workflow[{index}] references unknown bimanual pose")
        duration = step.get("duration_s")
        if isinstance(duration, bool) or not isinstance(duration, (int, float)) or not 0 < duration <= 120:
            raise WorkflowError(f"workflow[{index}].duration_s must be in (0, 120]")
        from_state = step.get("from_state")
        to_state = step.get("to_state")
        if not isinstance(from_state, str) or not isinstance(to_state, str):
            raise WorkflowError(f"workflow[{index}] requires string workpiece states")
        if previous_to is not None and from_state != previous_to:
            raise WorkflowError(
                f"workflow[{index}] state discontinuity: expected {previous_to}, got {from_state}"
            )
        previous_to = to_state


def stations_used_by(workflow: Iterable[Dict[str, Any]]) -> tuple[str, ...]:
    """Return carrier station names in execution order."""
    return tuple(step["station"] for step in workflow if step.get("station") is not None)
