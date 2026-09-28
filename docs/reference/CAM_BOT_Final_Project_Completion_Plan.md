# CAM-BOT — Final Project Completion & Execution Plan

> **Project:** Carrier-assisted Adaptive Manipulation with Bimanual Operational Technology (CAM-BOT)  
> **Current phase:** UR5 carrier + custom flange + dual-arm integration  
> **Primary objective:** Conclude the project at a strong, demonstrable prototype/research stage with minimal unnecessary scope expansion.

---

# 1. Current Project Status

The following work is already completed and should be treated as the **baseline** rather than rebuilt.

## 1.1 Completed technical work

- UR5 carrier model integrated.
- Official UR5 `flange` and `tool0` chain verified.
- Custom `carrier_flange` attached after `tool0`.
- `carrier_flange_interface` and `dual_arm_base_link` integrated.
- Custom left and right arm structures integrated.
- Four additional joints are available:
  - `left_shoulder_joint`
  - `left_elbow_joint`
  - `right_shoulder_joint`
  - `right_elbow_joint`
- Xacro generation is working.
- `check_urdf` passes.
- RViz visualization works.
- `joint_state_publisher_gui` works.
- A ROS 2 dual-arm cycle controller exists.
- Smooth cubic joint interpolation is implemented.
- Existing sequence:
  - HOME
  - APPROACH
  - GRASP
  - HOLD
  - TRANSPORT
  - PLACE
  - RELEASE
  - HOME
- `dual_arm_cycle` is registered as a ROS executable.
- The dual-arm motion cycle itself works.

## 1.2 Current known issue

The remaining baseline integration problem is the **single launch command**.

The target is one command that starts:

```text
Robot description
      ↓
robot_state_publisher
      ↓
joint states / controller
      ↓
dual-arm motion cycle
      ↓
RViz
```

This should be fixed before adding major new functionality.

---

# 2. Final Project Goal

## 2.1 Final technical scope

The project should conclude as:

> **A ROS 2 simulation of a carrier-assisted bimanual manipulation system in a machine-tending environment, where a UR5 carrier positions a custom dual-arm manipulator and the dual-arm system performs a sequential workpiece-handling workflow across a five-station workspace.**

The final demonstration should communicate three ideas clearly:

1. **Carrier-assisted manipulation**
   - The UR5 acts as the global positioning/carrier mechanism.

2. **Local bimanual manipulation**
   - The custom dual-arm mechanism performs manipulation around the task area.

3. **Machine-tending workflow**
   - The system is demonstrated in a structured industrial-style workspace rather than as an isolated pick-and-place animation.

---

# 3. Scope Freeze

## 3.1 MUST COMPLETE

These are the highest-priority deliverables.

- [ ] Reliable single-command launch.
- [ ] Clean final RViz/simulation setup.
- [ ] Five-station machine-tending environment.
- [ ] Sequential workpiece workflow through the stations.
- [ ] At least one complete end-to-end demonstration.
- [ ] Basic quantitative metrics.
- [ ] Screenshots/video of the final system.
- [ ] Technical documentation.

## 3.2 SHOULD ATTEMPT

Only after the MUST items are stable.

- [ ] Check existing UR5 MoveIt 2 configuration.
- [ ] Determine whether the custom flange can be incorporated easily.
- [ ] Determine whether the custom dual-arm joints can be added as a planning group without major restructuring.
- [ ] Demonstrate one simple MoveIt-generated motion if integration is straightforward.

## 3.3 OPTIONAL

Only if significant time remains.

- [ ] More sophisticated collision checking.
- [ ] Improved object grasp visualization.
- [ ] Better trajectory optimization.
- [ ] Additional machine-tending motions.
- [ ] More detailed machine geometry.
- [ ] Additional performance experiments.

## 3.4 EXPLICITLY DEFER

Do NOT make these requirements for project completion.

- Full bimanual inverse kinematics.
- Advanced closed-loop grasp control.
- Force/torque sensing.
- Real hardware implementation.
- Dynamic object physics.
- Full CNC machine physics.
- Advanced collision-aware bimanual planning.
- Complex grasp planning.
- Large-scale optimization.
- Full industrial controller integration.

These can be listed as **future work**.

---

# 4. Priority Order

The project should be executed in this exact priority order.

```text
P0  →  Stabilize launch
       ↓
P1  →  Build 5-station environment
       ↓
P2  →  Create sequential machine-tending workflow
       ↓
P3  →  Validate complete demonstration
       ↓
P4  →  Add basic metrics
       ↓
P5  →  Investigate MoveIt 2
       ↓
P6  →  Documentation + presentation + video
```

## Important rule

> **Do not start P5 MoveIt 2 until P0–P4 are working.**

The existing trajectory controller already provides a working fallback. MoveIt must therefore be treated as an enhancement rather than a dependency.

---

# 5. P0 — Reliable Single Launch Command

## Objective

Create one command that reliably starts the complete demonstration environment.

Target:

```bash
ros2 launch carrier_description dual_arm_demo.launch.py
```

## Required components

The launch should start:

```text
1. robot_state_publisher
2. robot description generated from Xacro
3. dual_arm_cycle
4. RViz
```

If required by the final setup:

```text
5. joint_state_publisher / joint_state_publisher_gui
```

## Acceptance criteria

The task is complete only when:

- [ ] One command starts the complete environment.
- [ ] No manual second terminal is required for the basic demonstration.
- [ ] UR5 appears correctly.
- [ ] Carrier flange appears correctly.
- [ ] Both arms appear correctly.
- [ ] Four custom joints are available.
- [ ] Dual-arm cycle starts correctly.
- [ ] RViz loads the intended configuration.
- [ ] No robot-description error appears.
- [ ] The complete cycle can run from a clean terminal.

## Decision

### If launch works

Proceed immediately to P1.

### If launch remains problematic after reasonable debugging

Create a **known-good fallback launch** using the simplest working architecture.

Do not spend excessive time redesigning the ROS launch system.

---

# 6. P1 — Five-Station Machine-Tending Environment

## Objective

Create a simple industrial-style environment that gives the robot a clear application context.

The environment does NOT need detailed CAD or realistic machine physics.

## Recommended stations

```text
Station 1
RAW MATERIAL / INPUT
        ↓
Station 2
STAGING / INSPECTION
        ↓
Station 3
CNC / MACHINE
        ↓
Station 4
OUTPUT / UNLOADING
        ↓
Station 5
FINISHED PART
```

A compact alternative is:

```text
[S1 INPUT]
    ↓
[S2 STAGING]
    ↓
[S3 CNC]
    ↓
[S4 OUTPUT]
    ↓
[S5 FINISHED]
```

## Environment components

Minimum geometry:

- [ ] Floor / workspace.
- [ ] CNC or machine enclosure.
- [ ] Input table.
- [ ] Staging area.
- [ ] Output table.
- [ ] Finished-part area.
- [ ] One simple workpiece.

## Important design decision

### Use simple geometry.

The machine is primarily a **visual and task-context element**.

Do NOT spend time implementing:

- CNC internals.
- Spindle dynamics.
- Cutting physics.
- Manufacturing simulation.
- Complex machine doors.
- Detailed collision meshes.

The project is about **carrier-assisted manipulation**, not CNC simulation.

---

# 7. P2 — Sequential Machine-Tending Workflow

## Objective

Transform the current generic dual-arm motion sequence into an application-specific machine-tending sequence.

## Proposed workflow

```text
HOME
  ↓
S1 — Approach raw workpiece
  ↓
S1 — Grasp workpiece
  ↓
S2 — Move to staging / inspection
  ↓
S3 — Load machine
  ↓
S3 — Release workpiece
  ↓
Machine processing / dwell
  ↓
S3 — Re-grasp processed workpiece
  ↓
S4 — Unload machine
  ↓
S5 — Place finished workpiece
  ↓
Release
  ↓
HOME
```

## Important implementation strategy

Do NOT rewrite the controller from scratch.

Reuse the existing motion architecture:

```text
HOME
APPROACH
GRASP
HOLD
TRANSPORT
PLACE
RELEASE
HOME
```

Replace the abstract locations with named task locations.

For example:

```python
HOME
RAW_PICK
STAGING
MACHINE_LOAD
MACHINE_RELEASE
MACHINE_REGRASP
OUTPUT
FINISHED_PLACE
HOME
```

## Decision

The exact trajectory values should be chosen from the actual RViz/world geometry.

Do NOT assume that the previous joint angles are physically correct for the new station positions.

---

# 8. Coordinated Bimanual Behaviour

## Minimum acceptable behaviour

The two arms should visually appear to cooperate on the workpiece.

A simple implementation is sufficient:

```text
Left arm  → approach left side
Right arm → approach right side
        ↓
Both elbows close
        ↓
WORKPIECE HELD
        ↓
Both arms transport
        ↓
Both elbows open
        ↓
WORKPIECE RELEASED
```

## Important distinction

The project does NOT need to claim advanced force-controlled bimanual grasping.

The final documentation should describe this as:

> **Predefined coordinated bimanual motion for simulated workpiece handling.**

Avoid claiming:

- force closure,
- autonomous grasp planning,
- dynamic force control,
- closed-loop object stabilization,

unless those are actually implemented and validated.

---

# 9. P3 — Final Demonstration

## Objective

Produce one clean, repeatable demonstration.

## Demonstration sequence

```text
              CAM-BOT CELL

       ┌─────────────────────┐
       │      S1 INPUT       │
       └──────────┬──────────┘
                  ↓
       ┌─────────────────────┐
       │    S2 STAGING       │
       └──────────┬──────────┘
                  ↓
       ┌─────────────────────┐
       │    S3 CNC MACHINE   │
       └──────────┬──────────┘
                  ↓
       ┌─────────────────────┐
       │    S4 OUTPUT        │
       └──────────┬──────────┘
                  ↓
       ┌─────────────────────┐
       │   S5 FINISHED PART  │
       └─────────────────────┘
```

## Demonstration requirements

- [ ] Robot starts from HOME.
- [ ] Raw workpiece is identified by location.
- [ ] Arms approach workpiece.
- [ ] Workpiece is grasped.
- [ ] Workpiece is transported.
- [ ] Machine-loading action occurs.
- [ ] Machine processing/dwell is represented.
- [ ] Workpiece is removed.
- [ ] Finished workpiece is placed.
- [ ] Robot returns HOME.

## Final video

Target:

**60–120 seconds**

Show:

1. Overall cell.
2. UR5 carrier.
3. Carrier flange.
4. Dual-arm mechanism.
5. Workpiece handling.
6. Machine loading.
7. Machine unloading.
8. Final placement.
9. Return to home.

---

# 10. P4 — Quantitative Metrics

Keep the experiment small but reproducible.

## Metric 1 — Cycle time

Measure:

```text
HOME → complete task → HOME
```

Report:

- Trial 1
- Trial 2
- Trial 3
- ...
- Mean cycle time

## Metric 2 — Task success rate

Example format:

| Trial | Complete cycle | Successful |
|---:|---|---|
| 1 | Yes | Yes |
| 2 | Yes | Yes |
| 3 | Yes | Yes |
| 4 | No | No |
| 5 | Yes | Yes |

Then:

```text
Success Rate = Successful Trials / Total Trials × 100
```

## Metric 3 — Joint motion

Possible measurements:

- Maximum shoulder displacement.
- Maximum elbow displacement.
- Total joint travel.

## Metric 4 — Optional planning metrics

Only if MoveIt is successfully integrated:

- Planning time.
- Number of trajectory points.
- Planned path length.

## Minimum experiment

A 5–10 trial demonstration is sufficient for a basic project-level result.

Do NOT claim industrial performance from this experiment.

---

# 11. P5 — MoveIt 2 Decision

## Objective

Determine whether the existing UR5 MoveIt configuration can be reused.

The project already has an existing UR5 MoveIt configuration, so the first step is **inspection**, not rebuilding.

## Step 1 — Inspect

Determine:

- What URDF/Xacro MoveIt currently loads.
- Existing planning groups.
- Existing end-effector definition.
- Existing SRDF.
- Existing controllers.
- Whether the custom carrier flange is included.

## Step 2 — Minimal integration

Attempt only:

```text
UR5
 ↓
carrier flange
 ↓
dual-arm base
```

and determine whether the custom joints can be represented cleanly.

## Step 3 — Decision gate

### OPTION A — Easy integration

If the changes are small:

- Add required links/joints.
- Update SRDF/planning groups.
- Update controller configuration if necessary.
- Test one simple planned motion.

### OPTION B — Moderate integration

If changes are possible but time-consuming:

- Integrate only the UR5/carrier portion.
- Keep dual-arm motion controlled by the existing trajectory node.

### OPTION C — Complex integration

If MoveIt requires major restructuring:

**STOP.**

Keep the existing trajectory controller.

Document:

> MoveIt 2 integration was investigated, but full bimanual planning was retained as future work due to project time and integration complexity.

This is a valid engineering decision.

---

# 12. MoveIt 2 Stop-Loss Rule

Use this rule:

> **If MoveIt 2 consumes more time than the five-station demonstration itself, stop MoveIt work.**

The final project must not depend on MoveIt.

Priority:

```text
Working machine-tending demonstration
          >
MoveIt integration
```

---

# 13. P6 — Documentation

The final documentation should explain both the engineering work and the decisions.

## Recommended structure

```text
CAM-BOT
│
├── 1. Introduction
│
├── 2. Problem Statement
│
├── 3. Motivation
│
├── 4. System Architecture
│
├── 5. UR5 Carrier Integration
│
├── 6. Custom Carrier Flange
│
├── 7. Bimanual Manipulator
│
├── 8. ROS 2 Architecture
│
├── 9. Machine-Tending Environment
│
├── 10. Five-Station Workflow
│
├── 11. Motion Control
│
├── 12. MoveIt 2 Investigation
│
├── 13. Experimental Setup
│
├── 14. Quantitative Results
│
├── 15. Limitations
│
├── 16. Future Work
│
└── 17. Conclusion
```

---

# 14. ROS 2 Architecture to Document

Final architecture should be presented approximately as:

```text
                    CAM-BOT
                       │
                 ROS 2 System
                       │
          ┌────────────┴────────────┐
          │                         │
 carrier_description          carrier_control
          │                         │
          │                  dual_arm_cycle
          │                         │
       Xacro                     /joint_states
          │                         │
          └──────────┬──────────────┘
                     │
            robot_state_publisher
                     │
                   TF tree
                     │
                    RViz
```

If MoveIt is successfully added:

```text
                    MoveIt 2
                       │
              Motion Planning
                       │
              Controller / ROS 2
                       │
                Dual-arm system
```

If MoveIt is not added, it should appear under **future work**, not as a missing core component.

---

# 15. Final Results Table

Prepare a table like:

| Parameter | Result |
|---|---|
| Carrier robot | UR5 |
| Carrier interface | Custom carrier flange |
| Manipulator | Custom dual-arm mechanism |
| Controlled custom joints | 4 |
| Simulation framework | ROS 2 |
| Visualization | RViz |
| Motion control | ROS 2 joint trajectory / joint-state control |
| Task | Machine tending |
| Stations | 5 |
| Workflow | Pick → stage → load → unload → place |
| Trials | 5–10 |
| Mean cycle time | TBD |
| Success rate | TBD |
| MoveIt 2 | Integrated / Investigated / Future Work |

Do not fill TBD values until they are measured.

---

# 16. Engineering Decisions That Must Be Taken

Before continuing, explicitly decide the following.

## Decision 1 — What is the final task?

**Decision:**

> Machine tending in a five-station simulated workspace.

---

## Decision 2 — Is the CNC machine physically simulated?

**Decision: NO.**

Use a static/simple machine representation.

Reason:

> The research focus is carrier-assisted manipulation, not CNC process simulation.

---

## Decision 3 — Is the workpiece physically simulated?

**Decision: Simple visual/kinematic representation.**

Use physics only if it is already easy to implement.

---

## Decision 4 — Is the dual-arm grasp force-controlled?

**Decision: NO.**

Use predefined coordinated motion.

---

## Decision 5 — Is MoveIt mandatory?

**Decision: NO.**

MoveIt is an enhancement.

---

## Decision 6 — Is full bimanual IK mandatory?

**Decision: NO.**

It is future work.

---

## Decision 7 — What constitutes project completion?

Project is considered complete when:

```text
Single launch
      +
5-station world
      +
complete machine-tending sequence
      +
repeatable demonstration
      +
basic metrics
      +
documentation
```

MoveIt is NOT required for completion.

---

# 17. Definition of Done

## Software

- [ ] Workspace builds.
- [ ] Packages discovered by `colcon`.
- [ ] Xacro generates correctly.
- [ ] `check_urdf` passes.
- [ ] Single launch works.
- [ ] RViz loads automatically.
- [ ] Dual-arm controller starts automatically.
- [ ] Complete sequence executes.

## Environment

- [ ] Five stations exist.
- [ ] Machine is visually identifiable.
- [ ] Workpiece exists.
- [ ] Station locations are clearly named.
- [ ] Robot fits within the workspace.

## Demonstration

- [ ] Raw workpiece pickup.
- [ ] Staging movement.
- [ ] Machine loading.
- [ ] Machine dwell.
- [ ] Machine unloading.
- [ ] Finished-part placement.
- [ ] Return home.

## Measurements

- [ ] At least 5 trials.
- [ ] Cycle time recorded.
- [ ] Success/failure recorded.
- [ ] At least one additional motion metric recorded.

## Documentation

- [ ] Architecture diagram.
- [ ] ROS 2 architecture.
- [ ] Workflow diagram.
- [ ] Screenshots.
- [ ] Results table.
- [ ] Limitations.
- [ ] Future work.
- [ ] Final conclusion.

---

# 18. Time Management Strategy

If time becomes extremely limited, use the following priority.

## If 4+ hours remain

```text
Launch
 ↓
5-station world
 ↓
Machine-tending sequence
 ↓
Metrics
 ↓
MoveIt
 ↓
Documentation
```

## If 2–4 hours remain

```text
Launch
 ↓
5-station world
 ↓
Machine-tending sequence
 ↓
Metrics
 ↓
Documentation
```

Skip MoveIt unless it is immediately straightforward.

## If <2 hours remain

```text
Launch
 ↓
Simple 5-station environment
 ↓
Existing motion cycle adapted to stations
 ↓
3–5 trials
 ↓
Screenshots/video
 ↓
Documentation
```

Do NOT start major MoveIt work.

---

# 19. Things That Should NOT Be Changed Now

The following working components should be protected from unnecessary refactoring:

- Existing UR5 description.
- Existing carrier flange structure.
- Existing dual-arm URDF.
- Existing four-joint names.
- Existing `dual_arm_cycle.py` architecture.
- Existing smooth interpolation.
- Existing ROS package structure.

Only modify what is necessary to connect the final workflow.

---

# 20. Final Presentation Story

The project presentation should tell this story:

```text
INDUSTRIAL PROBLEM
        ↓
Single manipulator requires repeated global repositioning
        ↓
CAM-BOT CONCEPT
        ↓
UR5 acts as carrier
        ↓
Custom flange carries local bimanual manipulator
        ↓
DUAL-ARM SYSTEM
        ↓
Local manipulation around machine workspace
        ↓
MACHINE-TENDING CELL
        ↓
Five-station sequential workflow
        ↓
EXPERIMENTAL DEMONSTRATION
        ↓
Cycle time + success rate + motion metrics
        ↓
CONCLUSION
```

## Core claim

Use a conservative claim:

> **CAM-BOT demonstrates the feasibility of a carrier-assisted bimanual manipulation architecture for simulated machine-tending tasks.**

Do NOT claim industrial deployment or production-ready performance.

---

# 21. Final Project Boundary

The final boundary is:

```text
                    COMPLETED
                         │
        ┌────────────────┴────────────────┐
        │                                 │
   GLOBAL MOTION                      LOCAL MOTION
        │                                 │
       UR5                         Dual-arm mechanism
        │                                 │
        └──────────────┬──────────────────┘
                       │
                Carrier Flange
                       │
                       ▼
              MACHINE-TENDING CELL
                       │
          ┌────────────┼────────────┐
          │            │            │
        INPUT        MACHINE      OUTPUT
          │            │            │
          └────────────┴────────────┘
                       │
                 5-STATION FLOW
                       │
                       ▼
                 FINAL RESULTS
```

The project should be considered a **simulation/prototype feasibility demonstration**, not a finished industrial manipulation system.

---

# 22. Immediate Next Actions

Start with these tasks in order:

### TASK 01 — Fix launch

**Goal:** one-command startup.

```bash
ros2 launch carrier_description dual_arm_demo.launch.py
```

---

### TASK 02 — Build the five-station world

Create:

```text
S1 — Raw/Input
S2 — Staging
S3 — CNC/Machine
S4 — Output
S5 — Finished
```

Keep geometry simple.

---

### TASK 03 — Add workpiece

Create one simple workpiece and define its task positions.

---

### TASK 04 — Convert current trajectory to machine tending

Use named states:

```text
HOME
PICK_RAW
STAGE
LOAD_MACHINE
MACHINE_DWELL
UNLOAD_MACHINE
PLACE_FINISHED
HOME
```

---

### TASK 05 — Run complete demonstration

Run at least 5 successful/attempted cycles.

---

### TASK 06 — Record metrics

Record:

```text
Trial
Cycle time
Success/failure
Joint travel / another simple metric
```

---

### TASK 07 — Investigate MoveIt

Only after the demonstration is stable.

---

### TASK 08 — Capture final evidence

Collect:

- Overall cell screenshot.
- UR5 + flange screenshot.
- Dual-arm screenshot.
- Machine-loading screenshot.
- Machine-unloading screenshot.
- RViz TF/robot screenshot if useful.
- Short final video.

---

### TASK 09 — Documentation

Finalize:

- System architecture.
- Implementation.
- Workflow.
- Results.
- Limitations.
- Future work.
- Conclusion.

---

# 23. Final Checklist

```text
[ ] P0  Single launch
[ ] P1  Five-station world
[ ] P2  Machine-tending sequence
[ ] P3  Complete demonstration
[ ] P4  Quantitative metrics
[ ] P5  MoveIt investigation
[ ] P6  Documentation
[ ] Final screenshots
[ ] Final video
[ ] Final presentation
```

## Golden Rule

> **A smaller complete system is more valuable than a larger partially implemented system.**

The target is therefore not to maximize the number of robotics features.

The target is to produce a **stable, reproducible, clearly documented CAM-BOT machine-tending demonstration** that shows:

**UR5 carrier → custom flange → bimanual manipulator → five-station workflow → measured results.**
