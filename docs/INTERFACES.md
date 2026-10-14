# CAM-BOT runtime interfaces

These interfaces support a bounded simulation/prototype workflow. They do not
define force control, a production gripper, or a physical CNC interface.

## Carrier action

| Property | Contract |
|---|---|
| Action type | `control_msgs/action/FollowJointTrajectory` |
| Default name | `/joint_trajectory_controller/follow_joint_trajectory` |
| Commanded joints | six UR5 joints in `machine_tending.json` order |
| Success gate | accepted goal + successful result + actual-position action feedback |
| Time bounds | server 10 s; response 5 s; result = requested duration + 5 s; cancellation 2 s |
| Retry policy | zero automatic retries |

Controller mode is rejected before connecting when any named target is missing
or is not marked `controller_validated`. Current S1–S4 mappings are legacy P1–P4
assumptions, and S5 has no taught target, so controller mode is intentionally
blocked until targets are taught against the displayed cell geometry.

## State topics

All state payloads are compact JSON strings in `std_msgs/msg/String`.

| Topic | Publisher | Meaning |
|---|---|---|
| `/cambot/coordinator_state` | coordinator | `READY`, `RUNNING`, `COMPLETE`, or `FAILED`, with mode/trial |
| `/cambot/task_state` | coordinator | step-level `STARTED`/`COMPLETED`; `CARRIER_NOT_COMMANDED` in visual mode |
| `/cambot/workpiece_state` | coordinator | logical workpiece state and visual world position |
| `/joint_states` | controller/broadcaster plus coordinator | carrier feedback plus partial placeholder/workpiece joint updates |

The coordinator publishes UR5 joint values only in `visual_simulation` mode.
Those values animate RViz and are not commands, controller results, or Gazebo
actuation. In `controller` mode it publishes only the four placeholder arm and
three visual workpiece joints, leaving UR5 joint feedback to the controller.

## Parameters

| Parameter | Default | Constraint |
|---|---:|---|
| `mode` | `visual_simulation` | `visual_simulation` or `controller` |
| `config_file` | installed `machine_tending.json` | valid schema and continuous state sequence |
| `results_file` | `~/.ros/cambot/machine_tending_trials.csv` | append-only CSV |
| `trial_count` | 1 | 1–25 |
| `visual_time_scale` | 1.0 | 0.01–10.0 |

## Inputs still required for controller validation

- actual five station poses relative to the UR5 base;
- a taught and collision-checked six-joint target for every station, including S5;
- the selected controller name and confirmation that its action feedback contains actual positions;
- the selected bimanual/gripper controller interface if end-to-end verification is desired; and
- Tanmay's final flange/module dimensions if the reconstruction values are to be replaced.

