# Machine-tending experiment records

This directory is intentionally separate from the archived mass-sensitivity
experiments. New machine-tending trial records must validate against
`schema/trial.schema.json` and must never be presented as measured until they
were produced by a ROS runtime with controller results and joint feedback.

`templates/trials.csv` is a header-only data-entry template, not a result.
Visualization-only runs use `visual_simulation` in the `mode` column and cannot
set `runtime_verified` or `end_to_end_verified` to `true`.

Minimum runtime evidence for a successful controller trial is:

1. accepted `FollowJointTrajectory` goals;
2. successful bounded action results;
3. action feedback containing actual joint positions;
4. task-state and workpiece-state transitions; and
5. a terminal `COMPLETE` coordinator state.

