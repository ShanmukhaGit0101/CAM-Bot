# Task 7: UR5 controller integration

The optional `carrier_controller_testbed` package runs the real Humble
`controller_manager`, `JointTrajectoryController` and `JointStateBroadcaster`
against `mock_components/GenericSystem`. It is a controller protocol testbed,
not Gazebo dynamics, a UR robot driver, physical actuation or a complete tending
cycle. Current dispositions live in [STATUS.md](STATUS.md).

## Scope and architecture

The launch expands the existing official UR5 plus CAM-BOT description. A
mock-only helper replaces the emitted physical-driver `ros2_control` block
with GenericSystem, removing network parameters, GPIO and physical interfaces.
All kinematic joints/origins remain unchanged. Six UR5 joints expose position
commands and position/velocity state interfaces; all start at synthetic zero.
No station target or validation flag changes. The placeholder's extra joints
have no simulated actuator and are outside this controller test.

The controller manager, RSP and controller topics use `/cambot_testbed`.
Only the joint-state broadcaster publishes `/cambot_testbed/joint_states`;
no visual coordinator or legacy publisher is started. The action is
`/cambot_testbed/ur5_trajectory_controller/follow_joint_trajectory`.
Spawner services establish readiness; broadcaster activation precedes trajectory
activation, and either spawner failure shuts the launch down.

The probe binds the production coordinator's `_move_carrier`, wait, feedback
and cancellation methods to an isolated test node with synthetic targets. It
uses the real action server and controller feedback. It does not instantiate
the tending coordinator with an invalid station plan or bypass its launch gate.
The original station configuration remains unvalidated and the full tending
controller launch still rejects it. Controller feedback here is mock state,
not encoder measurements or proof of grasp.

## Reproduce

Use a clean checkout of the review branch (or merged main), Docker with
BuildKit/Buildx, and a fresh output directory. From the repository root:

```bash
(
set -euo pipefail
[[ -z "$(git status --porcelain)" ]]
output="$(mktemp -d "$HOME/cambot-task7.XXXXXX")"
container="cambot-task7-$(basename "$output")"
ca_bundle=/etc/ssl/certs/ca-certificates.crt
[[ -r "$ca_bundle" ]] || ca_bundle=/etc/ssl/cert.pem

docker buildx build --load --progress=plain \
  -f tools/cloud/Dockerfile.controller_humble \
  --secret "id=ca,src=$ca_bundle" -t cambot-humble:controller-testbed . \
  2>&1 | tee "$output/image-build.log"
docker image inspect cambot-humble:controller-testbed --format '{{.Id}}' \
  > "$output/image-id.txt"
git rev-parse HEAD > "$output/source-commit.txt"
docker run -d --pull=never --name "$container" \
  --mount "type=bind,src=$PWD,dst=/workspace/CAM-BOT" \
  --mount "type=bind,src=$output,dst=/evidence" \
  -e ROS_DOMAIN_ID=117 -e ROS_LOCALHOST_ONLY=1 \
  cambot-humble:controller-testbed sleep infinity
trap 'docker stop "$container" >/dev/null 2>&1 || true' EXIT

docker exec "$container" /ros_entrypoint.sh bash -ec '
  git config --global --add safe.directory /workspace/CAM-BOT
  colcon build --base-paths src --symlink-install --executor sequential \
    --packages-select carrier_control carrier_description carrier_controller_testbed
  source install/setup.bash
  colcon test --base-paths src --executor sequential --return-code-on-test-failure \
    --packages-select carrier_control carrier_description carrier_controller_testbed
  colcon test-result --verbose
  python3 tools/check_ay13_docs.py --installed
  bash tools/run_ur5_mock_controller.sh /evidence/replay
' 2>&1 | tee "$output/runner.log"
printf 'Retained evidence: %s\n' "$output"
)
```

Select an unused ROS domain if 117 is occupied. The runner refuses preexisting
nodes and an existing replay output. Use `/ros_entrypoint.sh` for `docker exec`:
Docker does not invoke the image entrypoint for exec. The headless image pins
the ROS base digest and records apt controller versions; apt packages may
advance, so future images need their own validation. It has no RViz overlay or
hardware driver. Use the existing [Humble image](CLOUD_HUMBLE.md) for AY-13's
visual/RViz replay. That validator now scopes rosdep to its two core packages,
matching its build selection, so the optional third package does not silently
add controller dependencies to the visual replay.

To inspect the controller interactively after building/sourcing this image:

```bash
ros2 launch carrier_controller_testbed ur5_mock_controller.launch.py
```

Do not start this concurrently with the automated runner in the same domain.
The standalone probe is for this isolated mock launch only.

## Checks and interpretation

The automated probe verifies active controllers and one publisher, then tests:

- Production motion success, successful action status, actual-position feedback,
  nonzero feedback motion and final joint-state agreement within 0.002 rad.
- Invalid joint-name rejection, directly and through the production method.
- A real path-tolerance abort (`-4`), directly and through the production method.
  A test-only tolerance of `1e-12` rad deliberately rejects tracking during motion.
- Production cancellation: accepted cancellation, terminal CANCELED status,
  stable subsequent joint states and no increment of the success counter.
- Production result timeout followed by terminal cancellation. The fixture
  shortens the wait to 0.2 seconds using a test-only negative margin; no production
  configuration or timeout defaults are changed.
- Bounded absence of an action server on a deliberately nonexistent endpoint.
- Clean manager/RSP shutdown and an empty residual ROS graph.

The mock copies commands into state; it is not a tracking-performance benchmark.
It supplies no collision/IK, calibrated target, dynamics, speed-scaling, UR
safety-state, payload or physical communication evidence. Only the existing
carrier action methods are exercised, not a complete coordinator/BM cycle.
Task 7's mock integration can be verified while Task 6 remains pending; robot-
specific driver selection and hardware acceptance require the actual robot,
calibration, mounted geometry, validated targets and supervised operation.
