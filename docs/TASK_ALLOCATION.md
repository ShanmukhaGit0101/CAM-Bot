# CAMBOT — Task Allocation

Work is split into parallel workstreams so mechanical design, manipulator
modelling, software, and integration can progress simultaneously.

| Member | Primary responsibility | Supporting |
|---|---|---|
| **Shannu** | Manipulator kinematics & control | System architecture, integration, technical coordination |
| **Tanmay** | Mechanical & carrier design | CAD, mechanism development, structural design |
| **Ayush** | Software & digital systems | Simulation software, GitHub, presentation support |

**Ownership principle.** Each member owns a workstream but maintains the
interfaces to the others:

```text
Mechanical design → Kinematics → Simulation → Control → Integration → Validation
```

The goal is not isolated completion of modules but integration into one system.

---

## Shannu — Manipulator kinematics & control

- [ ] Define manipulator configuration and DOF requirements
- [ ] Forward kinematics model
- [ ] Inverse kinematics model
- [ ] Coordinate frames and transformation conventions
- [ ] Workspace analysis
- [ ] Jacobian formulation
- [ ] Singularity and manipulability study
- [ ] Joint-space and task-space control strategies
- [ ] Trajectory generation
- [ ] Bimanual coordination
- [ ] Integrate manipulator control with carrier positioning
- [ ] Validate kinematics and control in simulation
- [ ] Motion efficiency and task performance analysis

**Deliverables:** kinematic model · DH/transform documentation · workspace
analysis · control architecture · trajectory generation module · bimanual
coordination strategy · simulation results · technical documentation

---

## Tanmay — Mechanical & carrier design

- [ ] Overall mechanical architecture
- [ ] Carrier mechanism concept
- [ ] Manipulator mounting arrangement
- [ ] CAD models
- [ ] Dimensional and workspace studies
- [ ] End-effector mounting interfaces
- [ ] Structural constraint analysis
- [ ] Mechanical component selection
- [ ] Preliminary BOM
- [ ] Carrier and manipulator placement optimization
- [ ] Fabrication-ready models and drawings
- [ ] Support prototype development

**Deliverables:** system CAD model · carrier design · mounting design ·
end-effector interface · BOM · mechanical drawings · design analysis ·
prototype-ready design

---

## Ayush — Software, simulation & digital systems

- [ ] Repository structure and workflow
- [ ] Maintain documentation
- [ ] Simulation environment
- [ ] Robot models in simulation
- [ ] ROS 2 modules
- [ ] Communication interfaces between components
- [ ] Support motion-planning implementation
- [ ] Data logging and analysis scripts
- [ ] Visualization and simulation debugging
- [ ] Git branches, commits, issue tracking
- [ ] Presentations and technical diagrams
- [ ] Support integration of mechanical and control modules

**Deliverables:** simulation environment · software modules · ROS 2 packages ·
data-processing scripts · repository · visualization tools · technical
diagrams · presentation material

---

## Joint tasks

**System development**

- [ ] Finalize system requirements
- [ ] Finalize CNC machine-tending task sequence
- [ ] Define carrier and manipulator interfaces
- [ ] Define communication architecture
- [ ] Establish simulation-to-hardware workflow
- [ ] Integrate mechanical, software, and control subsystems

**Validation**

- [ ] Define performance metrics
- [ ] Create benchmark task scenarios
- [ ] Measure task completion time
- [ ] Compare conventional vs carrier-assisted approaches
- [ ] Analyze total motion distance
- [ ] Analyze workspace utilization
- [ ] Evaluate bimanual coordination
- [ ] Document experimental results

**Documentation**

- [ ] Maintain literature review
- [ ] Maintain project documentation
- [ ] Update CAD and simulation documentation
- [ ] Maintain experiment logs
- [ ] Prepare review presentations
- [ ] Prepare final report
- [ ] Prepare publication material if applicable
