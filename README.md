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

**Phase 4 of 6 — Carrier Flange & Bimanual Placeholder.**

| Phase | Scope | Status |
|---|---|---|
| 1 | UR5 carrier baseline (Gazebo, MoveIt 2, ros2_control, machine-shop cycle) | ✅ Complete |
| 2 | Mass sensitivity study (EXP01–03) | ✅ Complete |
| 3 | Carrier workspace characterization | ⏸ Planned |
| 4 | Carrier flange + dual-arm placeholder | 🔧 In progress |
| 5 | Quantitative baseline logging & metrics | ⏸ Planned |
| 6 | Carrier placement analysis | ⏸ Planned |

Full breakdown: [`docs/STATUS.md`](docs/STATUS.md) — the single source of truth.
Do not duplicate status tables into other documents.

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
├── src/                          ROS 2 packages (copy into your ws src/)
│   ├── carrier_description/      URDF, Xacro, meshes, launch, rviz
│   └── carrier_control/          trajectory nodes and cycle controllers
│
├── config/
│   └── waypoints.yaml            authoritative machine-shop waypoints
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
│   │   └── phase4-carrier-flange.md
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

**Requirements:** Ubuntu 22.04 · ROS 2 Humble · Gazebo · MoveIt 2 ·
`ros2_control` · Universal Robots ROS 2 packages.

```bash
# 1. Create a workspace and clone
mkdir -p ~/tops_ws/src && cd ~/tops_ws/src
git clone https://github.com/ShanmukhaGit0101/CAM-Bot.git
ln -s CAM-Bot/src/carrier_description .
ln -s CAM-Bot/src/carrier_control .

# 2. Dependencies
cd ~/tops_ws
rosdep install --from-paths src --ignore-src -r -y

# 3. Build
colcon build --symlink-install
source install/setup.bash
```

**Run the machine-shop cycle:**

```bash
# terminal 1 — simulation + MoveIt
ros2 launch carrier_description ur5_machine_shop.launch.py

# terminal 2 — automated cycle
ros2 run carrier_control machine_shop_joint_cycle
```

The carrier executes:

```text
HOME → P1 → HOME → P2 → HOME → P3 → HOME → P4 → HOME
```

holding ~3 s at each station.

> **Note:** `ur5_machine_shop.launch.py` and the Phase 4 dual-arm files are
> described in `docs/progress/phase4-carrier-flange.md` but are **not yet
> committed**. See [`AUDIT.md`](AUDIT.md) §2.1. Until they land, the simulation
> must be started from the stock `ur_simulation_gazebo` and `ur_moveit_config`
> launch files.

---

## Waypoints

Machine-shop stations are stored as **joint configurations**, not Cartesian
poses, in [`config/waypoints.yaml`](config/waypoints.yaml):

| Station | Purpose |
|---|---|
| HOME | Standby configuration |
| P1–P4 | Machine stations 1–4 |

They were taught by positioning the UR5 with MoveIt's RViz interactive marker
and recording `/joint_states`. This replaced an earlier Cartesian-target
approach that produced planning failures — see
[`docs/progress/phase1-carrier-baseline.md`](docs/progress/phase1-carrier-baseline.md).

---

## Experiments

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
