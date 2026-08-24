# UR5 Machine-Shop Carrier

Part of the **CAMBOT** project.

This module implements a **Universal Robots UR5** as the carrier
manipulator for a machine-shop simulation using:

- ROS 2 Humble
- Gazebo
- MoveIt 2
- ros2_control
- RViz

## What is implemented

- UR5 Gazebo simulation
- MoveIt motion planning
- RViz interactive control
- Joint trajectory control
- Manual waypoint teaching
- Four machine-shop positions
- Automated machine-shop cycle

## Machine-Shop Cycle

```text
HOME → P1 → HOME → P2 → HOME → P3 → HOME → P4 → HOME
```

Each station is held for approximately **3 seconds**.

## Package Structure

```text
UR5_Machine_Shop/
├── README.md
├── carrier_description/
├── carrier_control/
├── config/
│   └── waypoints.yaml
└── docs/
    └── progress.md
```

## Requirements

- Ubuntu 22.04
- ROS 2 Humble
- Gazebo
- MoveIt 2
- Universal Robots ROS 2 packages

## Setup

Create a ROS 2 workspace:

```bash
mkdir -p ~/tops_ws/src
cd ~/tops_ws/src
```

Copy these packages into the workspace:

```text
carrier_description
carrier_control
```

Then install dependencies:

```bash
cd ~/tops_ws
rosdep install --from-paths src --ignore-src -r -y
```

Build:

```bash
colcon build --symlink-install
source install/setup.bash
```

## Running

Start the UR5 Gazebo simulation and MoveIt/RViz configuration.

Then run the machine-shop cycle:

```bash
ros2 run carrier_control machine_shop_joint_cycle
```

The robot follows:

```text
HOME
 ↓
P1
 ↓
HOME
 ↓
P2
 ↓
HOME
 ↓
P3
 ↓
HOME
 ↓
P4
 ↓
HOME
```

## Waypoints

The experimentally taught joint configurations are stored in:

```text
config/waypoints.yaml
```

| Position | Purpose |
|---|---|
| HOME | Standby configuration |
| P1 | Machine station 1 |
| P2 | Machine station 2 |
| P3 | Machine station 3 |
| P4 | Machine station 4 |

The positions were obtained by manually positioning the UR5 using
MoveIt's RViz interactive control and reading the resulting
`/joint_states`.

## Documentation

Development details are available in:

```text
docs/progress.md
```

## Future Work

- Attach the actual bin manipulator
- Add machine-shop collision objects
- Add payload modelling
- Integrate carrier and bin-manipulator control
- Develop coordinated manipulation tasks
