# Three additional CAM-BOT visual scenarios

The original five-block demonstration remains available. Three new assumed
layouts add local pose changes, carrier-position reuse, unequal station heights
and narrower proxy tolerances. All station blocks remain fully opaque. These
are visual ROS examples rather than controller, grasp or collision validation.

| Selectable scenario | Level | Added challenge | Carrier repositions expected |
|---|---|---|---|
| `original` | Reference | Existing demonstration and exchanged arms | 5 |
| `compact` | 1 | Two nearby station pairs share carrier poses; local arms extend/fold between them | 3 |
| `tiered` | 2 | Five separate poses, unequal heights, rotated staging/output blocks | 5 |
| `precision` | 3 | Different alternating placements, rotated/off-centre station targets and tighter both-arm geometric-proxy bounds | 5 |

The levels describe coordination/layout complexity, not a claim that increasing
level always increases joint travel or cycle duration. There is no obstacle
avoidance or collision-planning claim. The offline station-footprint check only
establishes that the five station rectangles do not overlap each other.

## Run from VS Code

Stay on `fix/arm-presentation` (or its merged main). Pull the update and build
using **CAM-BOT: 01 Build visual demo**, then run **02 Test core packages**.
Stop any previous Launch and Observe tasks first. Use one of these launch tasks:

- **CAM-BOT: 13 Scenario 1: compact shared workspace**.
- **CAM-BOT: 14 Scenario 2: stepped-height cell**.
- **CAM-BOT: 15 Scenario 3: precision transfer cell**.

Wait for RViz, run **04 Observe workflow**, optionally **06 Inspect ROS graph**,
then **05 Start one cycle**. Start/Observe work with whichever scene is active;
do not run two scenes in the same domain. At completion, expect `FINISHED_AT_S5`
and HOME. Run **08 Analyze new trial** with the fresh run's `trials.csv` path.
Ctrl-C in Observe and Launch before choosing the next scene.

Equivalent terminal command (the same prepared Humble GUI container is used):

```bash
bash tools/workbench.sh launch compact
```

Replace `compact` with `tiered`, `precision` or `original`. Each launch retains a
fresh `plan.json`, source SHA, ROS logs, trial CSV and event log. No Docker image
rebuild is required in the previously prepared GUI environment. Outputs and
analyses belong to separate scenarios; do not pool them as repeated trials of
one layout or mix them with the archived five-cycle qualification.

## If a scenario configuration is missing

A `FileNotFoundError` for `install/carrier_control/.../scenario_compact.json`
means the installed workspace needs rebuilding after the update. Python source
can be visible through symlink-install while newly added configuration assets
have not yet been installed. The launch wrapper now reports this directly and
refuses to create an incomplete run folder.

Run **01 Build visual demo** (or `bash tools/workbench.sh build`) in the current
checkout through the workbench's Humble container, then retry **13 → 04 → 05**.
The rebuild installs all three new scenario files, so repeat it once rather than
once per scenario. No Docker image rebuild or manual copying into `install/`
is needed.

## What moves efficiently in these examples

The carrier keeps the shortest-equivalent-angle policy. The compact example
uses three positions for five stations: two transitions stay inside the current
both-arm proxy and therefore avoid another carrier reposition request.

For the three new scenes, each station has paired HOLD and OPEN poses rather
than one fixed HOLD pose everywhere. Symmetric wrist anchors are synthesized
0.14 m apart using the actual mirrored two-link geometry. Their midpoint defines
the assumed interaction point before the carrier FK transforms it into world.
The arms move directly between required poses and remain in HOLD while carrying;
they do not open and return HOME at every intermediate station.

These wrist-anchor checks do not validate tool orientation, physical contact,
force closure or collision clearance. The workpiece still follows the visual
state interpolation; it is not attached through simulated grasp physics.

## Read the additional motion report

Task 08 still writes the existing result plots in `analysis/`. It now also writes
`motion/motion_summary.json` and `motion/motion_travel.png` in the printed fresh
analysis output directory. The report keeps each trial separate and states:

- Carrier joint excursion: sum of absolute effective start→final joint changes
  from completed visual carrier segments, including HOME return.
- Local-arm joint excursion: equivalent sum from new `BIMANUAL_MOTION` telemetry.
  Cubic interpolation is monotonic per joint, so endpoint excursion equals the
  visual segment's total per-joint command excursion.
- Calculated carrier reference: interpolate the stored raw joint numbers along
  the same visited station sequence, without equivalent-angle selection.
- Calculated local reference: return HOME before every next local segment,
  with the same initial and final targets.

The two references are calculations, **not separately executed baselines**.
These metrics are radians summed over joints, not Cartesian distance, energy,
actuator performance or proven throughput improvement. Older captures without
local telemetry show it as unavailable rather than zero. Partial failed motion
is not reported as a completed segment. The existing standard analysis still
reports those failed/censored trials separately.

## Configuration generation and verification

The three installed `scenario_*.json` files are derived from the original plan
and retained carrier URDF. The original installed plan is unchanged. Exact source
hashes and assumptions are included in each scenario. Controller targets/flags
remain unvalidated; these files must not be treated as hardware programs.

Regenerate into a new directory on the host with workbench Python dependencies:

```bash
.venv/bin/python tools/generate_demo_scenarios.py --output /tmp/cambot-scenes-NEW
```

In a prepared Humble GUI environment, the repeatable runtime checker uses the
same launch wrapper, existing ROS observers and strict shutdown checks:

```bash
python3 tools/verify_demo_scenarios.py /tmp/cambot-scenes-replay-NEW
```

It needs an unused nonzero ROS domain, DISPLAY, patched RViz and installed core
packages. Optional `--screenshots` requires PyQt5. Every attempt uses new paths;
failed launches/probes are retained. The [scenario verification record](evidence/DELIVERY/scenarios_20261116/README.md)
records the actual outcomes and environment, including the initial unpatched
RViz shutdown failure rather than presenting it as a successful replay.
