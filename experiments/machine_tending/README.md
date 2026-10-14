# Machine-tending experiment records

This directory is intentionally separate from the archived mass-sensitivity
experiments. New machine-tending CSV summaries and JSONL events use schema
version 2.0 and must validate against `schema/trial.schema.json` and
`schema/event.schema.json`. They must never be presented as measured until
produced by a ROS runtime with controller results and joint feedback.

`templates/trials.csv` is a header-only template, not a result. For a summary
path such as `trials.csv`, events are durably appended to
`trials.events.jsonl`. Every append flushes and calls `fsync`. The start event
is immediately marked `INCOMPLETE_PENDING`, so an interrupted process leaves
a detectable record before the final CSV summary. Normal exception/interrupt
handling finalizes the row with `status=INCOMPLETE`.

`cycle_time_s` is elapsed steady-clock (`time.monotonic`) duration. UTC wall
timestamps are recorded for correlation, not duration calculation. The
configuration hash is SHA-256 of canonical sorted JSON. Trial IDs include a
UUID and are rejected if already present in either output.
Visualization-only runs use `visual_simulation` in the `mode` column and cannot
set `runtime_verified` or `end_to_end_verified` to `true`.

Minimum runtime evidence for a successful controller trial is:

1. accepted `FollowJointTrajectory` goals;
2. successful bounded action results;
3. action feedback containing actual joint positions;
4. task-state and workpiece-state transitions; and
5. a terminal `COMPLETE` coordinator state.

