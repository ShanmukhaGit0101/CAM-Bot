# UR5 Machine-Shop Carrier – Development Progress

## 1. Objective

Develop a Universal Robots UR5 industrial manipulator as the carrier arm
for the CAMBOT system.

The carrier is intended to operate in a machine-shop environment and
later carry/support the custom end-effector manipulator.

## 2. Environment

- Ubuntu 22.04
- ROS 2 Humble
- Gazebo
- MoveIt 2
- ros2_control
- Universal Robots ROS 2 packages
- UR5

## 3. UR5 Integration

The official Universal Robots ROS 2 packages were integrated into the
ROS 2 workspace.

The following packages were available:

- ur_description
- ur_bringup
- ur_calibration
- ur_controllers
- ur_moveit_config
- ur_robot_driver
- ur_simulation_gazebo

The UR5 was successfully visualized and simulated in Gazebo and RViz.

## 4. MoveIt Integration

MoveIt was successfully connected to the simulated UR5.

Verified interfaces included:

- `/move_action`
- `/execute_trajectory`
- `/joint_trajectory_controller/follow_joint_trajectory`

The MoveIt planning group used was:

`ur_manipulator`

The planning chain was:

`base_link → tool0`

## 5. ros2_control

The simulated UR5 was successfully controlled through:

`joint_trajectory_controller`

The controller was verified as active.

Joint states were received for all six UR5 joints:

- shoulder_pan_joint
- shoulder_lift_joint
- elbow_joint
- wrist_1_joint
- wrist_2_joint
- wrist_3_joint

## 6. Custom Tool

A custom test tool was attached to the UR5 using:

`ur5_with_test_tool.xacro`

The tool was connected to the robot through the `tool0` frame.

The URDF/Xacro model was validated and successfully integrated with the
UR5 simulation.

## 7. Machine-Shop Trajectory

A machine-shop operating sequence was developed using manually selected
joint configurations.

The sequence is:

HOME → P1 → HOME → P2 → HOME → P3 → HOME → P4 → HOME

Each station represents a different machine-shop working position.

The robot holds each station for approximately 3 seconds.

## 8. Experimentally Taught Positions

### HOME

```text
[ 0.000000,
 -1.570700,
  0.000000,
  0.000000,
  0.000000,
  0.000000 ]
