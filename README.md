# CAMBOT

## Carrier-assisted Adaptive Manipulation with Bimanual Operational Technology

CAMBOT is a carrier-assisted bimanual robotic manipulation system designed to improve the efficiency of repetitive industrial tasks such as CNC machine tending.

Conventional robotic manipulators often perform both global positioning and local manipulation using the same motion capabilities. This can result in unnecessary global movements, longer cycle times, increased energy consumption, and inefficient utilization of the robot's local workspace.

CAMBOT addresses this challenge through a **hierarchical manipulation architecture**, where a mobile/carrier mechanism performs global positioning while two manipulators perform coordinated local operations.

## Objectives

* Develop a carrier-assisted dual-arm manipulation architecture.
* Separate global positioning from local manipulation.
* Enable coordinated bimanual manipulation for machine-tending operations.
* Reduce unnecessary global robot motion.
* Improve workspace utilization and task efficiency.
* Develop and validate the system through simulation and hardware implementation.

## System Concept

The proposed system consists of three primary components:

1. **Carrier System**
   Provides global positioning and transports the manipulation system between work locations.

2. **Bimanual Manipulation System**
   Two robotic manipulators perform coordinated local operations such as loading, unloading, holding, and transferring workpieces.

3. **Hierarchical Control System**
   Coordinates carrier motion, manipulator motion, perception, planning, and task execution.

### Conceptual Architecture

```text
                    CAMBOT
                       │
          ┌────────────┴────────────┐
          │                         │
   Global Positioning        Local Manipulation
          │                         │
     Carrier System          ┌──────┴──────┐
          │                  │             │
          │              Left Arm      Right Arm
          │                  │             │
          └──────────┬───────┴───────┬─────┘
                     │               │
              Hierarchical Task & Motion
                     │
              CNC Machine Tending
```

## Key Research Areas

* Robotic Manipulation
* Bimanual Coordination
* Manipulator Kinematics
* Motion Planning
* Hierarchical Control
* Carrier-assisted Manipulation
* Industrial Robotics
* Machine Tending
* Robot Workspace Optimization
* Simulation and Digital Validation

## Repository Structure

```text
cambot/
├── README.md
├── TASKS_ALLOC.md
├── LICENSE
│
├── docs/
│   ├── proposal/
│   ├── literature/
│   └── presentations/
│
├── simulation/
│   ├── urdf/
│   ├── worlds/
│   ├── launch/
│   └── config/
│
├── src/
│   ├── carrier/
│   ├── manipulator/
│   ├── bimanual_control/
│   ├── motion_planning/
│   └── perception/
│
├── hardware/
│   ├── cad/
│   ├── electronics/
│   └── bom/
│
├── scripts/
├── data/
├── results/
└── tests/
```

## Development Workflow

The project will follow an iterative workflow:

```text
Literature Review
       ↓
System Requirements
       ↓
Mechanical & System Design
       ↓
Kinematic Modelling
       ↓
Simulation
       ↓
Control & Motion Planning
       ↓
Integration
       ↓
Experimental Validation
       ↓
Performance Analysis
```

## Expected Outcomes

The project aims to demonstrate that separating global carrier positioning from local bimanual manipulation can reduce unnecessary robot motion and improve the efficiency of repetitive machine-tending operations.

The final system will be evaluated using parameters such as task completion time, motion distance, workspace utilization, coordination performance, and energy/motion efficiency.

## Project Status

**Current Stage:** Design and system development

The repository will be progressively updated with CAD models, simulation environments, control algorithms, documentation, experimental data, and results.

## Team

**CAMBOT — TOPS Programme 2026**

See [`TASKS_ALLOC.md`](TASKS_ALLOC.md) for team responsibilities and project work allocation.

## License

This project is developed as part of the TOPS Programme 2026. Licensing and publication details will be finalized as the project progresses.
