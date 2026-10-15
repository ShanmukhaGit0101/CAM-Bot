# CAMBOT

**Carrier-assisted Adaptive Manipulation with Bimanual Operational Technology**

A carrier-assisted dual-arm manipulation framework for repetitive industrial
tasks such as CNC machine tending. A carrier arm handles **global positioning**;
a bimanual module mounted on it handles **local manipulation**.

![status](https://img.shields.io/badge/phase-4%20of%206-blue)
![ros](https://img.shields.io/badge/ROS%202-Humble-blue)
![license](https://img.shields.io/badge/license-Apache--2.0-green)

---

## The problem

A conventional industrial manipulator uses the same joints for both gross
transit between stations and fine work at each station. Every workpiece
exchange therefore costs a full-arm reposition. Across a shift this becomes
long cycle times, wasted energy, and a local workspace that is barely used.

## The approach

CAMBOT splits the two jobs across a hierarchy:

```text
                        CAMBOT
                           │
             ┌─────────────┴─────────────┐
             │                           │
    Global positioning           Local manipulation
             │                           │
      Carrier Arm (CA)           ┌───────┴───────┐
             │                   │               │
             │               Left arm        Right arm
             │                   │               │
             └──────────┬────────┴───────┬───────┘
                        │                │
              Hierarchical task & motion coordination
                        │
                 CNC machine tending
```

**Terminology used throughout this repository:**

| Term | Meaning |
|---|---|
| **CA** — Carrier Arm | The UR5 that positions the manipulation system |
| **CF** — Carrier Flange | The coupling between the UR5 wrist and the bimanual module |
| **BM** — Bimanual Module | The two-arm manipulation system mounted on the flange |

The detailed bimanual arm design is **deliberately deferred** until the carrier,
flange, workspace, and placement questions are settled. See
[`docs/DECISIONS.md`](docs/DECISIONS.md).

---

## Current status

**AY-01 through AY-12 have accepted visual ROS 2 Humble evidence; AY-13 is in
progress pending an independent quick-start repeat.** Five measured visual
cycles, raw observations, metrics and plots are in the
[experiment record](experiments/machine_tending/README.md). These results do not
prove controller or physical execution. The [status matrix](docs/STATUS.md)
defines every task's scope and evidence level; the [AY ledger](docs/ayush/ledger.json)
records each change, test and limitation.

---

## Repository layout

```text
CAM-Bot/
├── README.md                     ← you are here
├── LICENSE                       Apache-2.0
├── CONTRIBUTING.md               branch, commit, and review conventions
├── .gitignore
├── .gitattributes                Git LFS rules for CSV / video
│
├── src/                          ROS 2 packages built in this checkout
│   ├── carrier_description/      URDF, Xacro, meshes, launch, rviz
│   └── carrier_control/          trajectory nodes and cycle controllers
│
├── config/
│   └── waypoints.yaml            source mirror of installed carrier-control waypoints
│
├── docs/
│   ├── STATUS.md                 ← single source of truth for progress
│   ├── ROADMAP.md                the 6 phases, in detail
│   ├── ARCHITECTURE.md           kinematic chain, TF tree, interfaces
│   ├── DECISIONS.md              design decisions and their rationale
│   ├── TASK_ALLOCATION.md        who owns what
│   ├── progress/
│   │   ├── phase1-carrier-baseline.md
│   │   ├── phase2-mass-sensitivity.md
│   │   ├── phase3-carrier-flange.md
│   │   └── phase_4.md             archived narrative with provenance caveat
│   ├── ayush/                    AY evidence ledger and repeat guide
│   └── reference/
│       ├── TOPS_Team_2.pdf
│       └── task_split.pdf
│
├── experiments/
│   └── mass_sensitivity/
│       ├── README.md
│       ├── exp01-upper-arm-10pct/
│       ├── exp02-forearm-10pct/
│       └── exp03-shoulder-10pct/
│           ├── params/           YAML mass parameters
│           ├── urdf/             perturbed URDFs
│           ├── scripts/          extraction, analysis, plotting
│           ├── data/             raw /joint_states CSV  (Git LFS)
│           ├── plots/            generated figures
│           └── results/          numerical comparisons
│
└── media/                        screencasts  (Git LFS)
```

---

## Quick start

**Visual quick-start requirements:** Ubuntu 22.04 · ROS 2 Humble · colcon ·
rosdep · RViz · Universal Robots description package. See the
[clean-checkout guide](docs/ayush/README.md) for Distrobox, Wayland and LFS
details.

```bash
# Clone the current work branch (use main after merge)
git clone --branch feature/ay10-ay12-visual-experiments https://github.com/voidAyush-tsx/CAM-BOT.git
cd CAM-BOT
source /opt/ros/humble/setup.bash
rosdep install --from-paths src --ignore-src -r -y
colcon build --base-paths src --symlink-install --packages-select carrier_description carrier_control
export COLCON_TRACE=
set +u
source install/setup.bash
set -u
```

**Run the complete visual machine-tending sequence:**

```bash
ros2 launch carrier_description dual_arm_demo.launch.py auto_start:=false trial_count:=1
```

This entry point is fixed to **visual simulation**. It launches the robot
description, state publisher, coordinator, workpiece/task state, CSV logger, and
RViz, but no actuator, controller, or Gazebo physics. The displayed flow is:

```text
HOME → S1 pick → S2 stage → S3 load/dwell/re-grasp → S4 unload → S5 place → HOME
```

In another sourced terminal, start one trial with
`ros2 service call /machine_tending_coordinator/start std_srvs/srv/Trigger "{}"`.

The coordinator uses a one-shot, feedback-gated application FSM with explicit
`HOME → PICK_RAW → STAGE → LOAD_MACHINE → MACHINE_DWELL → UNLOAD_MACHINE →
PLACE_FINISHED → HOME` states. `dual_arm_cycle` remains a separate generic
viewer and is not launched alongside this FSM. See
[`docs/INTERFACES.md`](docs/INTERFACES.md) for start/reset/cancel services.

The separate `machine_tending_controller.launch.py` entry point requires an
absolute `controller_bringup_file` and a controller-validated `config_file`.
The supplied plan deliberately fails that gate (unvalidated S1–S4, missing S5).
It cannot yet launch an unattended controlled-carrier system. See
[`docs/VALIDATION.md`](docs/VALIDATION.md) and
[`docs/INTERFACES.md`](docs/INTERFACES.md).

The five visible stations and interaction targets are configured in the
installed [`machine_tending.json`](src/carrier_control/config/machine_tending.json).
Their positions, orientations and box sizes are **temporary visual-simulation
assumptions in metres/radians**, not measured cell geometry. Both launch modes
expand the existing workcell Xacro from this file; editing a station pose in
the config changes its TF frame and corresponding visual target together.

---

## Waypoints

Machine-shop stations are stored as **joint configurations**, not Cartesian
poses, in the installed [`carrier_control/config/waypoints.yaml`](src/carrier_control/config/waypoints.yaml).
The root [`config/waypoints.yaml`](config/waypoints.yaml) is kept as a byte-identical
source mirror for older documentation; the controller resolves the installed
package-share asset, not the current working directory.

| Station | Purpose |
|---|---|
| HOME | Standby configuration |
| P1–P4 | Machine stations 1–4 |

They were taught by positioning the UR5 with MoveIt's RViz interactive marker
and recording `/joint_states`. This replaced an earlier Cartesian-target
approach that produced planning failures — see
[`docs/progress/phase1-carrier-baseline.md`](docs/progress/phase1-carrier-baseline.md).

---

The current machine-tending coordinator includes a configurable, visual-only
geometric workspace proxy and TF-gated carrier/local decision policy. It is
not bimanual IK or verified grasp control; see
[`docs/INTERFACES.md`](docs/INTERFACES.md) and
[`docs/VALIDATION.md`](docs/VALIDATION.md) for limits and tests.

## Experiments

Machine-tending trials use a separate versioned CSV-summary/JSONL-event logger
with UUID trial IDs, Git/config provenance, monotonic durations, and durable
failure/interruption records. See
[`experiments/machine_tending/README.md`](experiments/machine_tending/README.md).
These records do not alter the archived mass-sensitivity datasets below.

Three 10% link-mass perturbations of the UR5, comparing recorded joint
trajectory statistics against a baseline run:

| ID | Link | Baseline | Perturbed |
|---|---|---|---|
| EXP01 | Upper arm | 8.3930 kg | 9.2323 kg |
| EXP02 | Forearm | 2.3300 kg | 2.5630 kg |
| EXP03 | Shoulder | 3.7000 kg | 4.0700 kg |

Results and their (important) limitations:
[`experiments/mass_sensitivity/README.md`](experiments/mass_sensitivity/README.md).

---

## Team

**CAMBOT — TOPS Programme 2026**

| Member | Workstream |
|---|---|
| Shannu | Manipulator kinematics & control |
| Tanmay | Mechanical & carrier design |
| Ayush | Software, simulation & digital systems |

See [`docs/TASK_ALLOCATION.md`](docs/TASK_ALLOCATION.md).

---

## License

Apache License 2.0 — see [`LICENSE`](LICENSE).
