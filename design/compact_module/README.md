# Original compact UR5-mounted module study

The user authorized an original design on 2026-11-15 (Asia/Calcutta), using
explicit assumptions instead of the supplied reference CAD. No SDA20D geometry
is imported or scaled. This is a **preliminary engineering model**, not a
manufacturing release or completed Tasks 7–15 acceptance.

[Requirements](requirements.json) define a 240 × 120 × 6 mm base, inboard
shoulders at ±90 mm, 140 mm shoulder-to-elbow spacing, 130 mm forearm tubes,
and 50 g payload allocation per arm. The 2 kg complete-module target is a
chosen design budget, not a verified robot rating. Four 80 g arm actuators and
two 80 g grippers are mass allocations, not selected products.

The original mechanism includes a mounting disc, matching through-hole patterns,
connected shoulder pedestals, yaw-shaft envelopes, hollow upper arms, elbow
forks, forearm pivot lugs and cross-pin envelopes. Elbow fork clearance is
geometrically checked at sampled angles. Bearings, fits, couplings, retention,
actuator interfaces, gripper internals and cabling still need design/selection.
The mounting pattern is provisional until checked against the actual carrier.

## Generate and inspect

Use the existing `tools/cad/requirements.txt` environment from repository root:

```bash
python tools/cad/build_compact_module.py \
  design/compact_module/requirements.json /tmp/cambot-compact-NEW
python -m tools.cad.check_compact_motion \
  design/compact_module/requirements.json /tmp/cambot-compact-clearance-NEW
python -m unittest discover -s tools/cad -p 'test_*.py' -v
```

Both output directories must be new. The generator emits STEP, SVG, a standalone
URDF, five local-link STL meshes and a mass-allocation report. Millimetre meshes
are explicitly scaled by 0.001 in URDF. The URDF's relative mesh paths refer to
its generated folder; it is an offline asset, not an installed ROS package.

There are two joints per arm: shoulder Z and elbow X. Their ±1.2 rad bounds,
1 Nm effort and 0.5 rad/s velocity fields are provisional study values, **not
actuator ratings**. No inertias, controllers or actuated gripper jaws are
emitted. Envelope-tip frames are not calibrated tool/contact frames. This
limited-DOF geometry cannot imply arbitrary position/orientation reachability.

The prototype is isolated from `src/` and the accepted visual demonstration.
Prior controller tests therefore do not establish execution of this new model.
An integration must qualify mounting, model limits, collision geometry and
contact frames before producing new controller-backed tending evidence.

## Current results and limits

The retained [generated artifacts](generated/report.json) contain 14 valid
solids. The STEP round-trip preserves 14 valid solids. The modeled parts,
actuator allocations and two payloads subtotal **1.522751944968146 kg**,
leaving **0.4772480550318541 kg** of the target budget for omitted components.
Actual complete mass and UR5 payload/inertia compatibility remain unestablished.
Pins currently use assumed aluminum density in the worksheet; selecting steel
pins or real hardware changes the budget and requires regeneration.

The [81-configuration study](clearance/sampled_clearance.json) passed **70/81**
configurations at a 5 mm nonadjacent-module separation margin. The 11 failures
remain recorded. Overlap and containment are detected by solid intersection;
otherwise OpenCascade supplies shape distance. Adjacent links are excluded;
elbow parent/child interference has separate sampled tests. These are discrete
samples, not continuous collision-free paths, a workspace coverage probability,
or a comparison with the older placeholder's different sampling distribution.
Carrier, workcell, actual actuator/cable and workpiece collisions are absent.

The [test log](tests.log) records 17 passing CAD/load tests, including analytic
load calculations, missing-input rejection, mount-hole volumes, valid connected
solids, sampled elbow motion, containment detection and URDF/FK export checks.
No new ROS or hardware replay is claimed for this CAD-only increment.

Full task closure still needs complete mechanism/interface selection, qualified
cell paths and manipulation feedback, whole-cell simulation, and physical
assembly/calibration/trials. See [STATUS.md](../../docs/STATUS.md).
