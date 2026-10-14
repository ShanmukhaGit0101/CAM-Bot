from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch.substitutions import Command, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    mode = LaunchConfiguration("mode")
    trial_count = LaunchConfiguration("trial_count")
    visual_time_scale = LaunchConfiguration("visual_time_scale")
    xacro_file = PathJoinSubstitution([
        FindPackageShare("carrier_description"), "urdf", "ur5_with_test_tool.xacro"
    ])
    rviz_config = PathJoinSubstitution([
        FindPackageShare("carrier_description"), "rviz", "dual_arm.rviz"
    ])
    description = ParameterValue(
        Command(["xacro ", xacro_file, " include_workcell:=true"]),
        value_type=str,
    )

    # Do not launch a second joint-state publisher. In visual mode the coordinator
    # publishes explicitly labelled visual positions; in controller mode the
    # external controller owns carrier feedback.
    return LaunchDescription([
        DeclareLaunchArgument(
            "mode",
            default_value="visual_simulation",
            description=(
                "visual_simulation or controller; controller requires an external "
                "active trajectory controller and validated targets"
            ),
        ),
        DeclareLaunchArgument("trial_count", default_value="1"),
        DeclareLaunchArgument("visual_time_scale", default_value="1.0"),
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            name="robot_state_publisher",
            output="screen",
            parameters=[{"robot_description": description}],
        ),
        Node(
            package="carrier_control",
            executable="machine_tending_coordinator",
            name="machine_tending_coordinator",
            output="screen",
            parameters=[{
                "mode": mode,
                "trial_count": trial_count,
                "visual_time_scale": visual_time_scale,
            }],
        ),
        Node(
            package="rviz2",
            executable="rviz2",
            name="rviz2",
            output="screen",
            arguments=["-d", rviz_config],
        ),
    ])
