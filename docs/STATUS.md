# CAM-BOT status and evidence levels

Updated 2026-11-15 (Asia/Calcutta). **Final delivery: COMPLETE within the accepted
visual-demonstrator scope; presentation package prepared.** See
[project closeout](PROJECT_CLOSEOUT.md) and [presentation](../presentation/README.md). This is the only project status matrix. Each AY record,
including prior state, options, exact files, commands, results, limitations and
next action, is in the [versioned evidence ledger](ayush/ledger.json).
The [2026-11-05 documentation repair](evidence/AY-13/reproducibility_repair.md)
adds offline validation and evidence clarification without changing dispositions.
The [2026-11-06 agent Humble replay](evidence/AY-13/agent_replay_20261106/README.md)
adds a fresh build, package tests and live visual success/failure/cancellation
evidence. The [consolidated runtime repair](evidence/AY-13/runtime_repair_20261107/README.md)
fixes impossible-target classification and coordinator shutdown, with focused
regressions and five interrupted-trial passes using a locally rebuilt RViz
patch. The [reproducible-image replay](evidence/AY-13/reproducible_image_20261107/README.md)
now integrates the pinned patch and passes the final clean-checkout suite,
including idle shutdown and five active interruptions. The subsequent
[independent human review](evidence/AY-13/independent_repeat.md) records Ayush
Ranjan’s clean-checkout technical/manual replay of `6df990b`, PASS acknowledgement
and explicit declaration of independent review, closing AY-13 in visual scope.

| Level | Meaning | Present evidence |
|---|---|---|
| Available code | Source, installed assets, offline contracts | Two core Humble packages plus an optional controller testbed; Xacro/URDF; 48 regression tests ([log](evidence/AY-10/final_tests.log)) |
| Visual-only run | Live ROS/TF/RViz and visual adapter transitions | [AY-10 raw manifest](../experiments/machine_tending/runs/ay10-visual-20261015-03/raw/manifest.json), [probe](../experiments/machine_tending/runs/ay10-visual-20261015-03/raw/probe.log), [screenshot](../experiments/machine_tending/runs/ay10-visual-20261015-03/raw/rviz_runtime.png) |
| Actuated simulated run | Controller results and simulated feedback | Complete actuated tending remains **unverified**; isolated GenericSystem controller feedback is recorded below. Historical [Phase 1](progress/phase1-carrier-baseline.md) and [Phase 4](progress/phase_4.md) reports do not establish current controller operation. |
| Measured complete cycle | Declared timing boundary, complete attempted FSM, raw events | **Five visual cycles only**; [methods/results](../experiments/machine_tending/README.md) |

Workcell dimensions and visual carrier poses are temporary assumptions. The
reachability check is a geometric proxy, not IK or collision checking.
Controller targets S1–S4 are unvalidated and S5 has no taught target.
Task 6 (measured geometry and station-target validation) remains pending.
The [survey and candidate-target intake](WORKCELL_SURVEY.md) supplies separate
blank records for measurements, provenance and validation; it does not change
the working demonstration or establish controller readiness.

Task 7 (UR5 controller integration) is **PARTIAL**: an isolated
[ros2_control mock testbed](TASK7_CONTROLLER.md) now verifies the production
carrier action method against the real joint trajectory controller, including
feedback, rejection, controller errors, cancellation and timeout. A fresh
checkout passed 73 package results (0 failures, 2 skips) and all eight live
protocol checks, with one broadcaster and clean shutdown; see
[retained evidence](evidence/TASK-07/mock_controller_20261114/README.md).
GenericSystem supplies mock state, not physical feedback or dynamics. Actual
UR driver/hardware validation and complete controller-backed tending remain
unverified. No station validation flags or bimanual feedback claims changed.

Task 13 now also has a separate [20-cycle synthetic carrier baseline](evidence/TASK-13/carrier_mock_20261114/README.md):
20 successes, zero attempted failures, with controller feedback and return-position
checks. These are mock carrier cycles, not complete tending cycles; the full
10–20-cycle tending baseline remains pending. The
[Tasks 7–15 dependency record](CONTROLLER_NEXT_STEPS.md) identifies the missing
interfaces, geometry and hardware evidence needed for subsequent milestones.

Task 15 (detailed mechanical design) remains **PARTIAL**. The
[user-supplied SDA20D CAD assessment](evidence/CAD/SDA20D/README.md) now informs a
[parameterized small-module concept](../design/bimanual_concept/README.md),
with a generated STEP layout and structural-volume worksheet. The reference is
not a replacement for the UR5 carrier. One imported reference body fails CAD
validity checks. The new concept has seven valid geometric components, but no
validated brackets, bearings, actuators, grippers or mounting load path. Its
approximately 1.022 kg structural-only estimate excludes those components;
total payload compatibility and physical validation remain unestablished.
Tasks 8–14 retain the dependencies in the controller/manipulation record above;
static CAD does not close their runtime or hardware acceptance gates.

## Deferred extensions: Tasks 7–15 (outside final delivery)

The user has closed the project at the visual-demonstrator and presentation
scope. The technical states below are retained honestly; they are future-work
readiness, not blockers to the final project. See [closeout](PROJECT_CLOSEOUT.md).

The [2026-11-15 clean local-clone replay](evidence/TASK-08/mock_bimanual_20261115/README.md)
at `44febde` passed 75 package results (0 failures, 2 copyright-header skips),
all 8 carrier and 7 bimanual protocol checks, the default carrier-only replay,
and 20/20 additional synthetic carrier cycles. Both launch modes had one joint-
state broadcaster and no residual nodes. Offline results: 42 host tool tests,
7 Humble observer tests, 14 historical analysis tests and 4 CAD tests passed.

| Task | Current state | Evidence and remaining acceptance |
|---|---|---|
| 7 — UR5 controller | PARTIAL | Real JTC/GenericSystem protocol integration passes. Exact UR driver, calibration, safety/disconnect behavior and physical controller feedback remain unverified. |
| 8 — Bimanual/gripper | PARTIAL | Optional four-joint JTC passes motion feedback, rejection, fault, cancellation and recovery tests. Gripper interfaces, object detection and verified grasp/release remain absent. |
| 9 — Reachability | PARTIAL | [Bounded placeholder IK and box diagnostics](../experiments/workspace/FEASIBILITY.md) implemented/tested. Complete robot/tool geometry, actual contact orientations and continuous path clearance remain open. |
| 10 — Complete controller-backed cycles | BLOCKED | Current proxy targets and visual paths do not qualify under the new diagnostics; manipulation feedback and qualified station paths are missing. |
| 11 — Physical operation | BLOCKED | No physical assembly, calibration or supervised hardware trials have been performed. |
| 12 — Workspace | PARTIAL | Prior 20,006 carrier samples plus 2,000 local module samples with limited self-clearance screening. Whole-cell orientation-constrained coverage and boundary uncertainty remain unverified. |
| 13 — Expanded baseline | PARTIAL | Two separate 20-cycle synthetic carrier captures pass; complete tending baseline is blocked by Task 10. Original five visual cycles are unchanged. |
| 14 — Placement | PARTIAL | Five placements tested against placeholder IK/box assumptions. No supported physical placement recommendation or qualified path-cost comparison. |
| 15 — Mechanical design | PARTIAL | Original compact design: 14 valid solids, standalone four-joint URDF/meshes, matching mounting/pedestal holes and elbow fork geometry. Mass allocations and discrete self-clearance checked; selected hardware, fits/retention, dynamic/load qualification, fabrication and physical acceptance remain missing. |

The [new feasibility study](../experiments/workspace/runs/placeholder-feasibility-20261115/README.md)
found zero simultaneous two-endpoint matches to the common proxy target within
1 mm in all five placement candidates, and box-margin violations in 11 of 12
sampled visual workflow segments. Of 2,000 local joint samples, 1,166 passed the
limited nonadjacent-module self-clearance screen. These are numerical/model
diagnostics, not global infeasibility proofs or measured workspace guarantees.
Station orientations and distinct grasp contacts are unspecified; whole-robot,
gripper and continuous collision checks are not included.

The [eleven extracted CAD files](evidence/CAD/extracted_package_20261115/README.md)
were received; hashes all match the earlier package. Native mates/features
remain undecoded. The user subsequently authorized an
[original compact module](../design/compact_module/README.md), without reference
CAD. This separate prototype has 14 valid solids and matching URDF/local meshes.
All 17 CAD/load tests passed, including sampled elbow interference checks.
A separate STEP round-trip confirmed 14 valid solids. A discrete nonadjacent-module study passed 70 of
81 configurations at 5 mm clearance; the 11 failures remain recorded. Its
1.522752 kg parts/actuator/payload allocation leaves 0.477248 kg of a chosen
2 kg budget; total mass and actual carrier compatibility remain unverified.
The original reference-based concept and accepted ROS implementation are
unchanged; no ROS or physical replay is claimed for the new CAD prototype.
The final presentation package and [VS Code execution workflow](VSCODE.md) are
prepared on `feat/sda20-cad-assessment`. [New execution checks](../presentation/execution-verification.md)
pass core builds/tests, analysis regeneration and all 15 optional mock protocol
cases; the existing accepted record remains the GUI demonstration baseline.
The [arm presentation view](ARM_PRESENTATION.md) adds clearer display geometry
without changing the accepted motion or collision model. Its
[separate headless RViz replay](evidence/DELIVERY/arm_view_20261115/README.md) passes
one cycle, one publisher and clean shutdown; 80 package results have no failures
and two existing skips. The [subsequent visual motion repair](evidence/DELIVERY/arm_motion_20261115/README.md)
exchanges the local arm sides with mirrored elbow folding and fixes long-way
carrier turns. Its separate success/failure/cancellation replay passes; hardware
readiness and physical grasp remain unverified. Further engineering is deferred; no hardware readiness is claimed. AY-13's accepted visual scope and all sealed prior records remain
unchanged.

## AY task matrix

| ID | Status | Accepted scope and evidence |
|---|---|---|
| AY-01 | COMPLETE | Source integration; [inventory](evidence/AY-01/manifest.json), [runtime record](progress/AY01_AY09_RUNTIME_FINALIZATION.md) |
| AY-02 | COMPLETE | Packages/build/install; [clean build](evidence/AY-02/clean_build.log), [assets](evidence/AY-02/installed_assets.txt) |
| AY-03 | COMPLETE | Visual launch and gated controller entry; [launch](evidence/AY-03/launch_process.log), [graph](evidence/AY-03/ros_graph.txt) |
| AY-04 | COMPLETE | Five visual stations; [mapping](evidence/AY-04/station_mapping.md), [TF](evidence/AY-04/tf_station_inspection.txt) |
| AY-05 | COMPLETE | One-shot visual FSM; [tests](evidence/AY-05/test_outputs.log), [live events](../experiments/machine_tending/runs/ay10-visual-20261015-03/raw/trials.events.jsonl) |
| AY-06 | COMPLETE | Visual coordination; [component verification](evidence/AY-06-08/verification.log), [probe](../experiments/machine_tending/runs/ay10-visual-20261015-03/raw/probe.log) |
| AY-07 | COMPLETE | Both-arm geometric proxy; [candidate matrix](evidence/AY-06-08/target_candidate_matrix.md), [probe](../experiments/machine_tending/runs/ay10-visual-20261015-03/raw/probe.log) |
| AY-08 | COMPLETE | Integrated visual cycle; [live manifest](../experiments/machine_tending/runs/ay10-visual-20261015-03/raw/manifest.json) |
| AY-09 | COMPLETE | Structured visual logger; [schema](evidence/AY-09/schema.md), [live CSV](../experiments/machine_tending/runs/ay10-visual-20261015-03/raw/trials.csv) |
| AY-10 | COMPLETE | Five actual visual attempts; [acceptance](evidence/AY-10/acceptance.json), [raw manifest](../experiments/machine_tending/runs/ay10-visual-20261015-03/raw/manifest.json) |
| AY-11 | COMPLETE | Event-derived visual metrics; [metrics](../experiments/machine_tending/runs/ay10-visual-20261015-03/raw_analysis/metrics.json), [tests](evidence/AY-10/analysis_tests.log) |
| AY-12 | COMPLETE | Reproducible visual tables/plots; [artifacts](../experiments/machine_tending/runs/ay10-visual-20261015-03/raw_analysis/artifacts.json), [regeneration](evidence/AY-10/regeneration.log) |
| AY-13 | COMPLETE | Documentation and reproducible pinned RViz repair; [independent clean-checkout acceptance](evidence/AY-13/independent_repeat.md), uploaded technical/manual evidence, and reviewer PASS acknowledgement. Visual simulation only. [Guide](ayush/README.md) |

AY-01…09 completion refers to visual ROS scope. The original AY-06–08 capture
was not retained. Later [AY-06–08 runtime records](evidence/AY-06-08/runtime/probe.jsonl)
and the [clean cross-validation recheck](evidence/AY-13/cross_validation/live_recheck/probe.jsonl)
are present; they are separate later runs, not the missing original capture.
AY-09's original one-trial runtime directory remains absent. The later AY-10
raw dataset independently shows the integrated paths and logger; it does not
change older offline logs into runtime proof. The [Phase 4 narrative](progress/phase_4.md)
is retained with an archival caveat because its Gazebo/controller claims lack
supporting files in this checkout.

Historical Phase 1 UR5 and Phase 2 mass experiments have their original
[progress](progress/phase1-carrier-baseline.md) and
[experiment](progress/phase2-mass-sensitivity.md) reports. Phase 3 carrier
workspace characterization and Phase 6 placement analysis are **IN PROGRESS**:
the [preliminary model study](../experiments/workspace/README.md) supplies
20,006 kinematic samples, five assumed placement comparisons and a live TF
cross-check. Collision/orientation checks, workspace boundary validation and
an evidence-backed physical placement recommendation remain open.
Phase 4/5 have visual integration and five measured visual cycles; selected
controllers, validated targets, grasp feedback, and actuated simulation remain
open. The installed carrier-control waypoint YAML is read by the legacy joint
cycle; root config is a mirror. See [decisions](DECISIONS.md) and
[clean-checkout steps](ayush/README.md).
