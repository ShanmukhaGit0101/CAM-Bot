from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import Command, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    xacro_file = PathJoinSubstitution([
        FindPackageShare("carrier_description"), "urdf", "ur5_with_test_tool.xacro"
    ])
    rviz_config = PathJoinSubstitution([
        FindPackageShare("carrier_description"), "rviz", "dual_arm.rviz"
    ])
    description = ParameterValue(Command(["xacro ", xacro_file]), value_type=str)

    # IMPORTANT: do not launch joint_state_publisher_gui here. dual_arm_cycle
    # is the single /joint_states publisher for both UR5-at-home and custom joints.
    return LaunchDescription([
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            name="robot_state_publisher",
            output="screen",
            parameters=[{"robot_description": description}],
        ),
        Node(
            package="carrier_control",
            executable="dual_arm_cycle",
            name="dual_arm_cycle",
            output="screen",
        ),
        Node(
            package="rviz2",
            executable="rviz2",
            name="rviz2",
            output="screen",
            arguments=["-d", rviz_config],
        ),
    ])
