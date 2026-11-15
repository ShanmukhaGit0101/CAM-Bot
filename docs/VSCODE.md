# Run CAM-BOT from VS Code

Use **File → Open Folder** on this repository, then **Terminal → Run Task**.
The `CAM-BOT:` tasks operate on the checkout you opened. Build uses only `src/`;
no archived source snapshot is compiled. These tasks are shortcuts to executable
scripts, so the same commands work in an ordinary Bash terminal.

The main demonstration remains the accepted coordinated **visual ROS simulation**.
It includes the UR5, mounted four-joint model, five stations, tending state machine,
coordination decisions, moving visual workpiece, structured logs and analysis.
The separate mock controllers and CAD studies can be shown as additional work;
they do not replace this working demonstration.

## 1. One-time setup on your CachyOS laptop

Keep VS Code on the host. ROS tasks execute in the prepared Humble Docker image
you already built for independent review. Python analysis and presentation tasks
run on the host. **No host ROS Jazzy installation is needed.** The old missing
`/opt/ros/jazzy/setup.bash` message comes from your shell startup file; remove that
obsolete source line, or guard it with `if [ -f ... ]; then source ...; fi`.

From the repository root in the VS Code terminal, prepare host dependencies:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r tools/workbench-requirements.txt
git lfs pull
bash tools/workbench.sh doctor
```

Select `.venv/bin/python` using **Python: Select Interpreter** for host editing.
The script automatically uses this venv for offline tasks, and system Python
inside Humble for ROS. The venv does not provide `rclpy` on CachyOS.

For your Wayland/XWayland session (`DISPLAY` previously `:1`), start one dedicated
container. This reuses `cambot-humble:ay13-reproducible`, containing the patched
RViz library. If the image is absent, follow [CLOUD_HUMBLE.md](CLOUD_HUMBLE.md)
with `docker buildx build --load`; build it **before** rehearsal. The headless
`controller-testbed` image alone cannot display RViz.

```bash
(
set -euo pipefail
repo_root="$(pwd -P)"
test -f "$repo_root/tools/workbench.sh"
docker image inspect cambot-humble:ay13-reproducible >/dev/null
test -n "${DISPLAY:-}"
test -d /tmp/.X11-unix
command -v xhost >/dev/null
# Narrow local-user access, matching the UID used inside the container.
xhost "+SI:localuser:$(id -un)"
docker run -d --pull=never --name cambot-vscode \
  --user "$(id -u):$(id -g)" \
  --mount "type=bind,src=$repo_root,dst=/workspace/CAM-BOT" \
  --mount type=bind,src=/tmp/.X11-unix,dst=/tmp/.X11-unix,readonly \
  -w /workspace/CAM-BOT \
  -e DISPLAY="$DISPLAY" -e HOME=/tmp/cambot-vscode-home \
  -e QT_QPA_PLATFORM=xcb -e QT_X11_NO_MITSHM=1 \
  -e LIBGL_ALWAYS_SOFTWARE=1 -e ROS_DOMAIN_ID=109 -e ROS_LOCALHOST_ONLY=1 \
  cambot-humble:ay13-reproducible \
  bash -c 'mkdir -p "$HOME"; exec sleep infinity'
)
```

This binds the **current checkout** and writes builds as your UID. Do not reuse a
container bound to an old clone. If `cambot-vscode` already exists, inspect it with
`docker inspect cambot-vscode`; start it with `docker start cambot-vscode` only if
its mount points to this checkout. To replace a stopped obsolete container,
explicitly remove that container (`docker rm cambot-vscode`) before the block.
Repository files are bind-mounted and are not removed by container removal.

For native Ubuntu/Humble, open the repository directly in VS Code after preparing
its dependencies using [the README](../README.md). Tasks automatically use native
Humble. An existing patched overlay at `/opt/cambot/rviz` is sourced when present.
To force a different prepared container, launch VS Code with
`CAMBOT_CONTAINER=your-container code .`; it must mount this checkout at
`/workspace/CAM-BOT`. Do not run simultaneous visual and legacy joint publishers.

The Launch task now enables the [clearer arm presentation view](ARM_PRESENTATION.md):
blue/orange arm links, joint housings, slimmer visual covers and opaque
station bodies. The wrapper also creates a fresh `plan.json` with the exchanged/mirrored arm
arrangement. The carrier uses shorter equivalent-angle turns; see the guide
for the difference between display styling and this new visual motion profile.

## 2. Rehearse the complete code demonstration

Run these tasks individually in this order. Long-running tasks get separate
terminals; they deliberately do not automatically start a cycle.

| VS Code task | What to see |
|---|---|
| 00 Check environment | Correct branch, checkout and running container |
| 01 Build visual demo | `carrier_description` and `carrier_control` build successfully |
| 02 Test core packages | Package tests and installed documentation checks; inspect any skips |
| 03 Launch RViz (wait for Start) | UR5, local arms and five stations; output directory printed |
| 04 Observe workflow | Live task/workpiece/coordination messages; three logs retained |
| 06 Inspect ROS graph | Exactly one `/joint_states` publisher: `machine_tending_coordinator` |
| 05 Start one cycle | S1 → S2 → S3 → S4 → S5, then HOME; final `FINISHED_AT_S5` |
| 07 Cancel cycle | Optional rehearsal of cancellation while active; use a fresh launch afterward |
| 08 Analyze new trial | Paste the **host** path to the new `trials.csv`; fresh plots/metrics |
| 12 Open presentation server | Open `http://127.0.0.1:8765/CAM-BOT.html` in your host browser |

Use **Ctrl-C in the Launch task's terminal** after completion to shut down ROS/RViz.
Use Ctrl-C separately in Observe. Do not merely close VS Code while nodes run.
The host task gives Docker a terminal when VS Code provides one, forwarding the
terminal interrupt to the foreground launch. To inspect after shutdown:

```bash
docker exec cambot-vscode /cambot_entrypoint.sh bash -c \
  'ROS_DOMAIN_ID=109 ROS_LOCALHOST_ONLY=1 ros2 node list --no-daemon'
```

Expect no nodes. The launch refuses an occupied domain; resolve your prior launch
before retrying. No task kills unrelated processes. To use another unused domain,
set `ROS_DOMAIN_ID` in the environment from which you start VS Code, identically
for all commands. Do not run multiple Start tasks at once.

New run and observer folders are under `.cambot-runs/` in this checkout, ignored
by Git. A container path `/workspace/CAM-BOT/.cambot-runs/run.ABC/trials.csv`
corresponds to `<your-checkout>/.cambot-runs/run.ABC/trials.csv` on the host.
Keep its sibling `trials.events.jsonl`. Copy useful rehearsal folders elsewhere
before cleaning your checkout. Neither analysis task overwrites archived results.
A new one-cycle run is not the archived five-trial qualification.

## Step through the code with F5

Select the host `.venv/bin/python` interpreter, open
`src/carrier_control/carrier_control/machine_tending_fsm.py`, and place a
breakpoint in `run()`. Choose **Run and Debug → CAM-BOT: debug offline FSM
(success + failure)**, then press F5. The existing offline trace drives a
successful workflow and an injected `S3_LOAD` failure with a synthetic adapter.
You can inspect the plan, current state and workpiece state and step through the
transition logic. This is source-level debugging, not ROS motion or a hardware run.
For integration behavior, use the live Launch/Observe tasks above.

## 3. Show the rest of the implemented work

| Contribution | Execute or inspect |
|---|---|
| Reproducible five-trial metrics and plots | Task 09; open the printed fresh `analysis/` directory |
| Kinematics, sampled workspace and five assumed placements | Task 10; generated `study/report.json`, `workspace.png`, coverage/point CSVs |
| Offline analysis, geometry and presentation tests | Task 11; no ROS required |
| Carrier and four-joint mock controller action protocols | Optional mock build/test, in the separate controller image below |
| Compact module design | [CAD README](../design/compact_module/README.md), `generated/preview.png`, STEP/URDF and mass/clearance reports; optional CAD dependencies are separate |
| Team workstreams and final results | [Contribution record](../presentation/CONTRIBUTIONS.md), presentation, report and speaker notes |

The workspace task reproduces the existing assumed kinematic model; it is not a
whole-cell collision or physical placement validation. CAD is a separate prototype
and is not silently swapped into the accepted live demo. PNG bytes may vary with
Matplotlib; compare numerical results and provenance.

Optional mock controller tasks require the **controller-testbed** image from
[TASK7_CONTROLLER.md](TASK7_CONTROLLER.md), not the visual-only image. Stop the
visual launch first. Start another container bound to the same checkout using
that image (no GUI needed), then run the terminal commands with its name:

```bash
docker run -d --pull=never --name cambot-controller \
  --user "$(id -u):$(id -g)" \
  --mount "type=bind,src=$(pwd -P),dst=/workspace/CAM-BOT" \
  -w /workspace/CAM-BOT -e HOME=/tmp/cambot-controller-home \
  cambot-humble:controller-testbed \
  bash -c 'mkdir -p "$HOME"; exec sleep infinity'
CAMBOT_CONTAINER=cambot-controller bash tools/workbench.sh mock-build
CAMBOT_CONTAINER=cambot-controller bash tools/workbench.sh mock-test
```

The mock-test command runs eight carrier and seven bimanual protocol cases, checking
one broadcaster and clean shutdown. No physical driver or full tending controller
cycle is invoked. Stop this optional container afterward with
`docker stop cambot-controller`. Rebuild older controller images without Git LFS
using the current Dockerfile before testing. Use separate checkouts for different images when their Colcon
build environments differ; rebuilding is required in the chosen environment.

## 4. Finish your session

After interrupting the Launch and Observe tasks and checking the empty graph:

```bash
docker stop cambot-vscode
xhost "-SI:localuser:$(id -un)"
```

Reapply the narrow X access command before starting this container on a later
session. If your desktop's `DISPLAY` changes, recreate the stopped container with
the new value. The HTML/PDF fallback always remains available without ROS.

The scripts and code-level checks are verified as recorded in
[execution verification](../presentation/execution-verification.md).
A fresh GUI rehearsal on your laptop is still necessary before the presentation;
the new VS Code tasks do not themselves constitute a new human RViz acceptance.
