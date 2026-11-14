"""Isolated UR5 mock controller; no station execution or hardware driver."""

from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import EmitEvent, RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.events import Shutdown
from launch_ros.actions import Node

from carrier_control.mock_controller_model import mock_control_description
from carrier_control.workcell_model import render_workcell_xacro
from carrier_control.workflow import load_plan


def generate_launch_description():
    """Start actual ros2_control controllers backed only by GenericSystem."""
    description_share = Path(get_package_share_directory('carrier_description'))
    control_share = Path(get_package_share_directory('carrier_control'))
    plan = load_plan(control_share / 'config/machine_tending.json')
    description = mock_control_description(render_workcell_xacro(
        description_share / 'urdf/ur5_with_test_tool.xacro', plan['workcell']))
    manager = Node(
        package='controller_manager', executable='ros2_control_node',
        namespace='cambot_testbed', output='screen',
        parameters=[{'robot_description': description},
                    str(Path(get_package_share_directory('carrier_controller_testbed')) /
                        'config/ur5_mock_controllers.yaml')],
    )
    broadcaster = Node(
        package='controller_manager', executable='spawner', output='screen',
        arguments=['joint_state_broadcaster', '-c', '/cambot_testbed/controller_manager',
                   '--controller-manager-timeout', '30'],
    )
    trajectory = Node(
        package='controller_manager', executable='spawner', output='screen',
        arguments=['ur5_trajectory_controller', '-c', '/cambot_testbed/controller_manager',
                   '--controller-manager-timeout', '30'],
    )

    def broadcaster_exit(event, context):
        if event.returncode != 0:
            return [EmitEvent(event=Shutdown(reason='broadcaster activation failed'))]
        return [trajectory]

    def trajectory_exit(event, context):
        if event.returncode != 0:
            return [EmitEvent(event=Shutdown(reason='trajectory activation failed'))]
        return []

    return LaunchDescription([
        RegisterEventHandler(OnProcessExit(target_action=manager, on_exit=[
            EmitEvent(event=Shutdown(reason='controller manager exited'))])),
        RegisterEventHandler(OnProcessExit(
            target_action=broadcaster, on_exit=broadcaster_exit)),
        RegisterEventHandler(OnProcessExit(
            target_action=trajectory, on_exit=trajectory_exit)),
        manager,
        Node(package='robot_state_publisher', executable='robot_state_publisher',
             namespace='cambot_testbed', output='screen',
             parameters=[{'robot_description': description}]),
        broadcaster,
    ])
