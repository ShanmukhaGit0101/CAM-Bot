# CAMBOT — Carrier Arm (CA) Work Plan

## Terminology

- **CA — Carrier Arm:** The UR5 used to position the manipulation system.
- **CF — Carrier Flange:** The coupling/interface between the UR5 wrist and the future bimanual module.
- **BM — Bimanual Module:** The future two-arm manipulation system mounted on the carrier flange.

Current scope ends at the **CA → CF → BM placeholder** stage. The actual bimanual arm design will be done later.

---

# Phase 1 — UR5 Carrier Baseline ✅ DONE

## 1. UR5 Simulation
- ROS 2 Humble
- Gazebo
- UR5 model
- RViz
- MoveIt 2
- ros2_control

**Output:** Functional simulated Carrier Arm (CA).

## 2. Motion Planning
- MoveIt planning to target configurations
- Joint trajectory execution
- RViz interactive teaching

**Output:** CA can move to commanded configurations.

## 3. Machine-Shop Waypoints
- HOME
- P1
- P2
- P3
- P4
- `waypoints.yaml`

**Output:** Defined machine-shop task locations.

## 4. Automated Carrier Cycle

```text
HOME → P1 → HOME → P2 → HOME → P3 → HOME → P4 → HOME
```

**Output:** First functional machine-shop carrier baseline.

---

# Phase 2 — Make the Baseline Measurable 🔵 NEXT

## 5. Automated Logging

Modify the cycle execution to record:

- Trial
- From
- To
- Planning time
- Execution time
- Success/failure

Example:

```text
1, HOME, P1, 0.82, 3.41, SUCCESS
1, P1, HOME, 0.74, 3.25, SUCCESS
```

**Output:**

```text
results/
└── baseline_trials.csv
```

## 6. Repeated Baseline Trials

Run **10–20 complete machine-shop cycles**.

Record:

- Successful/failed cycles
- Total cycle time
- Station-wise motion time
- Planning failures
- Execution failures

**Output:** Actual baseline dataset.

## 7. Baseline Metrics

Calculate:

- Mean cycle time
- Standard deviation
- Minimum/maximum cycle time
- Success rate
- Station-wise motion time
- Optional joint-motion metric

Useful equations:

\[
Success\ Rate =
\frac{N_{successful}}{N_{trials}} \times 100
\]

\[
T_{cycle} = T_{motion} + T_{dwell}
\]

Optional:

\[
Joint\ Motion = \sum_i |q_{i,f}-q_{i,0}|
\]

**Output:** Quantitative performance description of the current CA baseline.

---

# Phase 3 — Carrier Workspace Characterization 🟡

## 8. UR5 Workspace Mapping

Sample valid joint configurations:

```text
q1, q2, q3, q4, q5, q6
        ↓
Forward Kinematics
        ↓
(x, y, z)
```

Collect reachable end-effector positions and visualize them in 3D.

Important considerations:

- Respect joint limits
- Reject invalid/self-collision configurations where practical
- Generate a 3D reachable workspace
- Mark P1–P4 locations

**Output:** UR5 reachable workspace map.

## 9. Workspace vs Machine Stations

Overlay the machine-shop stations on the workspace.

Example:

| Station | Reachable? | Notes |
|---|---|---|
| P1 | ✓/✗ | |
| P2 | ✓/✗ | |
| P3 | ✓/✗ | |
| P4 | ✓/✗ | |

Where useful, estimate distance/margin between stations and the workspace boundary.

**Output:** Quantitative station-coverage analysis.

---

# Phase 4 — Carrier Flange / Interface 🟠

## 10. Parameterized Carrier Flange

Create a simple parameterized flange attached to the UR5 wrist.

Possible parameters:

```text
flange_length
flange_width
flange_thickness
mount_spacing
mount_height
tilt_angle
```

Concept:

```text
               BM placeholder
             │               │
             │               │
             ○               ○
             │               │
        ┌────────────────────────┐
        │    Carrier Flange      │
        └───────────┬────────────┘
                    │
                   UR5
```

The goal is parameterization and a clean interface, not final mechanical complexity.

**Output:** `carrier_flange.xacro` (or equivalent URDF/Xacro component).

## 11. Carrier Flange Coordinate Frame

Create a dedicated:

```text
carrier_flange
```

TF frame.

Target architecture:

```text
world
  │
  ▼
Carrier Arm (CA)
  │
  ▼
carrier_flange (CF)
  │
  ▼
Bimanual Module (BM)
```

**Output:** Correct carrier-to-flange transform and documented TF architecture.

---

# Phase 5 — Bimanual Placeholder 🟣

## 12. Bimanual Module Placeholder

Do **not** design the actual two arms yet.

Represent the future arms using two simple cylinders:

```text
           Cylinder 1
               │
               │
        ┌──────┴──────┐
        │   Flange    │
        └──────┬──────┘
               │
               │
           Cylinder 2
```

The cylinders represent:

- Future Arm 1
- Future Arm 2
- Approximate mounting locations
- Approximate orientations

Use the placeholder only to validate:

- Mounting geometry
- Spatial arrangement
- Carrier reach
- Workspace interaction
- Collision envelope
- Visualization

**Output:** BM placeholder attached to the CF without committing to final arm design.

---

# Phase 6 — Carrier Placement Analysis 🔥

## 13. Carrier Placement Analysis

Main question:

> Where should the Carrier Arm position itself so that the future Bimanual Module can service the machine-shop stations effectively?

Evaluate candidate carrier positions using:

- Station reachability
- Distance to stations
- Orientation feasibility
- Workspace overlap
- Carrier travel distance

Concept:

```text
              P1

       P2              P3


              P4

               │
               │
              CA
```

**Output:** Candidate carrier positions and their performance.

## 14. Carrier-Position Comparison

Compare several possible carrier locations:

```text
Position A
Position B
Position C
Position D
```

Example:

| Carrier Position | P1 | P2 | P3 | P4 | Total Movement |
|---|---|---|---|---|---|
| A | ✓ | ✓ | ✓ | ✓ | ... |
| B | ✓ | ✓ | ✓ | ✓ | ... |
| C | ✓ | ✓ | ✓ | ✓ | ... |

Identify the placement that provides the best overall coverage/travel trade-off.

**Output:** Preliminary carrier-placement recommendation.

---

# Overall Progression

```text
CURRENT
   │
   ▼
┌──────────────────────┐
│  UR5 Carrier Arm     │
│  Gazebo + MoveIt     │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Validated Baseline   │
│ 10–20 Trials         │
│ Logging + Metrics    │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Workspace Mapping    │
│ Reachability         │
│ Station Overlay      │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Carrier Flange       │
│ Parameterized Xacro  │
│ + TF                 │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Bimanual Placeholder │
│  ○             ○     │
│      Flange          │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Carrier Placement    │
│ Analysis             │
└──────────┬───────────┘
           │
           ▼
          STOP
Mechanical/System Design
comes next
```

---

# Suggested Evidence for Progress Reporting

Keep evidence for each phase:

```text
docs/
├── decisions.md
├── interfaces.md
├── progress.md
└── architecture.md

results/
├── baseline_trials.csv
├── cycle_time.csv
└── plots/

screenshots/
├── ur5_gazebo.png
├── moveit_rviz.png
├── waypoint_p1.png
├── machine_cycle.png
├── workspace_map.png
└── carrier_flange.png
```

## Core Progress Story

> I first established the Carrier Arm simulation and validated its machine-shop operation. I then moved toward quantitative baseline evaluation through repeated trials and logging, followed by workspace characterization. The next stage extends the carrier model with a parameterized Carrier Flange and a simple Bimanual Module placeholder. Finally, carrier-placement analysis will investigate how carrier positioning affects the future manipulation workspace. The detailed bimanual arm design is intentionally deferred until the carrier/interface analysis is complete.
