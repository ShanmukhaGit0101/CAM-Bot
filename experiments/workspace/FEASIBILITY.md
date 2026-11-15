# Placeholder IK and clearance diagnostics

`tools/analyze_module_feasibility.py` extends the earlier geometric proxy with
bounded numerical IK and oriented-box separation checks. It is an offline
assessment of the **existing placeholder URDF**, not the newer lightweight CAD
concept, a MoveIt planner, controller authorization or a physical design claim.
The original visual configuration and sealed study are unchanged.

Run from the repository root in a separate Python environment with
`experiments/workspace/requirements-feasibility.txt` installed:

```bash
python -m unittest tools.test_analyze_module_feasibility -v
python -m tools.analyze_module_feasibility \
  --urdf experiments/workspace/runs/model-study-20261107/model.urdf \
  --output /tmp/cambot-feasibility-NEW --samples 2000 --seed 15
```

The output directory must not exist. Inputs and analysis code are hashed; the
report records source commit, checkout status, parameters, every target attempt
and every workflow segment. `local_joint_samples.csv` preserves all sampled
four-joint configurations, both endpoint positions and self-clearance bounds.

## What is evaluated

- Existing URDF limits, joint origins and axes are used without changing the
  official carrier chain. Each putative tool is the distal centre of its
  forearm collision box. These are **not specified gripper TCPs**.
- Deterministic multistart bounded least squares solves each arm independently.
  Acceptance requires position error at most 1 mm. The solver also supports a
  required orientation and angular tolerance; tests cover recovery and rejection.
  Actual station orientation requirements are missing, so this study explicitly
  does **not** apply invented station orientations. `NO_SOLUTION_FOUND` is a
  numerical result, not a proof of global infeasibility.
- Both forearm endpoints are tested against the common existing proxy target.
  This diagnoses the old proxy assumption; a real two-contact grasp needs two
  separate specified contact frames and a workpiece/tool model.
- The separating-axis test uses all 15 box axes. A positive maximum projection
  gap is a **lower bound** on separation; zero/negative means touching/overlap.
  It is neither exact Euclidean clearance nor penetration depth. A pair passes
  the conservative screening only when this bound is at least 5 mm.
- Module boxes are checked against nonadjacent module boxes and all solid station
  boxes. Adjacent parent/child pairs are excluded. Carrier links, flange, cables,
  grippers, ground and workpiece are omitted. The CNC box has no modeled opening;
  overlaps identify missing geometry as well as possible path conflicts.
- Visual workflow waypoints are interpolated simultaneously in joint space at
  increments no larger than 0.05 rad. This is a sampled diagnostic, not the live
  timing law or a continuous collision guarantee. Failed samples are retained.
- Five carrier translations are compared using existing visual carrier joint
  configurations; carrier poses are not reoptimized. No placement recommendation
  or executable path cost is claimed. Local four-joint samples evaluate only
  nonadjacent module self-clearance, not whole-cell workspace feasibility.

## Consequence for later milestones

This tool advances Tasks 9/12/14 but does not close them. Real grasp frames,
orientation/approach requirements, complete geometry, continuous path validation
and uncertainty remain necessary. Failed diagnostics must not be bypassed by
promoting visual targets or mock feedback to controller/physical validation.
Tasks 10/13 require qualified complete tending paths and manipulation outcomes;
synthetic carrier or bimanual protocol tests cannot supply that evidence.
