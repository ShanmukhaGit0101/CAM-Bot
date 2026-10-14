#!/usr/bin/env python3
"""Feedback-gated CAM-BOT machine-tending workflow coordinator."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import time
from typing import Any, Dict, Optional

from ament_index_python.packages import get_package_share_directory
from control_msgs.action import FollowJointTrajectory
import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import String
from trajectory_msgs.msg import JointTrajectoryPoint

from carrier_control.metrics import append_trial
from carrier_control.workflow import WorkflowError, load_plan


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
VISUAL_CARRIER_JOINTS = (
    "shoulder_pan_joint",
    "shoulder_lift_joint",
    "elbow_joint",
    "wrist_1_joint",
    "wrist_2_joint",
    "wrist_3_joint",
)


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
        if not 1 <= self.trial_count <= 25:
            raise WorkflowError("trial_count must be in [1, 25]")
        if not 0.01 <= self.visual_time_scale <= 10.0:
            raise WorkflowError("visual_time_scale must be in [0.01, 10.0]")

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
        self.workpiece_positions = list(self.plan["stations"]["S1_RAW"]["visual_xyz"])
        self.workpiece_state = "RAW_AT_S1"
        self.coordinator_state = "INITIALIZING"
        self.carrier_motion_count = 0
        self.feedback_count = 0
        self.feedback_joint_travel = 0.0
        self._last_feedback_positions: Optional[list[float]] = None
        self.client = None

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
        else:
            self.get_logger().warning(
                "VISUAL SIMULATION ONLY: carrier joints are not commanded; "
                "this run is not runtime or end-to-end verification"
            )

        self._publish_coordinator("READY")
        self._publish_workpiece()
        self._publish_visual_joints()

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

    def _publish_workpiece(self) -> None:
        self._publish_json(
            self.workpiece_publisher,
            {
                "state": self.workpiece_state,
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

    def _cancel_bounded(self, goal_handle) -> None:
        cancel_future = goal_handle.cancel_goal_async()
        rclpy.spin_until_future_complete(self, cancel_future, timeout_sec=2.0)

    def _move_carrier(self, station_name: str, duration_s: float) -> bool:
        if self.mode == "visual_simulation":
            self._publish_task("CARRIER_NOT_COMMANDED", station=station_name)
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
        rclpy.spin_until_future_complete(self, send_future, timeout_sec=response_timeout)
        if not send_future.done() or send_future.result() is None:
            self.get_logger().error(f"{station_name}: goal response timed out")
            return False
        goal_handle = send_future.result()
        if not goal_handle.accepted:
            self.get_logger().error(f"{station_name}: trajectory rejected")
            return False

        result_future = goal_handle.get_result_async()
        result_timeout = duration_s + self.plan["carrier"]["result_margin_s"]
        rclpy.spin_until_future_complete(self, result_future, timeout_sec=result_timeout)
        if not result_future.done() or result_future.result() is None:
            self.get_logger().error(f"{station_name}: result timed out; cancelling")
            self._cancel_bounded(goal_handle)
            return False
        result = result_future.result().result
        if result.error_code != FollowJointTrajectory.Result.SUCCESSFUL:
            self.get_logger().error(
                f"{station_name}: controller error {result.error_code}"
            )
            return False
        feedback_deadline = time.monotonic() + self.plan["carrier"][
            "feedback_timeout_s"
        ]
        while self.feedback_count <= feedback_before:
            remaining = feedback_deadline - time.monotonic()
            if remaining <= 0:
                break
            rclpy.spin_once(self, timeout_sec=min(0.1, remaining))
        if self.feedback_count <= feedback_before:
            self.get_logger().error(
                f"{station_name}: success result had no actual-position feedback"
            )
            return False
        self.carrier_motion_count += 1
        return True

    @staticmethod
    def _state_station(state: str) -> Optional[str]:
        if state.endswith("AT_S1"):
            return "S1_RAW"
        if state.endswith("AT_S2"):
            return "S2_STAGING"
        if state.endswith("AT_S3") or state.endswith("IN_MACHINE"):
            return "S3_MACHINE"
        if state.endswith("AT_S4"):
            return "S4_OUTPUT"
        if state.endswith("AT_S5"):
            return "S5_FINISHED"
        return None

    def _animate_visual_state(
            self,
            pose_name: str,
            next_state: str,
            duration_s: float,
            station_name: Optional[str],
    ) -> None:
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
        workpiece_station = self._state_station(next_state)
        if workpiece_station is not None:
            target_workpiece = list(
                self.plan["stations"][workpiece_station]["visual_xyz"]
            )
        scaled_duration = duration_s * self.visual_time_scale
        ticks = max(1, int(scaled_duration * 20.0))
        for tick in range(1, ticks + 1):
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
            time.sleep(scaled_duration / ticks)

    def run_trial(self, trial_number: int) -> Dict[str, Any]:
        trial_id = f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{trial_number:03d}"
        started = time.monotonic()
        failure_stage = None
        self.carrier_motion_count = 0
        self.feedback_count = 0
        self.feedback_joint_travel = 0.0
        self._last_feedback_positions = None
        self.workpiece_state = "RAW_AT_S1"
        self.workpiece_positions = list(self.plan["stations"]["S1_RAW"]["visual_xyz"])
        self._publish_coordinator("RUNNING", trial_id=trial_id)
        self._publish_workpiece()

        for step in self.plan["workflow"]:
            self._publish_task("STARTED", step=step["name"], trial_id=trial_id)
            if self.workpiece_state != step["from_state"]:
                failure_stage = step["name"]
                self.get_logger().error(
                    f"{step['name']}: expected {step['from_state']}, "
                    f"got {self.workpiece_state}"
                )
                break
            if step["station"] is not None and not self._move_carrier(
                    step["station"], step["duration_s"]):
                failure_stage = step["name"]
                break
            self._animate_visual_state(
                step["bimanual_pose"],
                step["to_state"],
                step["duration_s"],
                step["station"],
            )
            self.workpiece_state = step["to_state"]
            self._publish_workpiece()
            self._publish_task("COMPLETED", step=step["name"], trial_id=trial_id)

        success = failure_stage is None and self.workpiece_state == "FINISHED_AT_S5"
        terminal = "COMPLETE" if success else "FAILED"
        self._publish_coordinator(terminal, trial_id=trial_id, failure_stage=failure_stage)
        runtime_verified = False
        return {
            "schema_version": "1.0",
            "trial_id": trial_id,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "mode": self.mode,
            "cycle_time_s": round(time.monotonic() - started, 6),
            "success": success,
            "failure_stage": failure_stage,
            "carrier_motion_count": self.carrier_motion_count,
            "carrier_joint_travel_rad": (
                round(self.feedback_joint_travel, 6)
                if self.mode == "controller" else None
            ),
            "workpiece_final_state": self.workpiece_state,
            "runtime_verified": runtime_verified,
            "end_to_end_verified": False,
            "notes": (
                "carrier result and actual-position feedback observed; "
                "TF/runtime validation and bimanual motion remain unverified"
                if self.mode == "controller" and success else
                "visual state-machine exercise only; no carrier actuation or verified grasp"
            ),
        }

    def run_trials(self) -> bool:
        all_successful = True
        for trial_number in range(1, self.trial_count + 1):
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
        if not node.run_trials():
            raise RuntimeError("machine-tending workflow failed")
    except (RuntimeError, WorkflowError) as exc:
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
