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
or is not marked `controller_validated`. It also requires a complete UR5
`/joint_states` sample in addition to the action server before proceeding.
Current S1–S4 mappings are legacy P1–P4
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
The controller bring-up file must include one authoritative broadcaster for
those six UR5 joints; the coordinator's second publisher owns disjoint joint
names. The launch never starts `dual_arm_cycle` alongside a UR5 controller.

## Visual workcell and targets

`carrier_control/config/machine_tending.json` is the runtime source for five
station IDs, unique TF frames, metres/radians poses, box dimensions and named
station-local interaction targets. Both launch files expand the workcell Xacro
from this installed config with a bounded 30-second Xacro call. Direct manual
Xacro expansion uses checked fallback geometry in the wrapper; launch does not
use those fallback coordinates. The `world` frame is parent of the station
frames and UR5 base. The coordinator transforms target offsets into world
coordinates and includes the resulting *visual* XYZ in task-state messages.
No IK/reachability, collision, grasp, or material-removal claim follows from
this transform.

The workpiece topic adds `process_phase` (`RAW`, `STAGED`, `IN_MACHINE`,
`PROCESSED`, `FINISHED`) and `simulated_attachment`. A `true` attachment is a
declared visual/logical state, not a gripper result. The moving workpiece is a
single three-prismatic-joint visual object; it is not Gazebo physics.

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

