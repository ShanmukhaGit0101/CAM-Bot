# AY-01…AY-13 traceability

The authoritative mapping is the Ayush individual task document. This table reflects the repository state after the Humble visual-runtime bring-up and the AY-06…AY-09 acceptance runs completed on 2026-10-15.

| ID | Task | Current disposition |
|---|---|---|
| AY-01 | Obtain and integrate Phase 4 source | COMPLETE for source integration; Humble visual runtime reproduced. |
| AY-02 | Repository / GitHub integration | COMPLETE for package/build integration used by the Humble workspace. |
| AY-03 | Single-command launch | COMPLETE for visual launch; RViz, TF and one authoritative `/joint_states` publisher observed. |
| AY-04 | Five-station workcell integration | COMPLETE for the configurable visual workcell; station geometry remains a simulation assumption, not a surveyed real cell. |
| AY-05 | Machine-tending state machine | COMPLETE for visual runtime; full HOME → PICK_RAW → STAGE → LOAD_MACHINE → MACHINE_DWELL → UNLOAD_MACHINE → PLACE_FINISHED → HOME cycle demonstrated. |
| AY-06 | Carrier ↔ dual-arm coordination | COMPLETE for visual runtime; both `CARRIER_REPOSITION` and `LOCAL_MANIPULATION` branches observed. |
| AY-07 | Workspace / reachability decision logic | COMPLETE for the documented geometric proxy; both-arm reachability rechecks observed live. This is not IK or collision checking. |
| AY-08 | Integrate coordination with simulation | COMPLETE for visual ROS integration; five post-carrier TF rechecks passed and the workpiece finished at S5. |
| AY-09 | Experiment logger | COMPLETE for visual runtime; structured CSV/JSONL capture validated with `validation: PASS`. |
| AY-10 | Run at least five trials | NOT YET COMPLETE — next experimental phase. |
| AY-11 | Calculate performance metrics | NOT YET COMPLETE — depends on the AY-10 qualifying dataset. |
| AY-12 | Result plots and tables | NOT YET COMPLETE — depends on AY-11 metrics. |
| AY-13 | Technical documentation | IN PROGRESS — implementation/runtime traceability through AY-09 is now documented; AY-10…AY-12 results remain pending. |

## Runtime acceptance snapshot

The successful AY-06…AY-08 visual probe reported:

- `probe_result = VISUAL_SIMULATION_PASS`
- state sequence `HOME, PICK_RAW, STAGE, LOAD_MACHINE, MACHINE_DWELL, UNLOAD_MACHINE, PLACE_FINISHED, HOME`
- decisions containing both `CARRIER_REPOSITION` and `LOCAL_MANIPULATION`
- five successful post-carrier reachability rechecks
- final workpiece state `FINISHED_AT_S5`
- `actuation_verified = false`
- `grasp_verified = false`

The successful AY-09 logger capture reported one complete visual trial, 44 structured events, final state `FINISHED_AT_S5`, and dataset validation `PASS`. Its summary intentionally records `runtime_verified = false` and `end_to_end_verified = false`, because the run does not prove physical/controller-backed carrier actuation or grasp feedback.

## Finalized runtime repairs

The Humble bring-up required the following compatibility/runtime repairs, now part of the source tree:

- remove the unsupported Humble `ur_robot` `force_abs_paths` Xacro argument;
- make visual `JointState.position` construction robust to ROS `array.array` conversion;
- calibrate **visual-only** carrier station poses S1…S5 against the current five-station geometry and both-arm proxy;
- keep controller validation flags false for those visual-only poses;
- republish the exact final visual carrier joint state before TF-based reachability rechecks;
- use a two-stage TF handshake so an intermediate carrier transform is not mistaken for the final station pose;
- make AY-06…AY-09 capture scripts safe when generated ROS setup scripts are sourced under Bash `nounset`.

These repairs do **not** convert the project into a controller-verified, collision-checked, IK-planned or grasp-verified system.
