# UR5 Machine-Shop Carrier

This module is part of the CAMBOT project.

It implements a Universal Robots UR5 as a carrier manipulator for a
machine-shop simulation using ROS 2 Humble, Gazebo, MoveIt and ros2_control.

## What is implemented

- UR5 Gazebo simulation
- MoveIt integration
- RViz interactive control
- Joint trajectory control
- Four manually taught machine-shop positions
- Automated machine-shop cycle

## Machine-Shop Cycle

```text
HOME → P1 → HOME → P2 → HOME → P3 → HOME → P4 → HOME

