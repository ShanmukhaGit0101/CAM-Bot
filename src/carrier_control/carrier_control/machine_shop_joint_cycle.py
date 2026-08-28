#!/usr/bin/env python3

import time

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

from control_msgs.action import FollowJointTrajectory
from trajectory_msgs.msg import JointTrajectoryPoint


class MachineShopJointCycle(Node):

    def __init__(self):

        super().__init__('machine_shop_joint_cycle')

        # =====================================================
        # UR5 JOINT ORDER
        # =====================================================

        self.joint_names = [
            'shoulder_pan_joint',
            'shoulder_lift_joint',
            'elbow_joint',
            'wrist_1_joint',
            'wrist_2_joint',
            'wrist_3_joint'
        ]

        # =====================================================
        # CONTROLLER ACTION
        # =====================================================

        self.client = ActionClient(
            self,
            FollowJointTrajectory,
            '/joint_trajectory_controller/follow_joint_trajectory'
        )

        self.get_logger().info(
            'Waiting for joint trajectory controller...'
        )

        if not self.client.wait_for_server(
            timeout_sec=10.0
        ):

            self.get_logger().error(
                'Joint trajectory controller not available.'
            )

            raise RuntimeError(
                'Controller action unavailable'
            )

        self.get_logger().info(
            'Connected to joint trajectory controller.'
        )

    # =========================================================
    # MOVE TO JOINT CONFIGURATION
    # =========================================================

    def move_to(
        self,
        name,
        joints,
        move_time=2.0
    ):

        self.get_logger().info('')
        self.get_logger().info(
            '=========================================='
        )
        self.get_logger().info(
            f'MOVING TO {name}'
        )
        self.get_logger().info(
            '=========================================='
        )

        goal = FollowJointTrajectory.Goal()

        trajectory = goal.trajectory

        trajectory.joint_names = self.joint_names

        # -----------------------------------------------------
        # TARGET POINT
        # -----------------------------------------------------

        point = JointTrajectoryPoint()

        point.positions = joints

        point.velocities = [0.0] * 6

        point.accelerations = [0.0] * 6

        point.time_from_start.sec = int(move_time)

        point.time_from_start.nanosec = int(
            (move_time - int(move_time)) * 1e9
        )

        trajectory.points.append(point)

        # -----------------------------------------------------
        # SEND
        # -----------------------------------------------------

        send_future = self.client.send_goal_async(
            goal
        )

        rclpy.spin_until_future_complete(
            self,
            send_future
        )

        goal_handle = send_future.result()

        if not goal_handle.accepted:

            self.get_logger().error(
                f'{name}: trajectory rejected.'
            )

            return False

        self.get_logger().info(
            f'{name}: trajectory accepted.'
        )

        # -----------------------------------------------------
        # WAIT FOR RESULT
        # -----------------------------------------------------

        result_future = (
            goal_handle.get_result_async()
        )

        rclpy.spin_until_future_complete(
            self,
            result_future
        )

        result = result_future.result().result

        # -----------------------------------------------------
        # CONTROLLER RESULT
        # -----------------------------------------------------

        if result.error_code == 0:

            self.get_logger().info(
                f'{name}: motion completed successfully.'
            )

            return True

        self.get_logger().error(
            f'{name}: controller error '
            f'{result.error_code}'
        )

        return False

    # =========================================================
    # HOLD
    # =========================================================

    def dwell(
        self,
        name,
        seconds=3.0
    ):

        self.get_logger().info(
            f'{name}: holding for '
            f'{seconds:.1f} seconds.'
        )

        time.sleep(seconds)

    # =========================================================
    # MACHINE SHOP CYCLE
    # =========================================================

    def run_cycle(self):

        # =====================================================
        # HOME
        # =====================================================

        HOME = [
             0.0,
            -1.5707,
             0.0,
             0.0,
             0.0,
             0.0
        ]

        # =====================================================
        # P1
        # =====================================================

        P1 = [
             3.5930650931,
            -2.2054793584,
            -1.0675882483,
             0.1313373823,
             1.2420101306,
            -4.7123874695
        ]

        # =====================================================
        # P2
        # =====================================================

        P2 = [
            -2.9731800422,
            -1.0697884970,
             0.4051854970,
            -2.4787475769,
            -1.7109676751,
            -0.0003444654
        ]

        # =====================================================
        # P3
        # =====================================================

        P3 = [
            -0.4911844575,
            -1.2432532203,
             1.0138335850,
            -2.9107543219,
            -1.5139363170,
            -0.0006938361
        ]

        # =====================================================
        # P4
        # =====================================================

        P4 = [
            -1.9124223037,
            -1.1707189683,
             1.5631410256,
            -3.5347189241,
            -1.7280385900,
            -0.0015613844
        ]

        # =====================================================
        # STATIONS
        # =====================================================

        stations = [
            ('P1', P1),
            ('P2', P2),
            ('P3', P3),
            ('P4', P4)
        ]

        # =====================================================
        # INITIAL HOME
        # =====================================================

        if not self.move_to(
            'HOME',
            HOME,
            move_time=2.0
        ):
            return

        self.dwell(
            'HOME',
            3.0
        )

        # =====================================================
        # MACHINE SHOP CYCLE
        # =====================================================

        for name, configuration in stations:

            # -------------------------------------------------
            # HOME → STATION
            # -------------------------------------------------

            if not self.move_to(
                name,
                configuration,
                move_time=2.0
            ):

                self.get_logger().error(
                    f'Cycle stopped at {name}.'
                )

                return

            # -------------------------------------------------
            # STATION HOLD
            # -------------------------------------------------

            self.dwell(
                name,
                3.0
            )

            # -------------------------------------------------
            # STATION → HOME
            # -------------------------------------------------

            if not self.move_to(
                'HOME',
                HOME,
                move_time=2.0
            ):

                self.get_logger().error(
                    f'Failed to return HOME after {name}.'
                )

                return

            # -------------------------------------------------
            # HOME HOLD
            # -------------------------------------------------

            self.dwell(
                'HOME',
                3.0
            )

        # =====================================================
        # COMPLETE
        # =====================================================

        self.get_logger().info('')
        self.get_logger().info(
            '=========================================='
        )
        self.get_logger().info(
            ' MACHINE SHOP CYCLE COMPLETE'
        )
        self.get_logger().info(
            '=========================================='
        )


# =============================================================
# MAIN
# =============================================================

def main(args=None):

    rclpy.init(args=args)

    node = MachineShopJointCycle()

    try:

        node.run_cycle()

    except KeyboardInterrupt:

        node.get_logger().warn(
            'Cycle interrupted by user.'
        )

    finally:

        node.destroy_node()

        rclpy.shutdown()


if __name__ == '__main__':

    main()
