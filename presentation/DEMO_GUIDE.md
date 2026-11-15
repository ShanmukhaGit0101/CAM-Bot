# Presentation demonstration — one integrated cycle

**Main message:** “CAM-BOT demonstrates a carrier/local-arm coordination
architecture through a repeatable, instrumented ROS 2 visual workflow.”

## Reliable presentation path

Open `presentation/CAM-BOT.html` in a browser. It works offline, including images
and the recorded-trial replay. Use ←/→ or the buttons for slides, N for speaker
notes, and the replay controls on the demonstration slide. The replay shows
actual archived event timing/state transitions; it is **not live ROS or animated
3D reconstruction**. The recorded RViz screenshot is static and labelled.

`CAM-BOT.pptx` is the editable PowerPoint version, with speaker notes.
`CAM-BOT.pdf` is the static fallback. PowerPoint/PDF do not contain the interactive
replay: open the HTML file separately for that segment. Browser Print also
exports a static deck. Check projector resolution and font sizing before the talk.

For VS Code task buttons, container setup and live state logging, follow
[the execution guide](../docs/VSCODE.md). If your browser blocks local HTML,
`bash tools/workbench.sh presentation` serves it at `http://127.0.0.1:8765/CAM-BOT.html`.

## Optional live RViz demonstration

Use the existing prepared **ROS 2 Humble GUI environment with the patched RViz**
from `docs/CLOUD_HUMBLE.md`. Do not install packages, rebuild Docker or introduce
new CAD/controllers during the presentation. The current small-module CAD is
shown separately; the accepted live demo intentionally uses its original
four-joint placeholder.

Before the presentation, inside that prepared environment and this checkout:

```bash
source /opt/ros/humble/setup.bash
colcon build --base-paths src --symlink-install \
  --packages-select carrier_description carrier_control
source install/setup.bash
python3 tools/check_ay13_docs.py --installed
bash tools/present_demo.sh
```

In a second terminal **in the same environment and checkout**:

```bash
bash tools/present_demo.sh start
```

Both default to ROS domain 109. If occupied, select the same unused
`ROS_DOMAIN_ID` in both terminals. The wrapper refuses an occupied domain at
launch, enables coordination explicitly and writes to a fresh folder under
`~/cambot-presentations/`, preserving archived results. It calls the existing
visual launch and does not select a robot driver.

1. Before start, point out the UR5 carrier, flange, local arms and five stations.
2. Start once. Explain S1 raw → S2 staging → S3 machine → S4 output → S5 finished.
3. Point out global carrier movement and local visual manipulation. The decision
   uses a geometric workspace proxy, not a claim of collision-free planning.
4. At the end, show `FINISHED_AT_S5`, completion and the return to HOME.
5. Ctrl-C in the launch terminal. Retain the newly printed output directory.

Optional checks during rehearsal, while the launch is running:

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
export ROS_DOMAIN_ID=109 ROS_LOCALHOST_ONLY=1
ros2 topic info /joint_states --verbose
ros2 topic echo /cambot/workpiece_state
```

Expect one publisher, `machine_tending_coordinator`. Stop the echo with Ctrl-C.
After stopping the launch, `ros2 node list --no-daemon` should be empty in this
domain. Do not kill unrelated nodes. Rehearse one full cycle before the event;
no fresh GUI/runtime pass is claimed by the presentation packaging itself.

## If the live demonstration has trouble

Spend at most 30 seconds diagnosing display/launch trouble, then open the HTML
recorded replay and say: “This is the retained visual trial, replayed from our
logs.” Show its source/capture and results slide. Never describe the fallback as
live or substitute the older carrier-only video as a full tending run.

## Ten-minute running order

- 0:00–1:30: motivation and carrier/local-arm architecture.
- 1:30–3:00: workcell, workflow and coordination decisions.
- 3:00–4:30: one live cycle or recorded event replay.
- 4:30–6:00: five-trial results and measurement boundary.
- 6:00–8:00: kinematics, controller checks and mechanical concepts.
- 8:00–9:00: team workstreams and integration.
- 9:00–10:00: delivered scope, limitations and future extensions.

## Short answers for discussion

- **Is this a physical robot demonstration?** No; the main result is visual ROS
  simulation. Separate tests exercise mock-backed controllers.
- **Does 5/5 prove industrial reliability?** No; five trials in one fixed visual
  scenario demonstrate repeatability of that scenario.
- **Is it faster than a conventional setup?** We have not run a controlled
  comparative baseline, so no efficiency improvement is claimed.
- **Why are Tasks 7–15 unfinished?** Those are extensions toward controller-backed
  and physical operation, now outside the agreed final-project scope.
- **What is the achievement?** An integrated, reproducible coordination demo,
  transparent measurements, engineering studies and a traceable evidence record.
