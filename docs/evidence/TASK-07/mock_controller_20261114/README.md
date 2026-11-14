# Task-7 mock controller verification

Agent-run 2026-11-14. **PASS for isolated ros2_control mock integration.**
No human review, physical robot, calibrated station validation, grasp or full
controller-backed tending cycle is claimed by this record.

## Exact final replay

- Fresh GitHub clone of `feat/ur5-mock-controller` at
  `3aa65beb6d758a28da1524a0042b76747586575d`.
- Image: `sha256:2e84a6c6578634cfd3983b7968ea19a793213e18dcb62689a5b170ff06d01856`.
  [Build log](image-build.log); the Dockerfile in the tested commit pins the ROS
  base digest. The image recipe is identical to the one built before commit.
- Ubuntu 22.04 / ROS Humble, isolated domain 118, localhost-only discovery.
- Controller manager/hardware interface 2.54.3, trajectory controller and
  broadcaster 2.54.1, UR description 2.14.0. Full apt revisions are in
  [environment.txt](clean_replay/replay/environment.txt).
- Three selected packages built from scratch: carrier_control,
  carrier_description, carrier_controller_testbed. No stale build/install tree
  was copied into this checkout. [Build](clean_replay/build.log).
- Clean tracked tree before and after the replay:
  [initial status](clean_replay/initial-status.txt),
  [final status](clean_replay/final-status.txt).

Commands are documented in [Task 7](../../../TASK7_CONTROLLER.md). After the
scoped build, `colcon test --base-paths src --packages-select carrier_control
carrier_description carrier_controller_testbed --executor sequential
--return-code-on-test-failure` passed. [Result](clean_replay/test-results.log):
**73 tests, 0 errors, 0 failures, 2 skipped** (existing copyright checks).
The optional package has no separate pytest suite; its installed launch/config
are exercised by the live runner. The three new pure unit tests cover URDF
preservation, physical-driver removal and malformed-description rejection.

`python3 tools/check_ay13_docs.py --installed` passed, including source inventory
and installed core assets. [Log](clean_replay/docs.log).
`bash tools/run_ur5_mock_controller.sh /evidence/replay` passed all eight cases:

| Case | Result |
|---|---|
| Production motion method | SUCCEEDED status (4), error code 0, actual-position feedback and final joint agreement. |
| Direct invalid joint goal | Rejected. |
| Production invalid joint goal | GOAL_REJECTED; no success reported. |
| Direct tracking fault | ABORTED status (6), PATH_TOLERANCE_VIOLATED (-4). |
| Production tracking fault | CONTROLLER_ERROR_-4; success count unchanged. |
| Production cancellation | Accepted, terminal CANCELED status (5), stable subsequent mock state. |
| Production result timeout | Cancellation accepted and terminal CANCELED status (5). |
| Absent action server | Bounded unsuccessful readiness check. |

[Structured result](clean_replay/replay/probe/result.json),
[action feedback](clean_replay/replay/probe/feedback.json),
[joint-state samples](clean_replay/replay/probe/joint_states.json),
[runner](clean_replay/runner.log), and [launch log](clean_replay/replay/launch.log)
are retained. ERROR messages for deliberately rejected, aborted, cancelled and
timed-out goals are expected probe outcomes, not unreported test failures.

Both controllers were active; the only joint-state publisher was
`joint_state_broadcaster`. Controller manager and RSP exited cleanly without
escalation. [Initial nodes](clean_replay/replay/preexisting_nodes.txt) and
[residual nodes](clean_replay/replay/residual_nodes.txt) are empty. The owned
test containers were stopped after inspection.

A separate comparison of the actual expanded URDF, excluding only its
`ros2_control` block, proved all kinematic structure unchanged. The new block
contains only GenericSystem and no robot IP. [Result](clean_replay/model-check.json),
[expanded mock model](clean_replay/mock.urdf).

## Diagnostics retained

The diagnostics directory records intermediate, uncommitted development runs;
their exact intermediate source trees were not archived and must not be
identified as the final tested commit.

- The initial exec attempt preceded container readiness; the next stopped on
  Git's bind-mount ownership check before launch. Exact-path safe.directory
  configuration resolved it.
- Run 02 rejected the existing control block emitted by ur_description. The
  helper was corrected to replace it completely with mock interfaces, with a
  new regression test; no physical driver was started in that failed attempt.
- Run 03's second fault injection did not move the tolerance-constrained joint,
  so the correct controller response was success and the test assertion failed.
  Changing that synthetic target made the intended tracking fault meaningful.
- Run 04 passed the eight cases before the final optional-package relocation.
- Four style errors in the new test file were fixed; the failed style report
  and subsequent passing results are retained. The fresh final replay is the
  authoritative execution above.

The [manifest](manifest.json) hashes all retained files except itself. Existing
AY-13 and experimental archives were not rewritten. Production coordinator,
FSM, reachability, configuration and UR5 kinematics are unchanged. Task 7's
robot-specific driver selection, safety/state handling and hardware validation
remain open; Task 6's inputs and Task 8's manipulation feedback are still needed
before complete controller-backed tending can be demonstrated.
