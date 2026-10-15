# CAMBOT — Project Status

**This is the single source of truth for project progress.**
Do not copy status tables into other documents. Link here instead.

Last updated: 2026-10-15 · See `artifacts/inventory.json` for the implementation base

---

## Phase summary

| Phase | Scope | Status |
|---|---|---|
| 1 | UR5 carrier baseline | ✅ Complete |
| 2 | Mass sensitivity study | ✅ Complete |
| 3 | Carrier workspace characterization | ⏸ Planned |
| 4 | Carrier flange + bimanual placeholder | ✅ Source present; runtime recheck blocked |
| 5 | Machine-tending logging & metrics | 🔧 Schema/recorder built; measured trials pending |
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

## Phase 4 — Carrier flange & dual-arm placeholder

| Item | Current evidence |
|---|---|
| `tool0` → flange → interface → four-joint module source | STATIC VALID offline |
| Five visual stations + movable visual workpiece source | STATIC VALID offline |
| Named machine-tending workflow and state validation | STATIC VALID offline |
| Bounded carrier action/result/feedback gates | STATIC VALID offline |
| One-command visual launch | FOUND and Python syntax valid; ROS runtime blocked here |
| Controller-mode named workflow | BLOCKED: unvalidated S1–S4 mappings and missing S5 target |
| End-to-end grasp/placement | BLOCKED: no bimanual/gripper controller feedback interface |

Details: [`progress/phase4-carrier-flange.md`](progress/phase4-carrier-flange.md)

---

## Outstanding technical debt

Tracked from the audit. Roughly ordered by cost of leaving it.

| # | Item | Severity |
|---|---|---|
| 1 | Teach/validate named carrier targets, including S5 | 🔴 Critical |
| 2 | Run ROS Humble build, Xacro/check_urdf, launch, TF, and controller tests | 🔴 Critical |
| 3 | Select bimanual/gripper controller interface for end-to-end feedback | 🟠 High |
| 4 | Legacy `waypoints.yaml` remains duplicated in old controller | 🟠 High |
| 5 | Historical filenames containing `:` are not Windows-compatible | 🟠 High |
| 6 | `exp03` archive lacks `physical_parameters_baseline.yaml` | 🟡 Medium |
| 7 | Unused legacy MoveIt dependencies remain for the optional Cartesian node | 🟢 Low |

---

## Next actions

1. Teach and validate all named carrier targets against the actual cell geometry.
2. Run the ROS-only checks in `docs/VALIDATION.md` on ROS 2 Humble.
3. Select a bimanual/gripper controller feedback interface if end-to-end proof is required.
4. Run five controller trials and retain the generated CSV without editing it.
