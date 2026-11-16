#!/usr/bin/env python3
"""Exercise the production carrier action method against an isolated mock JTC.

No station plan or validation flag is changed. These small synthetic joint
vectors are protocol-test inputs, never taught poses or hardware commands.
"""

import argparse
import json
import math
from pathlib import Path
import time

from action_msgs.msg import GoalStatus
from control_msgs.action import FollowJointTrajectory
from control_msgs.msg import JointTolerance
from controller_manager_msgs.srv import ListControllers
import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from sensor_msgs.msg import JointState
from trajectory_msgs.msg import JointTrajectoryPoint

from carrier_control.machine_tending_coordinator import MachineTendingCoordinator
from carrier_control.mock_controller_model import JOINTS


ACTION = '/cambot_testbed/ur5_trajectory_controller/follow_joint_trajectory'


class RecordingClient(ActionClient):
    """Retain real goal handles so cancellation completion can be inspected."""

    def __init__(self, node):
        super().__init__(node, FollowJointTrajectory, ACTION)
        self.handles = []
        self.test_path_tolerance = None

    def send_goal_async(self, goal, **kwargs):
        if self.test_path_tolerance is not None:
            goal.path_tolerance = [JointTolerance(
                name=JOINTS[0], position=self.test_path_tolerance)]
        future = super().send_goal_async(goal, **kwargs)
        future.add_done_callback(lambda done: self.handles.append(done.result()))
        return future


class Probe(Node):
    """Reuse the production motion method without starting the tending FSM."""

    _move_carrier = MachineTendingCoordinator._move_carrier
    _wait_future = MachineTendingCoordinator._wait_future
    _cancel_bounded = MachineTendingCoordinator._cancel_bounded
    _fail_move = MachineTendingCoordinator._fail_move

    def __init__(self):
        super().__init__('task7_probe', namespace='cambot_testbed')
        self.mode = 'controller'
        self.plan = {
            'carrier': {'joint_names': list(JOINTS), 'goal_response_timeout_s': 3.0,
                        'result_margin_s': 3.0, 'feedback_timeout_s': 1.0},
            'stations': {'PROBE': {'carrier_joints': [0.1, -0.1, 0.1, 0.0, 0.0, 0.0]}},
        }
        self.feedback_count = 0
        self.feedback_joint_travel = 0.0
        self._last_feedback_positions = None
        self.carrier_motion_count = 0
        self.feedback_records = []
        self.joint_records = []
        self.client = RecordingClient(self)
        self.create_subscription(JointState, '/cambot_testbed/joint_states',
                                 self.joint_state, 10)

    def joint_state(self, msg):
        self.joint_records.append(dict(zip(msg.name, msg.position)))

    def _feedback(self, msg):
        feedback = msg.feedback
        assert list(feedback.joint_names) == list(JOINTS)
        assert len(feedback.actual.positions) == 6
        assert all(math.isfinite(x) for x in feedback.actual.positions)
        self.feedback_records.append({'actual': list(feedback.actual.positions),
                                      'desired': list(feedback.desired.positions),
                                      'error': list(feedback.error.positions)})
        MachineTendingCoordinator._feedback(self, msg)

    def wait(self, future, timeout=8.0):
        rclpy.spin_until_future_complete(self, future, timeout_sec=timeout)
        assert future.done() and future.result() is not None, 'future timed out'
        return future.result()

    def spin_for(self, seconds):
        end = time.monotonic() + seconds
        while time.monotonic() < end:
            rclpy.spin_once(self, timeout_sec=0.05)

    def raw_goal(self, names=JOINTS, duration=2, tolerance=None):
        goal = FollowJointTrajectory.Goal()
        goal.trajectory.joint_names = list(names)
        point = JointTrajectoryPoint()
        point.positions = [0.2] * len(names)
        point.time_from_start.sec = duration
        goal.trajectory.points = [point]
        if tolerance is not None:
            goal.path_tolerance = [JointTolerance(name=JOINTS[0], position=tolerance)]
        return goal

    def run_checks(self, report):
        assert self.client.wait_for_server(timeout_sec=30.0), 'controller not ready'
        service = self.create_client(ListControllers, '/cambot_testbed/controller_manager/list_controllers')
        assert service.wait_for_service(timeout_sec=5.0)
        controllers = self.wait(service.call_async(ListControllers.Request()))
        report['controllers'] = {c.name: c.state for c in controllers.controller}
        assert report['controllers']['ur5_trajectory_controller'] == 'active'
        assert report['controllers']['joint_state_broadcaster'] == 'active'
        self.spin_for(0.5)
        publishers = self.get_publishers_info_by_topic('/cambot_testbed/joint_states')
        report['joint_state_publishers'] = [p.node_name for p in publishers]
        assert report['joint_state_publishers'] == ['joint_state_broadcaster']
        assert self.joint_records and all(j in self.joint_records[-1] for j in JOINTS)
        assert self._move_carrier('PROBE', 2.0)
        handle = self.client.handles[-1]
        result = self.wait(handle.get_result_async())
        assert result.status == GoalStatus.STATUS_SUCCEEDED and result.result.error_code == 0
        self.spin_for(0.2)
        target = self.plan['stations']['PROBE']['carrier_joints']
        assert all(abs(self.joint_records[-1][j] - x) < 0.002 for j, x in zip(JOINTS, target))
        assert self.feedback_count > 0 and self.feedback_joint_travel > 0
        report['cases']['production_adapter_success'] = {
            'status': result.status, 'error_code': result.result.error_code,
            'feedback_samples': self.feedback_count, 'final_positions': self.joint_records[-1]}

        # A real controller rejects an invalid joint list before execution.
        handle = self.wait(self.client.send_goal_async(self.raw_goal(['unknown_joint'])))
        assert not handle.accepted
        report['cases']['invalid_joints_rejected'] = True
        self.plan['carrier']['joint_names'] = ['unknown_joint'] * 6
        assert not self._move_carrier('PROBE', 2.0)
        assert self.last_motion_failure == 'GOAL_REJECTED'
        self.plan['carrier']['joint_names'] = list(JOINTS)
        report['cases']['production_adapter_rejection'] = self.last_motion_failure

        # Impossible tracking tolerance produces an actual controller abort.
        handle = self.wait(self.client.send_goal_async(self.raw_goal(tolerance=1e-12)))
        assert handle.accepted
        result = self.wait(handle.get_result_async())
        assert result.status == GoalStatus.STATUS_ABORTED
        assert result.result.error_code == FollowJointTrajectory.Result.PATH_TOLERANCE_VIOLATED
        report['cases']['path_tolerance_abort'] = {
            'status': result.status, 'error_code': result.result.error_code}

        self.plan['stations']['PROBE']['carrier_joints'] = [-0.2] * 6
        self.client.test_path_tolerance = 1e-12
        assert not self._move_carrier('PROBE', 2.0)
        assert self.last_motion_failure == 'CONTROLLER_ERROR_-4'
        self.client.test_path_tolerance = None
        report['cases']['production_adapter_controller_error'] = self.last_motion_failure
        assert self.carrier_motion_count == 1

        self.plan['stations']['PROBE']['carrier_joints'] = [-0.1] * 6
        end = time.monotonic() + 0.5
        before = self.carrier_motion_count
        assert not self._move_carrier('PROBE', 5.0, lambda: time.monotonic() >= end)
        assert self.last_motion_failure == 'CANCEL_REQUEST_ACCEPTED'
        handle = self.client.handles[-1]
        result = self.wait(handle.get_result_async())
        assert result.status == GoalStatus.STATUS_CANCELED
        assert self.carrier_motion_count == before
        self.spin_for(0.2)
        held = self.joint_records[-1]
        self.spin_for(0.4)
        assert all(abs(held[j] - self.joint_records[-1][j]) < 1e-6 for j in JOINTS)
        report['cases']['production_adapter_cancel'] = {
            'status': result.status, 'cause': self.last_motion_failure, 'held_positions': held}

        # A deliberately impossible result deadline exercises the real timeout/cancel path.
        self.plan['carrier']['result_margin_s'] = -4.8
        assert not self._move_carrier('PROBE', 5.0)
        assert self.last_motion_failure == 'RESULT_TIMEOUT_CANCEL_REQUEST_ACCEPTED'
        result = self.wait(self.client.handles[-1].get_result_async())
        assert result.status == GoalStatus.STATUS_CANCELED
        assert self.carrier_motion_count == before
        report['cases']['production_adapter_timeout'] = {
            'status': result.status, 'cause': self.last_motion_failure,
            'note': 'test-only shortened deadline, not a production configuration'}

        missing = ActionClient(self, FollowJointTrajectory, '/cambot_testbed/absent/follow_joint_trajectory')
        assert not missing.wait_for_server(timeout_sec=0.5)
        missing.destroy()
        report['cases']['absent_server_bounded'] = True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    report = {'result': 'FAIL', 'scope': 'ros2_control GenericSystem mock only',
              'cases': {}, 'station_targets_validated': False,
              'physical_operation_verified': False, 'grasp_verified': False,
              'end_to_end_verified': False}
    rclpy.init()
    node = Probe()
    try:
        node.run_checks(report)
        report['result'] = 'PASS'
    finally:
        (args.output / 'result.json').write_text(json.dumps(report, indent=2) + '\n')
        (args.output / 'feedback.json').write_text(json.dumps(node.feedback_records) + '\n')
        (args.output / 'joint_states.json').write_text(json.dumps(node.joint_records) + '\n')
        node.destroy_node()
        rclpy.shutdown()
    print('TASK7_MOCK_CONTROLLER_PASS')


if __name__ == '__main__':
    main()
