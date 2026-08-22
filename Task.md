# CAMBOT — Task Allocation

## Project

**CAMBOT — Carrier-assisted Adaptive Manipulation with Bimanual Operational Technology**

The project is divided into parallel workstreams so that mechanical design, manipulator modelling, software development, and system integration can progress simultaneously.

---

## Team Responsibilities

| Member     | Primary Responsibility           | Supporting Responsibilities                              |
| ---------- | -------------------------------- | -------------------------------------------------------- |
| **Shannu** | Manipulator Kinematics & Control | System architecture, integration, technical coordination |
| **Tanmay** | Mechanical & Carrier Design      | CAD, mechanism development, structural design            |
| **Ayush**  | Software & Digital Systems       | Coding, simulation software, GitHub, PPT/design support  |

---

# 1. Shannu — Manipulator Kinematics & Control

### Primary Tasks

* [ ] Define manipulator configuration and DOF requirements.
* [ ] Develop forward kinematics model.
* [ ] Develop inverse kinematics model.
* [ ] Define coordinate frames and transformation conventions.
* [ ] Analyze manipulator workspace.
* [ ] Develop Jacobian formulation.
* [ ] Study singularities and manipulability.
* [ ] Develop joint-space and task-space control strategies.
* [ ] Develop trajectory generation methods.
* [ ] Coordinate bimanual manipulation.
* [ ] Integrate manipulator control with carrier positioning.
* [ ] Validate kinematics and control in simulation.
* [ ] Analyze motion efficiency and task performance.

### Deliverables

* Manipulator kinematic model
* DH/transform documentation
* Workspace analysis
* Control architecture
* Trajectory generation module
* Bimanual coordination strategy
* Simulation results
* Technical documentation

---

# 2. Tanmay — Mechanical & Carrier Design

### Primary Tasks

* [ ] Define overall mechanical architecture.
* [ ] Develop carrier mechanism concept.
* [ ] Design manipulator mounting arrangement.
* [ ] Develop CAD models.
* [ ] Perform dimensional and workspace studies.
* [ ] Design end-effector mounting interfaces.
* [ ] Analyze structural constraints.
* [ ] Select suitable mechanical components.
* [ ] Prepare preliminary BOM.
* [ ] Optimize carrier and manipulator placement.
* [ ] Prepare fabrication-ready models/drawings.
* [ ] Support physical prototype development.

### Deliverables

* System CAD model
* Carrier design
* Manipulator mounting design
* End-effector interface
* BOM
* Mechanical drawings
* Design analysis
* Prototype-ready design

---

# 3. Ayush — Software, Simulation & Digital Systems

### Primary Tasks

* [ ] Set up GitHub repository and project workflow.
* [ ] Maintain repository structure and documentation.
* [ ] Develop simulation environment.
* [ ] Implement robot models in simulation.
* [ ] Develop ROS/ROS2 software modules where required.
* [ ] Implement communication interfaces between system components.
* [ ] Support motion-planning implementation.
* [ ] Develop data logging and analysis scripts.
* [ ] Support visualization and simulation debugging.
* [ ] Maintain Git branches, commits, and issue tracking.
* [ ] Prepare project presentations and technical diagrams.
* [ ] Support integration of mechanical and control modules.

### Deliverables

* Simulation environment
* Software modules
* ROS/ROS2 packages where applicable
* Data-processing scripts
* GitHub repository
* Visualization tools
* Technical diagrams
* Presentation material

---

# 4. Joint Team Tasks

These tasks require collaboration between multiple members.

### System Development

* [ ] Finalize system requirements.
* [ ] Finalize task sequence for CNC machine tending.
* [ ] Define carrier and manipulator interfaces.
* [ ] Define communication architecture.
* [ ] Establish simulation-to-hardware workflow.
* [ ] Integrate mechanical, software, and control subsystems.

### Validation

* [ ] Define performance metrics.
* [ ] Create benchmark task scenarios.
* [ ] Measure task completion time.
* [ ] Compare conventional and carrier-assisted approaches.
* [ ] Analyze total motion distance.
* [ ] Analyze workspace utilization.
* [ ] Evaluate bimanual coordination.
* [ ] Document experimental results.

### Documentation

* [ ] Maintain literature review.
* [ ] Maintain project documentation.
* [ ] Update CAD and simulation documentation.
* [ ] Maintain experiment logs.
* [ ] Prepare review presentations.
* [ ] Prepare final report.
* [ ] Prepare research/publication material if applicable.

---

# 5. GitHub Workflow

### Branch Structure

```text
main
│
├── development
│
├── feature/kinematics
├── feature/control
├── feature/carrier-design
├── feature/simulation
└── feature/perception
```

### Commit Convention

Use clear commit messages:

```text
feat: add inverse kinematics solver
feat: add carrier simulation model
fix: correct transformation matrix
docs: update system architecture
test: add workspace validation
refactor: reorganize ROS packages
```

### General Rules

* Do not directly push experimental/broken code to `main`.
* Create a feature branch for major development.
* Keep commits small and meaningful.
* Update documentation when implementing major features.
* Do not commit large generated files or unnecessary build files.
* Review code before merging into `main`.
* Keep simulation, hardware, and documentation organized.

---

# 6. Priority Roadmap

## Phase 1 — Foundation

* [ ] Literature review
* [ ] Problem definition
* [ ] System requirements
* [ ] Initial architecture
* [ ] Task sequence definition

## Phase 2 — Design

* [ ] Carrier concept
* [ ] Manipulator configuration
* [ ] CAD development
* [ ] Kinematic modelling
* [ ] Workspace analysis

## Phase 3 — Simulation

* [ ] Robot model
* [ ] Carrier simulation
* [ ] Manipulator simulation
* [ ] Motion planning
* [ ] Control implementation

## Phase 4 — Integration

* [ ] Carrier + manipulator integration
* [ ] Bimanual coordination
* [ ] Task execution
* [ ] Performance measurement

## Phase 5 — Validation

* [ ] Benchmark experiments
* [ ] Performance comparison
* [ ] Optimization
* [ ] Results analysis
* [ ] Final documentation

---

## Ownership Principle

Each member owns their primary workstream but should maintain interfaces with the other workstreams.

**Mechanical design → Kinematics → Simulation → Control → Integration → Validation**

The goal is not isolated completion of individual modules, but successful integration into a single CAMBOT system.
