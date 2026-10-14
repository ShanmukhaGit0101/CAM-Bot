#!/usr/bin/env python3
"""Feedback-gated CAM-BOT machine-tending workflow coordinator."""

from __future__ import annotations

from datetime import datetime, timezone
import json
import math
from pathlib import Path
import time
from typing import Any, Dict, Optional

from ament_index_python.packages import get_package_share_directory
from control_msgs.action import FollowJointTrajectory
import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_srvs.srv import Trigger
from std_msgs.msg import String
from trajectory_msgs.msg import JointTrajectoryPoint

from carrier_control.metrics import append_trial
from carrier_control.machine_tending_fsm import FSMError, MachineTendingFSM, StepOutcome
from carrier_control.workflow import PROCESS_PHASES, WorkflowError, load_plan
from carrier_control.waypoints import UR5_JOINT_NAMES
from carrier_control.workcell_model import station_for_target, target_world_xyz


CUSTOM_JOINTS = (
    "left_shoulder_joint",
    "left_elbow_joint",
    "right_shoulder_joint",
    "right_elbow_joint",
)
WORKPIECE_JOINTS = (
    "workpiece_x_joint",
    "workpiece_y_joint",
    "workpiece_z_joint",
)
VISUAL_CARRIER_JOINTS = UR5_JOINT_NAMES

class MachineTendingCoordinator(Node):
    """Run one bounded, traceable workflow in controller or visual mode."""

    def __init__(self) -> None:
        super().__init__("machine_tending_coordinator")
        share = Path(get_package_share_directory("carrier_control"))
        default_config = str(share / "config" / "machine_tending.json")
        default_results = str(Path.home() / ".ros" / "cambot" / "machine_tending_trials.csv")
        self.declare_parameter("mode", "visual_simulation")
        self.declare_parameter("config_file", default_config)
        self.declare_parameter("results_file", default_results)
        self.declare_parameter("trial_count", 1)
        self.declare_parameter("visual_time_scale", 1.0)
        self.declare_parameter("auto_start", True)
        self.declare_parameter("fault_injection_step", "")

        self.mode = self.get_parameter("mode").value
        if self.mode not in ("controller", "visual_simulation"):
            raise WorkflowError("mode must be controller or visual_simulation")
        config_file = self.get_parameter("config_file").value
        self.plan = load_plan(
            config_file,
            require_controller_ready=self.mode == "controller",
        )
        self.results_file = self.get_parameter("results_file").value
        self.trial_count = int(self.get_parameter("trial_count").value)
        self.visual_time_scale = float(self.get_parameter("visual_time_scale").value)
        self.fault_injection_step = self.get_parameter("fault_injection_step").value
        auto_value = self.get_parameter("auto_start").value
        if isinstance(auto_value, bool):
            self.auto_start = auto_value
        elif isinstance(auto_value, str) and auto_value.lower() in ("true", "false"):
            self.auto_start = auto_value.lower() == "true"
        else:
            raise WorkflowError("auto_start must be true or false")
        if not 1 <= self.trial_count <= 25:
            raise WorkflowError("trial_count must be in [1, 25]")
        if not 0.01 <= self.visual_time_scale <= 10.0:
            raise WorkflowError("visual_time_scale must be in [0.01, 10.0]")
        if (not isinstance(self.fault_injection_step, str) or
                (self.fault_injection_step and self.mode != "visual_simulation") or
                (self.fault_injection_step and self.fault_injection_step not in
                 {step["name"] for step in self.plan["workflow"]})):
            raise WorkflowError(
                "fault_injection_step must name a workflow step in visual simulation only"
            )

        self.joint_publisher = self.create_publisher(JointState, "/joint_states", 10)
        self.task_publisher = self.create_publisher(String, "/cambot/task_state", 10)
        self.workpiece_publisher = self.create_publisher(
            String, "/cambot/workpiece_state", 10
        )
        self.coordinator_publisher = self.create_publisher(
            String, "/cambot/coordinator_state", 10
        )

        self.custom_positions = list(self.plan["bimanual_poses"]["HOME"])
        self.visual_carrier_positions = list(
            self.plan["stations"]["HOME"]["visual_carrier_joints"]
        )
        self.workpiece_positions = target_world_xyz(self.plan["workcell"], "RAW_PICK")
        self.workpiece_state = "RAW_AT_S1"
        self.coordinator_state = "INITIALIZING"
        self.carrier_motion_count = 0
        self.feedback_count = 0
        self.feedback_joint_travel = 0.0
        self._last_feedback_positions: Optional[list[float]] = None
        self.carrier_joint_sample: Optional[tuple[float, ...]] = None
        self.client = None
        self.last_motion_failure = None
        self.start_requested = False
        self.fsm = MachineTendingFSM(
            self.plan,
            notify=self._fsm_event,
            timeout_scale=(max(1.0, self.visual_time_scale)
                           if self.mode == "visual_simulation" else 1.0),
        )

        if self.mode == "controller":
            self.client = ActionClient(
                self,
                FollowJointTrajectory,
                self.plan["carrier"]["action_name"],
            )
            timeout = self.plan["carrier"]["server_timeout_s"]
            if not self.client.wait_for_server(timeout_sec=timeout):
                raise RuntimeError(
                    f"carrier controller unavailable after {timeout:.1f}s"
                )
            self.carrier_joint_subscription = self.create_subscription(
                JointState, "/joint_states", self._carrier_joint_state, 10
            )
            joint_deadline = time.monotonic() + timeout
            while self.carrier_joint_sample is None:
                remaining = joint_deadline - time.monotonic()
                if remaining <= 0:
                    raise RuntimeError(
                        f"carrier /joint_states unavailable after {timeout:.1f}s"
                    )
                rclpy.spin_once(self, timeout_sec=min(0.1, remaining))
        else:
            self.get_logger().warning(
                "VISUAL SIMULATION ONLY: carrier joints are not commanded; "
                "this run is not runtime or end-to-end verification"
            )

        self._publish_coordinator("READY")
        self._publish_workpiece()
        self._publish_visual_joints()
        self.start_service = self.create_service(Trigger, "~/start", self._start_service)
        self.reset_service = self.create_service(Trigger, "~/reset", self._reset_service)
        self.cancel_service = self.create_service(Trigger, "~/cancel", self._cancel_service)

    def _publish_json(self, publisher, payload: Dict[str, Any]) -> None:
        message = String()
        message.data = json.dumps(payload, sort_keys=True)
        publisher.publish(message)

    def _publish_coordinator(self, state: str, **extra: Any) -> None:
        self.coordinator_state = state
        self._publish_json(
            self.coordinator_publisher,
            {"state": state, "mode": self.mode, **extra},
        )

    def _publish_task(self, state: str, **extra: Any) -> None:
        self._publish_json(
            self.task_publisher,
            {"state": state, "mode": self.mode, **extra},
        )

    def _fsm_event(self, event: Dict[str, Any]) -> None:
        payload = {**event, "mode": self.mode}
        step_name = event.get("step")
        if step_name:
            step = next(item for item in self.plan["workflow"]
                        if item["name"] == step_name)
            target_id = step.get("target")
            if target_id:
                station_id = station_for_target(self.plan["workcell"], target_id)
                payload.update({
                    "target": target_id,
                    "target_frame": self.plan["workcell"]["stations"][station_id]["frame"],
                    "visual_target_world_xyz_m": target_world_xyz(
                        self.plan["workcell"], target_id
                    ),
                })
        self._publish_json(self.task_publisher, payload)
        if event["event"] in ("STEP_COMPLETED", "RESET"):
            self.workpiece_state = event["workpiece_state"]
            if event["event"] == "RESET":
                self.workpiece_positions = target_world_xyz(
                    self.plan["workcell"], "RAW_PICK"
                )
                self.custom_positions = list(self.plan["bimanual_poses"]["HOME"])
                self.visual_carrier_positions = list(
                    self.plan["stations"]["HOME"]["visual_carrier_joints"]
                )
                self._publish_visual_joints()
            self._publish_workpiece()

    def _start_service(self, request, response):
        if self.fsm.status != "IDLE" or self.start_requested:
            response.success = False
            response.message = "start requires IDLE; reset after terminal state"
        else:
            self.start_requested = True
            response.success = True
            response.message = "one-shot cycle queued"
        return response

    def _reset_service(self, request, response):
        try:
            self.fsm.reset()
        except FSMError as exc:
            response.success = False
            response.message = str(exc)
            return response
        self.start_requested = False
        self._publish_coordinator("READY")
        response.success = True
        response.message = "FSM reset to IDLE and raw workpiece"
        return response

    def _cancel_service(self, request, response):
        if self.start_requested and self.fsm.status == "IDLE":
            self.start_requested = False
            response.success = True
            response.message = "queued start cancelled"
            return response
        try:
            self.fsm.cancel()
        except FSMError as exc:
            response.success = False
            response.message = str(exc)
            return response
        response.success = True
        response.message = "cancellation requested; awaiting bounded step stop"
        return response

    def _publish_workpiece(self) -> None:
        self._publish_json(
            self.workpiece_publisher,
            {
                "state": self.workpiece_state,
                "process_phase": PROCESS_PHASES[self.workpiece_state],
                "simulated_attachment": self.workpiece_state.startswith("HELD_"),
                "mode": self.mode,
                "visual_xyz": self.workpiece_positions,
            },
        )

    def _publish_visual_joints(self) -> None:
        message = JointState()
        message.header.stamp = self.get_clock().now().to_msg()
        message.name = list(CUSTOM_JOINTS + WORKPIECE_JOINTS)
        message.position = self.custom_positions + self.workpiece_positions
        if self.mode == "visual_simulation":
            message.name = list(VISUAL_CARRIER_JOINTS) + message.name
            message.position = self.visual_carrier_positions + message.position
        self.joint_publisher.publish(message)

    def _feedback(self, message) -> None:
        positions = list(message.feedback.actual.positions)
        if len(positions) != len(self.plan["carrier"]["joint_names"]):
            return
        if self._last_feedback_positions is not None:
            self.feedback_joint_travel += sum(
                abs(current - previous)
                for current, previous in zip(positions, self._last_feedback_positions)
            )
        self._last_feedback_positions = positions
        self.feedback_count += 1

    def _carrier_joint_state(self, message: JointState) -> None:
        """Accept a complete UR5 sample, never our custom-only joint update."""
        positions = dict(zip(message.name, message.position))
        names = self.plan["carrier"]["joint_names"]
        if (len(message.name) == len(message.position) and
                all(name in positions and math.isfinite(positions[name]) for name in names)):
            self.carrier_joint_sample = tuple(float(positions[name]) for name in names)

    def _cancel_bounded(self, goal_handle) -> bool:
        cancel_future = goal_handle.cancel_goal_async()
        rclpy.spin_until_future_complete(self, cancel_future, timeout_sec=2.0)
        return bool(cancel_future.done() and cancel_future.result() is not None and
                    cancel_future.result().goals_canceling)

    def _wait_future(self, future, timeout_s, cancelled) -> str:
        deadline = time.monotonic() + timeout_s
        while not future.done():
            if cancelled():
                return "CANCELLED"
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return "TIMEOUT"
            rclpy.spin_once(self, timeout_sec=min(0.1, remaining))
        return "DONE"

    def _fail_move(self, cause, message) -> bool:
        self.last_motion_failure = cause
        self.get_logger().error(message)
        return False

    def _move_carrier(self, station_name: str, duration_s: float,
                      cancelled=lambda: False) -> bool:
        self.last_motion_failure = None
        if cancelled():
            return self._fail_move("CANCELLED", f"{station_name}: cancelled before goal")
        if self.mode == "visual_simulation":
            self._publish_task(
                "CARRIER_NOT_COMMANDED", station=station_name,
                fsm_state=self.fsm.current_state, trial_id=self.fsm.trial_id,
                timestamp_utc=datetime.now(timezone.utc).isoformat(),
            )
            return True

        station = self.plan["stations"][station_name]
        goal = FollowJointTrajectory.Goal()
        goal.trajectory.joint_names = list(self.plan["carrier"]["joint_names"])
        point = JointTrajectoryPoint()
        point.positions = list(station["carrier_joints"])
        point.velocities = [0.0] * 6
        point.accelerations = [0.0] * 6
        point.time_from_start.sec = int(duration_s)
        point.time_from_start.nanosec = int((duration_s % 1.0) * 1e9)
        goal.trajectory.points.append(point)

        feedback_before = self.feedback_count
        send_future = self.client.send_goal_async(goal, feedback_callback=self._feedback)
        response_timeout = self.plan["carrier"]["goal_response_timeout_s"]
        response_wait = self._wait_future(send_future, response_timeout, cancelled)
        if response_wait == "CANCELLED":
            rclpy.spin_until_future_complete(
                self, send_future, timeout_sec=response_timeout
            )
            if (send_future.done() and send_future.result() is not None and
                    send_future.result().accepted):
                cancel_accepted = self._cancel_bounded(send_future.result())
            else:
                cancel_accepted = False
            cause = ("CANCEL_REQUEST_ACCEPTED" if cancel_accepted
                     else "CANCEL_UNCONFIRMED")
            return self._fail_move(cause, f"{station_name}: cancelled during goal response")
        if not send_future.done() or send_future.result() is None:
            return self._fail_move("GOAL_RESPONSE_TIMEOUT",
                                   f"{station_name}: goal response timed out")
        goal_handle = send_future.result()
        if not goal_handle.accepted:
            return self._fail_move("GOAL_REJECTED", f"{station_name}: trajectory rejected")

        result_future = goal_handle.get_result_async()
        result_timeout = duration_s + self.plan["carrier"]["result_margin_s"]
        result_wait = self._wait_future(result_future, result_timeout, cancelled)
        if result_wait == "CANCELLED":
            cancel_accepted = self._cancel_bounded(goal_handle)
            cause = ("CANCEL_REQUEST_ACCEPTED" if cancel_accepted
                     else "CANCEL_UNCONFIRMED")
            return self._fail_move(cause, f"{station_name}: cancellation requested")
        if not result_future.done() or result_future.result() is None:
            cancel_accepted = self._cancel_bounded(goal_handle)
            cause = ("RESULT_TIMEOUT_CANCEL_REQUEST_ACCEPTED" if cancel_accepted
                     else "RESULT_TIMEOUT_CANCEL_UNCONFIRMED")
            return self._fail_move(cause, f"{station_name}: result timed out; cancelling")
        result = result_future.result().result
        if result.error_code != FollowJointTrajectory.Result.SUCCESSFUL:
            return self._fail_move(
                f"CONTROLLER_ERROR_{result.error_code}",
                f"{station_name}: controller error {result.error_code}",
            )
        feedback_deadline = time.monotonic() + self.plan["carrier"][
            "feedback_timeout_s"
        ]
        while self.feedback_count <= feedback_before:
            if cancelled():
                return self._fail_move("CANCELLED_AFTER_RESULT",
                                       f"{station_name}: cancelled while awaiting feedback")
            remaining = feedback_deadline - time.monotonic()
            if remaining <= 0:
                break
            rclpy.spin_once(self, timeout_sec=min(0.1, remaining))
        if self.feedback_count <= feedback_before:
            return self._fail_move(
                "NO_ACTUAL_POSITION_FEEDBACK",
                f"{station_name}: success result had no actual-position feedback",
            )
        self.carrier_motion_count += 1
        return True

    @staticmethod
    def _state_target(state: str) -> Optional[str]:
        if state.endswith("AT_S1"):
            return "RAW_PICK"
        if state.endswith("AT_S2"):
            return "STAGE_INSPECT"
        if state.endswith("AT_S3") or state.endswith("IN_MACHINE"):
            return "MACHINE_UNLOAD" if "PROCESSED" in state else "MACHINE_LOAD"
        if state.endswith("AT_S4"):
            return "OUTPUT_UNLOAD"
        if state.endswith("AT_S5"):
            return "FINISHED_PLACE"
        return None

    def _animate_visual_state(
            self,
            pose_name: str,
            next_state: str,
            duration_s: float,
            station_name: Optional[str],
            deadline: float,
            cancelled,
    ) -> bool:
        start_custom = list(self.custom_positions)
        start_workpiece = list(self.workpiece_positions)
        start_carrier = list(self.visual_carrier_positions)
        target_custom = list(self.plan["bimanual_poses"][pose_name])
        target_workpiece = list(self.workpiece_positions)
        target_carrier = list(self.visual_carrier_positions)
        if self.mode == "visual_simulation" and station_name is not None:
            target_carrier = list(
                self.plan["stations"][station_name]["visual_carrier_joints"]
            )
        workpiece_target = self._state_target(next_state)
        if workpiece_target is not None:
            target_workpiece = target_world_xyz(self.plan["workcell"], workpiece_target)
        # In controller mode, placeholder joints have no actuator feedback.
        # Publish their visual target once; do not use sleep as action success.
        scaled_duration = (duration_s * self.visual_time_scale
                           if self.mode == "visual_simulation" else 0.0)
        ticks = max(1, int(scaled_duration * 20.0))
        for tick in range(1, ticks + 1):
            if cancelled() or time.monotonic() >= deadline:
                return False
            alpha = tick / ticks
            smooth = 3.0 * alpha * alpha - 2.0 * alpha * alpha * alpha
            self.custom_positions = [
                start + (target - start) * smooth
                for start, target in zip(start_custom, target_custom)
            ]
            self.visual_carrier_positions = [
                start + (target - start) * smooth
                for start, target in zip(start_carrier, target_carrier)
            ]
            self.workpiece_positions = [
                start + (target - start) * smooth
                for start, target in zip(start_workpiece, target_workpiece)
            ]
            self._publish_visual_joints()
            if scaled_duration > 0:
                rclpy.spin_once(self, timeout_sec=min(
                    scaled_duration / ticks, max(0.0, deadline - time.monotonic())
                ))
        return not cancelled() and time.monotonic() < deadline

    def _wait_machine_dwell(self, seconds, deadline, cancelled) -> bool:
        end = min(time.monotonic() + seconds, deadline)
        while time.monotonic() < end:
            if cancelled():
                return False
            rclpy.spin_once(self, timeout_sec=min(0.1, end - time.monotonic()))
        return not cancelled() and time.monotonic() < deadline

    def _execute_fsm_step(self, step, deadline, cancelled) -> StepOutcome:
        if step["name"] == self.fault_injection_step:
            return StepOutcome(False, "INJECTED_VISUAL_TEST_FAILURE")
        if step["name"] == "MACHINE_DWELL":
            completed = self._wait_machine_dwell(step["duration_s"], deadline, cancelled)
            return StepOutcome(completed, None if completed else "DWELL_CANCELLED_OR_TIMEOUT")
        if step["station"] is not None and not self._move_carrier(
                step["station"], step["duration_s"], cancelled):
            return StepOutcome(False, self.last_motion_failure or "CARRIER_ACTION_FAILED")
        if not self._animate_visual_state(
                step["bimanual_pose"], step["to_state"], step["duration_s"],
                step["station"], deadline, cancelled):
            return StepOutcome(False, "VISUAL_UPDATE_CANCELLED_OR_TIMEOUT")
        return StepOutcome(True)

    def run_trial(self, trial_number: int) -> Dict[str, Any]:
        trial_id = f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{trial_number:03d}"
        started = time.monotonic()
        self.carrier_motion_count = 0
        self.feedback_count = 0
        self.feedback_joint_travel = 0.0
        self._last_feedback_positions = None
        self.workpiece_state = "RAW_AT_S1"
        self.workpiece_positions = target_world_xyz(self.plan["workcell"], "RAW_PICK")
        self._publish_coordinator("RUNNING", trial_id=trial_id)
        self._publish_workpiece()
        self.fsm.start(trial_id)
        outcome = self.fsm.run(self._execute_fsm_step)
        self._publish_coordinator(
            outcome.terminal, trial_id=trial_id,
            failure_state=outcome.failure_state,
            failure_stage=outcome.failure_step,
            failure_cause=outcome.cause,
        )
        runtime_verified = False
        return {
            "schema_version": "1.0",
            "trial_id": trial_id,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "mode": self.mode,
            "cycle_time_s": round(time.monotonic() - started, 6),
            "success": outcome.success,
            "failure_stage": outcome.failure_step,
            "carrier_motion_count": self.carrier_motion_count,
            "carrier_joint_travel_rad": (
                round(self.feedback_joint_travel, 6)
                if self.mode == "controller" else None
            ),
            "workpiece_final_state": outcome.workpiece_state,
            "runtime_verified": runtime_verified,
            "end_to_end_verified": False,
            "notes": (
                "carrier result and actual-position feedback observed; "
                "TF/runtime validation and bimanual motion remain unverified"
                if self.mode == "controller" and outcome.success else
                "visual state-machine exercise only; no carrier actuation or verified grasp"
            ),
        }

    def run_trials(self) -> bool:
        all_successful = True
        for trial_number in range(1, self.trial_count + 1):
            if trial_number > 1:
                self.fsm.reset()
            record = self.run_trial(trial_number)
            append_trial(self.results_file, record)
            all_successful = all_successful and record["success"]
            if not record["success"]:
                break
        return all_successful


def main(args=None) -> None:
    rclpy.init(args=args)
    node = None
    try:
        node = MachineTendingCoordinator()
        if node.auto_start:
            if not node.run_trials():
                raise RuntimeError("machine-tending FSM failed")
        else:
            while rclpy.ok():
                rclpy.spin_once(node, timeout_sec=0.1)
                if node.start_requested:
                    node.start_requested = False
                    node.run_trials()
    except (RuntimeError, WorkflowError, FSMError) as exc:
        if node is not None:
            node.get_logger().error(str(exc))
        else:
            print(f"machine_tending_coordinator: {exc}")
        raise
    finally:
        if node is not None:
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
