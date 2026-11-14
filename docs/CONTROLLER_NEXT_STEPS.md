# Controller and manipulation milestones after AY-13

This dependency record supplements [STATUS.md](STATUS.md), the authoritative
status matrix. AY-13's visual acceptance does not close controller or hardware
milestones. No runtime verification flag is promoted by this plan.

| Task | Available work | Remaining acceptance/input |
|---|---|---|
| 7: UR5 controller | Real ros2_control trajectory controller tested with GenericSystem; production motion methods exercised. | Exact UR model/controller interface, calibration, selected robot driver, safety-state/disconnect handling and supervised hardware feedback validation. |
| 8: bimanual/gripper feedback | Placeholder joint poses and fail-closed manipulation boundary. | Actual actuator joint names, limits, driver/action interfaces; measured open/closed/position/effort feedback; workpiece detection; grasp/release acceptance; bounded timeout/cancel and fault recovery tests. |
| 9: reachability | Both-arm geometric proxy and UR5 FK sampling. | Actual module/tool geometry, joint limits and tool orientations, IK solutions, self/environment collision model and continuous path clearance assessment. |
| 10: tending cycles | Visual cycle and isolated carrier controller protocol test. | Tasks 6/8/9, task-specific carrier goals and manipulation outcomes. Each state transition must depend on actual controller/manipulation results; a mock attachment cannot establish physical grasp. |
| 11: physical operation | Survey intake and explicit unsupported gates. | Mechanical assembly, calibration, robot-specific integration, supervised execution and measured trial evidence. Cannot be completed in this cloud workspace. |
| 12: workspace | 20,006 model samples and live FK/TF agreement. | Collision filtering and orientation-constrained tool coverage with measured/CAD assembly, convergence and boundary uncertainty. |
| 13: baseline | Five sealed visual trials plus separately scoped synthetic carrier benchmark. | 10–20 complete tending cycles once task 10 passes; distinguish planning from execution durations, preserve attempted failures and scenario/config hashes. |
| 14: placement | Five assumed placements compared. | Feasible collision/orientation coverage, uncertainty and executable path costs using task 9/12 inputs. Keep recommendations preliminary until supported. |
| 15: mechanical design | Flange and four-joint placeholder only. | Payload/workpiece envelope, required reach and accuracy, cycle duty, mass budget, mounting envelope, actuator choices and power/interface constraints; dimensioned CAD, load/deflection calculations, fabrication and physical validation. |

## Input handoff

Use [WORKCELL_SURVEY.md](WORKCELL_SURVEY.md) for dimensions and station targets.
For actuator integration, supply each device's make/model, control mode, ROS
package/version or protocol, action/service/topic types, joint names and units,
feedback rate, limits, cancellation/stop semantics and fault/disconnect behavior.
Record whether grasp detection comes from a sensor, motor current/effort, or a
model assumption. A successful motion action alone is insufficient grasp proof.

For the mechanical design, specify workpiece dimensions/mass and variation,
required grip surfaces, desired manipulation workspace, tolerances, station
access envelopes, allowable module mass/centre of gravity and mounting loads.
Without these inputs there is no supported detailed mechanism or load rating.

## Synthetic carrier benchmark

`tools/benchmark_mock_controller.py` measures 20 synthetic outbound/return
carrier cycles through the production motion method on the isolated mock JTC.
Each cycle checks both successful terminal action statuses, actual-position
feedback and final return position. A failed attempt is flushed to CSV and
stops the benchmark. The summary includes attempted/success/failed counts,
mean, sample standard deviation, minimum and maximum successful cycle durations.
Planning duration remains null because there is no planner.

Run using the Task-7 container and its scoped build from
[TASK7_CONTROLLER.md](TASK7_CONTROLLER.md), changing the runner invocation to:

```bash
CAMBOT_RUN_BENCHMARK=1 bash tools/run_ur5_mock_controller.sh /evidence/NEW_REPLAY
```

This adds the benchmark while the runner owns the controller launch, then checks
shutdown and the residual graph. Use a new output directory and unused domain.
The timing includes outbound and return action requests/results plus a final
observation interval. These synthetic cycles are not pooled with AY-10 trials
and do not complete task 13's full tending baseline.
