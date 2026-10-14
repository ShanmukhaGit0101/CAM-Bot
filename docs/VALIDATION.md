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
  visual_time_scale:=0.05
```

The last command is a visual simulation check, not Gazebo actuation.

For the five-station cell, run
`PYTHONPATH=src/carrier_control python3 -m unittest
src/carrier_control/test/test_workcell_contract.py -v` for positive and
failure-path config/transform tests. In Humble, run
`bash tools/capture_ay04_humble.sh` to expand/check the configured URDF,
inspect station TF frames and workpiece state, and capture an RViz screenshot.
The supplied cell geometry is temporary simulation-only, and no screenshot or
TF runtime evidence was available on the implementation host.

## Controller-mode gate and five-trial run

Before changing `controller_validated` to `true`, teach each named target against
the actual cell, add the missing S5 target, and review the mapping. Supply a
single selected ROS launch file that starts the UR5 trajectory controller and
its joint-state broadcaster, without a second robot-state publisher or a
publisher of fabricated UR5 positions. The gated entry point includes that
file and waits for both the action server and a complete UR5 `/joint_states`
sample before proceeding:

```bash
timeout 10s ros2 action info \
  /joint_trajectory_controller/follow_joint_trajectory
timeout 10s ros2 topic hz /joint_states
```

Run five trials only after both commands show the expected controller and stream:

```bash
timeout 300s ros2 launch carrier_description machine_tending_controller.launch.py \
  controller_bringup_file:=/absolute/path/to/selected_controller.launch.py \
  config_file:=/absolute/path/to/validated_machine_tending.json trial_count:=5
```

Inspect the CSV and state topics. Carrier movement may be marked **RUNTIME
VERIFIED** only when every carrier action has a successful result and actual
position feedback. The overall cycle remains below **END-TO-END VERIFIED** while
the bimanual module has no selected controller/feedback interface.

The current repository cannot pass this run: there is no selected controller
bring-up file, S1–S4 are unvalidated mappings, and S5 lacks a taught carrier
target. Use `bash tools/capture_ay03_humble.sh` in a sourced Ubuntu 22.04/Humble
GUI session for three visual launch/stop checks and the default fail-closed
controller check. Do not label those visual trials as controlled motion.

## AY-05 FSM checks

The offline FSM tests cover ordered transitions, one-shot success, reset,
invalid lifecycle, state timeout, zero retry, cancellation, and a failed
`LOAD_MACHINE` step with no later state or workpiece advance:

```bash
PYTHONPATH=src/carrier_control python3 -m unittest \
  src/carrier_control/test/test_machine_tending_fsm.py -v
```

In a sourced Ubuntu 22.04/Humble GUI workspace, run
`bash tools/capture_ay05_humble.sh`. It launches the **visual-only** coordinator
in manual-start mode for three cases: successful one-shot, injected `S3_LOAD`
failure, and early cancel. Its observer records trial IDs, timestamps, state
order, terminal event, and workpiece topic updates. It does not simulate a
trajectory controller or prove physical picking/placing. Controller-mode FSM
integration remains blocked by AY-03's missing controller stack and validated
station targets.

Failure tests include an unavailable action server, rejected goal, result
timeout, missing feedback, discontinuous workpiece state, and invalid or
unvalidated station configuration. In each case the coordinator must publish or
log failure, stop the cycle, and must not advance the workpiece state for the
failed step.

