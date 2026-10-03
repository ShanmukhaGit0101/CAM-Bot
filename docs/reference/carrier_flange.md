# CAM-BOT Phase 4 — Carrier Flange Interface

## Purpose

The carrier flange is the custom interface below the official UR5 `tool0` frame and
above the future bimanual module.

```text
wrist_3_link
  -> flange
  -> tool0
  -> carrier_flange
  -> carrier_flange_interface
  -> dual_arm_base_link
```

The official UR5 description remains untouched above `tool0`.

## Xacro parameters

| Parameter | Unit | Status |
|---|---|---|
| `flange_length` | m | reconstruction value |
| `flange_width` | m | reconstruction value |
| `flange_thickness` | m | reconstruction value |
| `mount_spacing` | m | reconstruction value |
| `mount_height` | m | reconstruction value |
| `tilt_angle` | rad | reconstruction value |

The project documentation establishes these parameter names and the interface
contract. The original final numerical flange dimensions were not recoverable from
the repository history. Therefore the values used by this reconstruction must not
be described as the historical mechanical design.

Current reconstruction defaults:

```text
flange_length     = 0.60 m
flange_width      = 0.40 m
flange_thickness  = 0.05 m
mount_spacing     = 0.25 m
mount_height      = 0.06 m
tilt_angle        = 0.00 rad
```

## Fixed joints

- `tool0_to_carrier_flange`
- `carrier_flange_to_interface`
- `carrier_flange_interface_to_dual_arm_base`

## Bimanual placeholder

The placeholder has four controllable joints:

- `left_shoulder_joint` — Z axis
- `left_elbow_joint` — X axis
- `right_shoulder_joint` — Z axis
- `right_elbow_joint` — X axis

The motion node synchronizes the four joints with a cubic easing profile at about
50 Hz. This is a predefined visualization/reachability motion, not closed-chain
bimanual manipulation or force-controlled grasping.

## Launch

```bash
ros2 launch carrier_description dual_arm_demo.launch.py
```

The launch intentionally does **not** start `joint_state_publisher_gui`, because
`dual_arm_cycle` is the sole `/joint_states` publisher in the demo launch.
