# CAM-BOT — final project report

**Carrier-assisted Adaptive Manipulation with Bimanual Operational Technology**  
TOPS Programme 2026 · Final scope: visual ROS 2 Humble demonstrator

## Abstract

CAM-BOT explores a hierarchical approach to CNC machine tending: a UR5 carrier
moves a smaller flange-mounted bimanual module between stations, while local
arms represent manipulation at each station. The project implements this idea
as an integrated ROS 2 visual simulation with a five-station workcell, task
state machine, carrier/local-motion coordination, visual workpiece tracking and
structured experiment logging. Five attempts in a fixed visual scenario all
completed; event-derived cycle time averaged 19.579117 seconds, with five
completed carrier repositions per trial. The implementation was reproduced in
ROS 2 Humble and independently reviewed in its visual scope. Supplementary work
includes mass-sensitivity records, kinematic workspace studies, mock-controller
protocol checks and preliminary mechanical concepts. The final project delivers
a reproducible demonstrator and an auditable engineering record. Physical
operation and a comparative efficiency advantage are not established.

## Objective and architecture

The primary objective is to demonstrate how global positioning and local
manipulation can be coordinated within one machine-tending workflow. The
architecture preserves the official UR5 chain and attaches the carrier flange
and local module after `tool0`. A configurable workcell provides raw input,
staging, machine, output and finished-part stations.

The coordinator uses live transforms and a both-arm geometric reachability
proxy. It chooses local manipulation or carrier repositioning, waits for final
visual pose feedback through TF, and rechecks the target. The FSM handles
HOME, PICK_RAW, STAGE, LOAD_MACHINE, MACHINE_DWELL, UNLOAD_MACHINE,
PLACE_FINISHED and return HOME. Start/cancel/reset services, structured events
and fresh output paths make demonstrations and analysis repeatable.

The live demonstration publishes visual joint states; it does not command a
physical robot or validate object grasp. One authoritative joint-state publisher
avoids competing state sources. Failed-target classification and shutdown fixes
are retained with regression and runtime evidence.

## Implementation and studies

The core packages are `carrier_description` and `carrier_control`. They provide
the URDF/Xacro model, workcell, RViz launch, coordination, FSM and logger.
The sealed AY-10 capture supports the later analysis and charts. AY-13 records
reproducibility repairs, a pinned RViz patch and an independent human replay.

Additional engineering work is presented as supporting investigation:

- Historical mass-sensitivity studies perturbed three UR5 link masses by 10%.
  Their recordings were not time-aligned, so derived acceleration changes are
  trajectory statistics, not verified dynamic sensitivity or force measurements.
- A 20,006-sample carrier study and five assumed placements explored kinematics;
  that study did not establish collision-free task coverage or optimal placement.
- Real ros2_control trajectory controllers backed by GenericSystem passed eight
  carrier and seven bimanual protocol checks. Separate synthetic carrier
  benchmarks completed 20/20 cycles; these are not full tending cycles.
- Original compact-module CAD supplies fourteen valid solids, a provisional
  four-joint mesh/kinematic model and sampled clearance/mass-budget studies.
  It is a design concept, not a manufactured or load-qualified mechanism.

## Results and measurement boundary

| Metric | Fixed visual scenario |
|---|---:|
| Attempted trials | 5 |
| Successful visual trials | 5 |
| Mean measured cycle time | 19.579117 s |
| Sample standard deviation | 0.016634 s |
| Minimum / maximum | 19.551515 / 19.592351 s |
| Completed visual carrier repositions | 25 total; 5 per trial |
| Final workpiece state | FINISHED_AT_S5 |

These durations are derived from `S1_APPROACH STEP_STARTED` through
`HOME_END STEP_COMPLETED`. Initial HOME/setup is excluded. The raw trial CSV's
broader elapsed duration is therefore not the reported event-derived cycle
metric. Do not average its `cycle_time_s` column and substitute that value for
the published analysis. Preliminary captures are retained separately.

The results demonstrate repeatability in one visual scenario. There is no
controlled conventional-versus-carrier-assisted baseline, so the project does
not quantify throughput, energy, physical accuracy or industrial reliability.
Raw files, configuration/source hashes and analysis artifacts make the claims
inspectable without replacing historical results.

## Contributions and final delivery

The documented team workstreams are Shannu/Shanmukha (kinematics/control and
architecture), Tanmay (mechanical/carrier concepts) and Ayush Ranjan
(software, simulation and integration). The contribution record distinguishes
these roles from artifact authorship and identifies AI-assisted development.
See [CONTRIBUTIONS.md](CONTRIBUTIONS.md) for the evidence portfolio.

The final delivery includes the accepted visual implementation, editable
PowerPoint and offline HTML presentation, static PDF, speaker notes, a live-demo
wrapper, archived-event replay, this report and the retained experiment/code
history. The current project is closed at this visual-demonstrator scope.
Tasks 7–15 remain future extensions where incomplete; they are not silently
marked technically complete and no longer block this presentation delivery.

## Evidence index

- Current status and scoped closure: `docs/STATUS.md`, `docs/PROJECT_CLOSEOUT.md`.
- Independent visual review: `docs/evidence/AY-13/independent_repeat.md`.
- Visual methods/results: `experiments/machine_tending/README.md` and
  `runs/ay10-visual-20261015-03/raw_analysis/metrics.json` beneath it.
- Controller extension: `docs/evidence/TASK-08/mock_bimanual_20261115/README.md`.
- Workspace study: `experiments/workspace/README.md`.
- Original design: `design/compact_module/README.md`.

Reviewers can follow these paths from the repository root. The presentation
is a communication layer over this evidence; its offline replay is not a new
runtime experiment or a new independent acceptance run.
