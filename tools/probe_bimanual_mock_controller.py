#!/usr/bin/env python3
"""Verify four-joint mock action/feedback; deliberately no gripper/grasp claim."""

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

from carrier_control.mock_controller_model import BIMANUAL_JOINTS, JOINTS


class BimanualProbe(Node):
    def __init__(self):
        super().__init__('task8_mock_probe', namespace='cambot_testbed')
        self.client = ActionClient(self, FollowJointTrajectory,
            '/cambot_testbed/bimanual_trajectory_controller/follow_joint_trajectory')
        self.positions = {}
        self.joint_time = None
        self.feedback = []
        self.active = None
        self.create_subscription(JointState, '/cambot_testbed/joint_states', self.state, 10)

    def state(self, message):
        assert len(message.name) == len(message.position)
        assert all(math.isfinite(x) for x in message.position)
        self.positions = dict(zip(message.name, message.position))
        self.joint_time = time.monotonic()

    def on_feedback(self, message):
        sample = message.feedback
        assert list(sample.joint_names) == list(BIMANUAL_JOINTS)
        assert len(sample.actual.positions) == 4
        assert all(math.isfinite(x) for x in sample.actual.positions)
        self.feedback.append({'received_monotonic': time.monotonic(),
                              'actual': list(sample.actual.positions),
                              'desired': list(sample.desired.positions)})

    def wait(self, future, timeout=5):
        rclpy.spin_until_future_complete(self, future, timeout_sec=timeout)
        assert future.done() and future.result() is not None, 'bounded wait timed out'
        return future.result()

    def spin(self, seconds):
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            rclpy.spin_once(self, timeout_sec=.02)

    def goal(self, target, duration=1.0, names=BIMANUAL_JOINTS, tolerance=None):
        request = FollowJointTrajectory.Goal()
        request.trajectory.joint_names = list(names)
        point = JointTrajectoryPoint()
        point.positions = [float(value) for value in target]
        point.time_from_start.sec = int(duration)
        point.time_from_start.nanosec = round((duration - int(duration)) * 1e9)
        request.trajectory.points = [point]
        if tolerance is not None:
            request.path_tolerance = [JointTolerance(name=BIMANUAL_JOINTS[0], position=tolerance)]
        self.active = self.wait(self.client.send_goal_async(request, feedback_callback=self.on_feedback))
        return self.active

    def cancel(self):
        response = self.wait(self.active.cancel_goal_async())
        assert response.goals_canceling, 'cancellation not accepted'
        result = self.wait(self.active.get_result_async())
        assert result.status == GoalStatus.STATUS_CANCELED
        self.spin(.2)
        held = self.positions.copy()
        self.spin(.3)
        assert all(abs(held[j] - self.positions[j]) < 1e-6 for j in BIMANUAL_JOINTS)
        return {'status': result.status, 'held_positions': {j: held[j] for j in BIMANUAL_JOINTS}}

    def run(self, report):
        assert self.client.wait_for_server(timeout_sec=30)
        service = self.create_client(ListControllers, '/cambot_testbed/controller_manager/list_controllers')
        assert service.wait_for_service(timeout_sec=5)
        controllers = self.wait(service.call_async(ListControllers.Request()))
        report['controllers'] = {c.name: c.state for c in controllers.controller}
        for name in ('joint_state_broadcaster', 'ur5_trajectory_controller', 'bimanual_trajectory_controller'):
            assert report['controllers'][name] == 'active'
        self.spin(.5)
        assert all(name in self.positions for name in JOINTS + BIMANUAL_JOINTS)
        assert time.monotonic() - self.joint_time < .5
        publishers = self.get_publishers_info_by_topic('/cambot_testbed/joint_states')
        assert [p.node_name for p in publishers] == ['joint_state_broadcaster']
        report['joint_state_publishers'] = [p.node_name for p in publishers]
        carrier_start = {j: self.positions[j] for j in JOINTS}
        target = [.15, -.1, -.15, .1]
        first_feedback = len(self.feedback)
        handle = self.goal(target)
        assert handle.accepted
        result = self.wait(handle.get_result_async())
        assert result.status == GoalStatus.STATUS_SUCCEEDED and result.result.error_code == 0
        self.spin(.1)
        assert time.monotonic() - self.joint_time < .5
        assert all(abs(self.positions[j] - x) < .002 for j, x in zip(BIMANUAL_JOINTS, target))
        samples = self.feedback[first_feedback:]
        assert len(samples) > 1
        assert any(max(s['actual'][i] for s in samples) - min(s['actual'][i] for s in samples) > .01
                   for i in range(4)), 'no observed motion feedback'
        report['cases']['four_joint_motion_feedback'] = {'status': result.status, 'feedback_samples': len(samples)}

        handle = self.goal([0], names=['not_a_joint'])
        assert not handle.accepted
        report['cases']['unknown_joint_rejected'] = True
        handle = self.goal([0] * 4, tolerance=1e-12)
        assert handle.accepted
        result = self.wait(handle.get_result_async())
        assert result.status == GoalStatus.STATUS_ABORTED and result.result.error_code == -4
        report['cases']['tracking_fault_aborted'] = {'status': result.status, 'error_code': result.result.error_code}

        handle = self.goal([-.15, .1, .15, -.1], duration=5)
        assert handle.accepted
        self.spin(.3)
        report['cases']['cancellation_and_hold'] = self.cancel()

        handle = self.goal(target, duration=5)
        assert handle.accepted
        future = handle.get_result_async()
        rclpy.spin_until_future_complete(self, future, timeout_sec=.2)
        assert not future.done(), 'five-second motion unexpectedly finished within deadline'
        report['cases']['deadline_cancel_and_hold'] = self.cancel()
        # Recovery only after terminal cancellation; no reset of physical faults implied.
        handle = self.goal([0.0] * 4)
        assert handle.accepted
        result = self.wait(handle.get_result_async())
        assert result.status == GoalStatus.STATUS_SUCCEEDED and result.result.error_code == 0
        self.spin(.1)
        assert all(abs(self.positions[j]) < .002 for j in BIMANUAL_JOINTS)
        assert all(abs(self.positions[j] - carrier_start[j]) < 1e-6 for j in JOINTS)
        report['cases']['recovery_and_carrier_isolation'] = {'status': result.status, 'carrier_positions': carrier_start}
        missing = ActionClient(self, FollowJointTrajectory, '/cambot_testbed/absent_bimanual/follow_joint_trajectory')
        assert not missing.wait_for_server(timeout_sec=.5)
        missing.destroy()
        report['cases']['absent_server_bounded'] = True
        report['final_positions'] = self.positions


def main(output):
    output.mkdir(parents=True, exist_ok=False)
    report = {'scope': 'four-joint GenericSystem controller protocol only', 'cases': {},
              'gripper_interface_available': False, 'grasp_verified': False,
              'physical_actuation_verified': False, 'complete_tending_cycle_verified': False,
              'passed': False}
    rclpy.init()
    node = BimanualProbe()
    try:
        node.run(report)
        report['passed'] = True
    except BaseException as error:
        report['error'] = repr(error)
        raise
    finally:
        # Keep failures and partial observations as well as successful runs.
        (output / 'result.json').write_text(json.dumps(report, indent=2) + '\n')
        (output / 'feedback.json').write_text(json.dumps(node.feedback, indent=2) + '\n')
        node.destroy_node()
        rclpy.shutdown()
    print('TASK8_BIMANUAL_MOCK_PROTOCOL_PASS (no gripper or grasp verification)')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    main(parser.parse_args().output)
