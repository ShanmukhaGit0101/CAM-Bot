from pathlib import Path

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch.substitutions import Command, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    trial_count = LaunchConfiguration("trial_count")
    visual_time_scale = LaunchConfiguration("visual_time_scale")
    config_file = LaunchConfiguration("config_file")
    results_file = LaunchConfiguration("results_file")
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

    # Visual-only: one joint-state publisher, with no controller or actuation.
    return LaunchDescription([
        DeclareLaunchArgument("trial_count", default_value="1"),
        DeclareLaunchArgument("visual_time_scale", default_value="1.0"),
        DeclareLaunchArgument("config_file", default_value=PathJoinSubstitution([
            FindPackageShare("carrier_control"), "config", "machine_tending.json"
        ])),
        DeclareLaunchArgument("results_file", default_value=str(
            Path.home() / ".ros" / "cambot" / "machine_tending_trials.csv"
        )),
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
                "mode": "visual_simulation",
                "config_file": config_file,
                "results_file": results_file,
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
