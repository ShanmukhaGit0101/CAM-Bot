# Four-joint bimanual mock controller

The Task-7 testbed can optionally control the existing four placeholder joints
through a second real Humble `JointTrajectoryController`, backed by
`mock_components/GenericSystem`. Enable it with:

```bash
ros2 launch carrier_controller_testbed ur5_mock_controller.launch.py enable_bimanual_mock:=true
```

The default remains the six-joint UR5 testbed. Both controllers share one
joint-state broadcaster in `/cambot_testbed`; the bimanual action is
`/cambot_testbed/bimanual_trajectory_controller/follow_joint_trajectory`.
No physical driver, gripper joint, grasp detector, station-validity flag or
production FSM behavior is added or changed. The description helper preserves
all kinematic origins, joints and collision shapes. Controller activation is
sequenced after the carrier controller; a failed spawner shuts down the launch.

Use the image/build procedure in [TASK7_CONTROLLER.md](TASK7_CONTROLLER.md),
then substitute the runner command below, using an unused domain and a new
output directory:

```bash
CAMBOT_RUN_BIMANUAL=1 bash tools/run_ur5_mock_controller.sh /evidence/NEW_REPLAY
```

The runner first repeats all eight carrier protocol checks, then runs seven
bimanual checks: successful four-joint motion with observed position feedback,
unknown-joint rejection, tracking-tolerance abort, cancellation with held state,
a deliberately short result deadline followed by cancellation, subsequent
recovery with the carrier held unchanged, and bounded absence of a server.
It checks one broadcaster, controller activation, clean launch shutdown and an
empty residual graph. The probe retains results and received feedback even if
an assertion fails; the runner stops its launch on failure.

These are small synthetic test vectors, not the demo's station/grasp poses.
GenericSystem copies commands to state; this is neither measured encoder feedback
nor a physics model. A successful action does not imply an object was grasped.
Task 8 still needs selected actuator/gripper interfaces, fresh sensor-based
object/grasp/release confirmation, fault semantics and hardware validation.
The production tending gate still refuses unsupported manipulation.
