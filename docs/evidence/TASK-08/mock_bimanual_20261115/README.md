# Four-joint mock and carrier regression evidence — 2026-11-15 UTC

Agent-run verification of source `44febde` (full SHA in `source-commit.txt`).
This is not a human acceptance record or physical operation. The existing image
in `image-id.txt` was reused; the unchanged Docker recipe was not rebuilt.

## Checkout and commands

A fresh **local clone** at `/workspace/CAM-BOT-task8-clone` was created from the
feature branch with `git clone --no-hardlinks`. LFS objects were copied from the
existing local object store and materialized with `git lfs checkout`. This is
not a fresh GitHub download or a new independent human reproduction. Clean
before/after status files are retained. The clone was mounted into a new
Humble container at `/workspace/CAM-BOT`, with domain 119 and localhost-only ROS.

An initial detached-worktree container could not resolve its host `.git`
reference; it stopped before building or testing. Its diagnostic is retained in
`worktree-mount-failure.log`. The local clone resolved this mount issue.

Inside the container, using `/ros_entrypoint.sh`:

```bash
colcon build --base-paths src --symlink-install --executor sequential \
  --packages-select carrier_control carrier_description carrier_controller_testbed
source install/setup.bash
colcon test --base-paths src --executor sequential --return-code-on-test-failure \
  --packages-select carrier_control carrier_description carrier_controller_testbed
colcon test-result --verbose
python3 tools/check_ay13_docs.py --installed
python3 -m unittest tools.test_ay05_ros_probe -v
CAMBOT_RUN_BIMANUAL=1 CAMBOT_RUN_BENCHMARK=1 \
  bash tools/run_ur5_mock_controller.sh /evidence/combined
bash tools/run_ur5_mock_controller.sh /evidence/carrier-default
```

## Observed results

- All three packages built. **75 package results, 0 errors, 0 failures, 2 skips**
  (existing copyright-header opt-outs in the two core packages). Optional testbed package has no separate
  package unit tests; its actual launch is covered by the runtime probes.
- Installed documentation/assets check passed. Fresh model expansion matched all
  30 joint elements and all five module collision elements in the archived study
  input (`model-contract.json`); the expanded model is retained.
- **8 carrier + 7 bimanual checks passed** in `combined/`; both controllers and
  the broadcaster active, one authoritative ten-joint state publisher.
- **8 carrier checks passed** again with bimanual disabled in `carrier-default/`.
- Both launches stopped manager/RSP cleanly; empty preexisting and residual
  graph records are retained. Expected rejection/tolerance/cancellation errors
  are deliberately exercised and are not successful motion outcomes.
- **20/20 synthetic carrier cycles passed**, zero attempted failures. Mean
  duration 1.1598969500000293 s; sample SD 0.0005524682677081234 s. Full CSV,
  boundary definition and summary are under `combined/benchmark/`. These are
  not complete tending cycles and do not close Task 13.
- Host Python 3.12 offline tool suite: **42 passed** (`tool-tests.log`), including
  nine new geometry tests and two package-discovery regressions. The seven
  ROS-dependent observer tests were run separately in Humble and **passed**
  (`ros-tool-tests.log`); they were not silently skipped on the host.
- Historical analysis tests: **14 passed** (`analysis-tests.log`). CAD tests:
  **4 passed** (`cad-tests.log`). Geometry analysis results are retained in the
  [separate study](../../../../experiments/workspace/runs/placeholder-feasibility-20261115/README.md).

The offline tests and geometry study ran in a clean detached worktree of the
same exact commit before the container mount issue was discovered. The actual
ROS build/runtime replay ran in the separate local clone. Both reference the
same committed code; neither is called an independent reviewer run.

## Failures preserved and corrected

`development/` contains the initial build, tests and both development runs.
The first bimanual probe completed its initial motion but failed constructing
an invalid-joint test request with integer positions. The probe now explicitly
converts command values to floats; the second run and clean replay pass.

The initial host discovery failed importing ROS-dependent tests without rclpy,
and exposed the old verifier's assumption that only two packages may exist.
The suites now run in their required environments. Package verification accepts
the optional testbed, checks its installed assets, and still rejects missing
core or unexpected packages. Corrected development logs are retained too.

## Boundaries

GenericSystem supplies mock positions, without motor dynamics, contact, object
sensing or UR safety-state/driver integration. Bimanual success proves joint
protocol/feedback behavior only. There is no gripper interface or confirmed
physical grasp, release, tool calibration, measured reachability, full tending
cycle or hardware test. No production FSM, station validation flag, official
UR5 kinematics or archived evidence was changed.
