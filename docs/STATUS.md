# CAMBOT — Project Status

**This is the single source of truth for project progress.**
Do not copy status tables into other documents. Link here instead.

Last updated: 2026-08-28 · Corresponds to commit `c0cd8df`

---

## Phase summary

| Phase | Scope | Status |
|---|---|---|
| 1 | UR5 carrier baseline | ✅ Complete |
| 2 | Mass sensitivity study | ✅ Complete |
| 3 | Carrier workspace characterization | ⏸ Planned |
| 4 | Carrier flange + bimanual placeholder | 🔧 In progress |
| 5 | Quantitative baseline logging & metrics | ⏸ Planned |
| 6 | Carrier placement analysis | ⏸ Planned |

> **Phase ordering note.** The original plan in `Task2_aim.md` put quantitative
> baseline logging at Phase 2 and mass sensitivity was unplanned. In practice
> the mass study was done first and logging was deferred. The numbering above
> reflects what actually happened. Phase 5 (logging) is still outstanding and
> should not be forgotten — it is what makes every later claim measurable.

---

## Phase 1 — UR5 carrier baseline ✅

| Item | Status | Evidence |
|---|---|---|
| UR5 model in Gazebo | ✅ | `src/carrier_description/urdf/` |
| MoveIt 2 planning (`ur_manipulator`, `base_link → tool0`) | ✅ | `/move_action`, `/move_group` verified |
| `ros2_control` trajectory execution | ✅ | `joint_trajectory_controller` active |
| `joint_state_broadcaster` | ✅ | all 6 joints publishing |
| RViz interactive control | ✅ | |
| Custom test tool attached at `tool0` | ✅ | `urdf/test_tool.xacro` |
| Waypoints P1–P4 taught | ✅ | `config/waypoints.yaml` |
| Automated machine-shop cycle | ✅ | `machine_shop_joint_cycle.py` |
| 3D trajectory plotting | ⚠️ Partial | recorder works; plot generation not confirmed end-to-end |

Details: [`progress/phase1-carrier-baseline.md`](progress/phase1-carrier-baseline.md)

---

## Phase 2 — Mass sensitivity ✅

| Experiment | Link | Δ mass | Status |
|---|---|---|---|
| EXP01 | Upper arm | 8.3930 → 9.2323 kg | ✅ Complete, archived |
| EXP02 | Forearm | 2.3300 → 2.5630 kg | ✅ Complete, archived |
| EXP03 | Shoulder | 3.7000 → 4.0700 kg | ✅ Complete, archived |
| EXP04 | — | — | ❌ Deliberately not run |

Details: [`progress/phase2-mass-sensitivity.md`](progress/phase2-mass-sensitivity.md)
Rationale for skipping EXP04: [`DECISIONS.md`](DECISIONS.md) §D-03

---

## Phase 4 — Carrier flange & dual-arm placeholder 🔧

| Item | Reported | In repository |
|---|---|---|
| `carrier_flange` link + `tool0_to_carrier_flange` joint | ✅ Working | ❌ Not committed |
| `carrier_flange_interface` link | ✅ Working | ❌ Not committed |
| `dual_arm_base_link` + 4 joints | ✅ Working | ❌ Not committed |
| `check_urdf` passes on full chain | ✅ Verified | ❌ Not committed |
| `joint_state_publisher_gui` control of 4 joints | ✅ Working | ❌ Not committed |
| RViz visualization | ✅ Working | ❌ Not committed |
| `dual_arm_cycle.py` with cubic interpolation @ 50 Hz | ✅ Working | ❌ Not committed |
| Pick / grasp / transport / place / release sequence | ✅ Working | ❌ Not committed |
| Single reliable `dual_arm_demo.launch.py` | 🔧 Blocked | ❌ Not committed |

> ⚠️ **The single most important outstanding action on this project is
> committing the Phase 4 files.** All of the above is currently documented in
> prose only. If the working machine is lost, the work is lost.

Details: [`progress/phase4-carrier-flange.md`](progress/phase4-carrier-flange.md)

---

## Outstanding technical debt

Tracked from the audit. Roughly ordered by cost of leaving it.

| # | Item | Severity |
|---|---|---|
| 1 | Phase 4 flange / dual-arm source not committed | 🔴 Critical |
| 2 | No launch files — repo is not runnable as cloned | 🔴 Critical |
| 3 | `dual_arm_demo.launch.py` robot_description integration broken | 🟠 High |
| 4 | `waypoints.yaml` not installed to `share/`, not read by any node | 🟠 High |
| 5 | No `.gitignore`; 114 MB repo with 53 MB of un-LFS'd CSV | 🟠 High |
| 6 | Filenames containing `:` — unclonable on Windows | 🟠 High |
| 7 | `package.xml` still says `TODO: Package description` | 🟡 Medium |
| 8 | `setup.py` globs `launch/`, `config/`, `meshes/` that don't exist | 🟡 Medium |
| 9 | `exp03` missing `physical_parameters_baseline.yaml` | 🟡 Medium |
| 10 | Duplicate `rclpy` and unused `moveit_msgs`/`shape_msgs` deps | 🟢 Low |
| 11 | Branch strategy in `TASK_ALLOCATION.md` not actually in use | 🟢 Low |

---

## Next actions

1. **Commit the Phase 4 source.** `carrier_flange.xacro`, the dual-arm Xacro,
   `dual_arm_cycle.py`, all launch files, and the RViz config. Nothing else on
   this list matters as much.
2. **Fix `dual_arm_demo.launch.py`** so a single command brings up
   `robot_description` → `robot_state_publisher` → `dual_arm_cycle` → RViz.
3. **Make `waypoints.yaml` authoritative.** Move it inside
   `carrier_description`, install it via `setup.py`, and have
   `machine_shop_joint_cycle.py` load it instead of hardcoding values.
4. **Add `.gitignore` and Git LFS**, then rewrite history if the repo size
   becomes a real problem.
5. **Phase 5 logging.** Instrument the cycle to emit
   `trial, from, to, planning_time, execution_time, result` to
   `results/baseline_trials.csv`, then run 10–20 cycles. Without this, "the
   carrier works" is an anecdote rather than a measurement.
