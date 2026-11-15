# Contribution record and speaking roles

This follows the team's documented workstreams in `docs/TASK_ALLOCATION.md`.
Workstream responsibility is not a claim that every planned task was completed.
The old unchecked task allocation is a historical plan, not the final status.

| Member | Documented workstream | Suggested presentation contribution |
|---|---|---|
| Shannu / Shanmukha | Manipulator kinematics, control, architecture and integration | Explain the carrier/local-arm split, frames, UR5 baseline, kinematic studies and coordination concept. |
| Tanmay | Mechanical and carrier design, CAD and structural concepts | Explain the flange/mounting requirements, design choices and evolution from placeholder to compact concept. |
| Ayush Ranjan | Software, simulation, repository, documentation and integration | Run the demonstration; explain the FSM, ROS interfaces, logging, reproducibility and measured results. |

## Artifacts to show across the workstreams

- **Carrier foundation:** official UR5 description, historical HOME/P1–P4 study
  and machine-shop recording; `docs/progress/phase1-carrier-baseline.md` and
  `media/2026-08-24-machine-shop-cycle.webm`. That older recording is a carrier
  baseline, not the later five-station tending demonstration.
- **Mechanical architecture:** carrier flange/interface and four-joint module,
  `src/carrier_description/urdf/`; original compact concept and generated models
  in `design/compact_module/`.
- **Kinematics and studies:** 20,006 carrier FK samples, five assumed placements,
  historical mass-sensitivity experiments, and later limited IK/clearance studies.
  See `experiments/workspace/` and `experiments/mass_sensitivity/`.
- **Integrated software:** five-station workcell, coordinator, FSM, one-shot
  start/cancel/reset, visual workpiece state, trial logger and analysis tools.
- **Verification:** AY-01–AY-13 evidence/ledger, independent visual reproduction,
  failure/shutdown tests and separate mock-controller protocol experiments.
- **Communication:** this presentation, demonstration guide, evidence-backed
  results and scoped final report.

## Attribution rules for the final presentation

Git history contains contributions under Ayush Ranjan and ShanmukhaGit0101.
It does not establish individual authorship for every CAD file or off-repository
activity. Tanmay's documented role should be acknowledged; do not invent commits,
measurements, fabrication or tests to make the contribution table look complete.

The later original compact CAD, standalone analysis utilities and presentation
pack were developed with AI assistance at Ayush's direction. Do not attribute
those automatically to Tanmay or Shannu. Team members may describe the decisions
and review they actually contributed. Suggested speaking roles above are talk
assignments, not a substitute for an authorship record.

Credit ROS 2, RViz, Universal Robots' description packages, ros2_control,
CadQuery/OpenCascade and the other open-source dependencies. Hardware manufacture,
physical grasp validation and physical trials are not claimed contributions.
