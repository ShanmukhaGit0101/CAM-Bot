# CAMBOT — Design Decisions

Decisions and the reasoning behind them. Append; don't rewrite history.

---

## D-01 — Waypoints are joint configurations, not Cartesian poses

**Date:** Phase 1 · **Status:** Adopted

Hand-picked Cartesian targets produced repeated planning failures (MoveIt error
codes `99999` and `-4`) even for points that looked geometrically reasonable
and adjacent to points that worked.

Cartesian coordinates carry no guarantee of a reachable, well-conditioned,
collision-free IK solution. Stations are instead taught by positioning the UR5
with MoveIt's RViz interactive marker and recording `/joint_states`, making
every configuration reachable by construction.

**Trade-off:** joint configurations are tied to this base placement. If the
carrier base moves, they must be re-taught. Accepted for now; Phase 6 will
revisit when carrier placement becomes a variable.

---

## D-02 — Custom geometry attaches after `tool0`

**Date:** Phase 1 · **Status:** Adopted

`ur_description` is included via its official `ur_macro.xacro` rather than
vendored. All custom links attach below `tool0`, so upstream UR packages can be
updated without merge conflicts and the official
`wrist_3_link → flange → tool0` chain stays authoritative.

---

## D-03 — Stop mass experiments at EXP03

**Date:** Phase 2 · **Status:** Adopted

EXP01–03 cover distal, mid, and proximal links. A fourth perturbation would add
another point to a noisy dataset without answering a new question, and the
derived-acceleration metric is already at the edge of what unsynchronized
recordings support.

The binding constraint on the project is architectural (the CA → CF → BM
interface), not UR5 dynamics. Effort moves to Phase 4.

---

## D-04 — Defer the real bimanual design

**Date:** Phase 4 · **Status:** Adopted

The bimanual module is represented by a four-joint placeholder — two simple arms
of shoulder + elbow — not a designed mechanism.

Designing real arms before knowing the flange interface, the carrier's reachable
workspace, and the best carrier placement would mean designing against unknown
constraints and redoing it. The placeholder is enough to validate mounting
geometry, spatial arrangement, reach, collision envelope, and visualization.

**Consequence:** the current `dual_arm_cycle` moves four joints independently.
It resembles a pick-and-place but the arms do not hold a common object. That is
acceptable for a placeholder and must be stated whenever the demo is shown.

---

## D-05 — Interpret derived accelerations with caution

**Date:** Phase 2 · **Status:** Adopted

Baseline and experiment recordings differ in sample count and duration, and
acceleration is obtained by applying `numpy.gradient` twice. Double numerical
differentiation of unsynchronized data amplifies sampling noise heavily.

Results are reported as trajectory *statistics*, never as torque, motor current,
or physical acceleration capability. Percentage changes in the hundreds are
presented as artifacts unless independently corroborated.

---

## D-06 — `waypoints.yaml` becomes the single waypoint source

**Date:** Phase 4 · **Status:** ⚠️ Agreed, not implemented

Waypoints currently exist twice: in `config/waypoints.yaml` (which no node
reads) and hardcoded inside `machine_shop_joint_cycle.py`. Two sources will
drift.

**Action:** move `waypoints.yaml` inside `carrier_description`, install it via
`setup.py` `data_files`, and load it at node startup.
