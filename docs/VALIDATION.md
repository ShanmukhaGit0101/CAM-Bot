# Validation procedure

## Offline checks

These checks are valid without ROS and establish only **STATIC VALID** evidence:

```bash
PYTHONPATH=src/carrier_control python3 -m unittest \
  src/carrier_control/test/test_workflow.py \
  src/carrier_control/test/test_metrics.py \
  src/carrier_control/test/test_action_safety.py -v
python3 -m unittest \
  src/carrier_description/test/test_cell_model.py \
  src/carrier_description/test/test_launch_contract.py -v
python3 -m compileall -q \
  src/carrier_control/carrier_control src/carrier_description/launch
python3 tools/verify_ay.py --output artifacts/verification/ay_verification.json
```

The generated JSON contains legacy offline component checks created before the
PDF-defined AY mapping was supplied. It is useful static evidence but is not
AY-01…AY-13 acceptance evidence. The current runtime gate is recorded in
`artifacts/verification/first_execution_gate.json`.

## ROS 2 Humble static checks

Run in a sourced Humble workspace; these commands were not available in the
implementation shell:

```bash
timeout 120s colcon build --symlink-install
source install/setup.bash
xacro $(ros2 pkg prefix carrier_description)/share/carrier_description/urdf/ur5_with_test_tool.xacro > /tmp/cambot.urdf
check_urdf /tmp/cambot.urdf
timeout 20s ros2 launch carrier_description dual_arm_demo.launch.py \
  mode:=visual_simulation visual_time_scale:=0.05
```

The last command is a visual simulation check, not Gazebo actuation.

## Controller-mode gate and five-trial run

Before changing `controller_validated` to `true`, teach each named target against
the actual cell, add the missing S5 target, and review the mapping. Then start the
selected UR5 simulation/controller stack and verify the action exists:

```bash
timeout 10s ros2 action info \
  /joint_trajectory_controller/follow_joint_trajectory
timeout 10s ros2 topic hz /joint_states
```

Run five trials only after both commands show the expected controller and stream:

```bash
timeout 300s ros2 launch carrier_description dual_arm_demo.launch.py \
  mode:=controller trial_count:=5
```

Inspect the CSV and state topics. Carrier movement may be marked **RUNTIME
VERIFIED** only when every carrier action has a successful result and actual
position feedback. The overall cycle remains below **END-TO-END VERIFIED** while
the bimanual module has no selected controller/feedback interface.

Failure tests include an unavailable action server, rejected goal, result
timeout, missing feedback, discontinuous workpiece state, and invalid or
unvalidated station configuration. In each case the coordinator must publish or
log failure, stop the cycle, and must not advance the workpiece state for the
failed step.

