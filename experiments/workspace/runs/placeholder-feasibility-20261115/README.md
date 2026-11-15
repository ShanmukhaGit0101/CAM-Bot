# Placeholder feasibility diagnostics — 2026-11-15 UTC

Source `44febde`, agent-run in a clean detached checkout. Python/NumPy/SciPy
versions, input/code hashes and source status are recorded in `report.json`.
The archived input URDF is the original placeholder model, not the new CAD
concept. Methods and reproduction: [FEASIBILITY.md](../../FEASIBILITY.md).

```bash
python -m tools.analyze_module_feasibility \
  --urdf experiments/workspace/runs/model-study-20261107/model.urdf \
  --output /workspace/cambot-task8-final/feasibility --samples 2000 --seed 15
```

Observed results:

- **0 of 6 common-target checks matched both arm endpoints within 1 mm** for
  each of the five carrier placement candidates. Every arm's best-fit error and
  joints are retained. This is a numerical diagnostic using forearm box ends,
  not a proof that an appropriately designed two-contact grasp is impossible.
- **11 of 12 sampled visual workflow segments** contain a module/self/station
  pair with a SAT separation lower bound below the selected 5 mm margin. Each
  segment retains its sample count, worst gap and first violating pairs.
- **1,166 of 2,000 local four-joint samples** passed the nonadjacent-module
  self-clearance screen. All samples are in `local_joint_samples.csv`. This is
  not whole-robot collision-free coverage or a measured boundary margin.
- Actual station tool orientations and grasp contact offsets are unavailable;
  station orientation constraints were not invented. Orientation-capable IK
  itself is covered by synthetic recovery/rejection tests.

The station CNC is a solid box with no access opening. UR5, flange, gripper,
workpiece and cable geometry are excluded. Adjacent module pairs are excluded.
Path checks sample joint interpolation at <=0.05 rad increments; continuous
clearance and dynamic execution are not established. Positive SAT gaps are
lower bounds, not exact distance; negative magnitude is not penetration depth.
See report scope fields before using any result.

`development/` preserves the initial analysis before commit, whose dirty source
status is explicit. The top-level report is the repeat on committed clean code.
No original AY dataset, result or numerical claim was overwritten. These
findings prevent promoting visual waypoints into validated controller targets;
no physical placement recommendation is made.
