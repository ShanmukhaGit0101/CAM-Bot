# CAM-Bot — Repository Audit

Audit of `ShanmukhaGit0101/CAM-Bot` @ `c0cd8df` (main, 22 commits).

---

## 1. Documentation problems

### 1.1 Three byte-identical files

These are the same file, md5 `f73935f5...`:

```text
Task2/README.md
UR5_Machine_Shop/docs/Task3_Summary.md
UR5_Machine_Shop/docs/summary/Task3_Sumarry.md      <- typo: "Sumarry"
```

Its content is the **Phase 4 flange / dual-arm** status. It is not a README for
`Task2/`, and `Task2/` (mass sensitivity) is not what it describes. A reader
opening `Task2/README.md` gets documentation for entirely different work.

### 1.2 The word "Task 2" means three different things

| Location | Actually contains |
|---|---|
| `Task2/` | Mass sensitivity experiments EXP01–03 |
| `docs/Task2_aim.md` | The 6-phase carrier work plan (whole project roadmap) |
| `docs/Task2_Summary.md` | Mass sensitivity results summary |
| `docs/Task3_Summary.md` | Phase 4 flange / dual-arm status |

Task numbers and phase numbers are used interchangeably and do not line up.

### 1.3 Docs are raw chat transcripts

Files open with lines addressed to an AI assistant rather than to a reader:

- `Task2_Summary.md` line 1: *"Absolutely. Here is a self-contained handoff summary you can paste into a new chat…"*
- `Task3_Summary.md` line 1: *"Here's the current Phase 4 – Flange / Dual-Arm status, structured so we can continue directly from here."*
- `Task2_Summary.md` §19: *"Since you said we may go directly to Phase 4, the next chat should begin with…"*
- `Task2_Summary.md` ends with a "STARTING POINT FOR THE NEXT CHAT" prompt block.
- `task1_chat .md` — the filename itself says "chat", and has a space before `.md`.

This is fine as a personal working note. It is not fine as the documentation a
reviewer, teammate, or examiner reads.

### 1.4 `Task1_Progress.md` is truncated

The file ends mid-code-block:

```text
## 8. Experimentally Taught Positions

### HOME

```text
[ 0.000000, -1.570700, 0.000000, 0.000000, 0.000000, 0.000000 ]
```

The fence is never closed and **P1–P4 are missing**. Those values exist in
`task1_chat .md` §15–18 and in `config/waypoints.yaml`, so nothing is lost —
but the file as committed is broken.

### 1.5 Status tables contradict each other

`Task2_Summary.md` says Carrier flange is **➡️ NEXT** (not started).
`Task3_Summary.md` says Custom `carrier_flange` is **✅ Working**.

Both are committed on `main`. There is no single source of truth for status.

### 1.6 Root README advertises a structure that does not exist

The README shows this tree:

```text
docs/  simulation/  src/  hardware/  scripts/  data/  results/  tests/
```

**None of these directories exist at the repository root.** The actual root is
`Task2/`, `UR5_Machine_Shop/`, plus four loose files.

### 1.7 License contradiction

`LICENSE` is Apache-2.0 and GitHub labels the repo Apache-2.0. The README says
*"Licensing and publication details will be finalized as the project progresses."*

---

## 2. Code / reproducibility problems

### 2.1 Documented files that are not in the repository

`Task3_Summary.md` describes these as working:

```text
carrier_description/urdf/carrier_flange.xacro          MISSING
carrier_description/launch/view_dual_arm.launch.py     MISSING
carrier_description/launch/dual_arm_demo.launch.py     MISSING
carrier_description/launch/view_carrier.launch.py      MISSING
carrier_description/rviz/dual_arm.rviz                 MISSING
carrier_control/carrier_control/dual_arm_cycle.py      MISSING
```

`UR5_Machine_Shop/README.md` points readers to `docs/progress.md` — also missing
(it was renamed to `Task1_Progress.md` in commit `1be3317` and the link was
never updated).

The entire Phase 4 dual-arm work exists only as prose. **It has never been
committed.** Anyone cloning this repo cannot reproduce it.

### 2.2 No launch files at all

`carrier_description/` contains only `urdf/`. There is no `launch/`, `config/`,
`meshes/`, or `rviz/` directory anywhere in either package. The README's
"Running" section says to "start the UR5 Gazebo simulation and MoveIt/RViz
configuration" without saying how — because no launch file is provided.

### 2.3 `setup.py` globs directories that do not exist

`carrier_description/setup.py` installs `launch/*`, `config/*`, `meshes/*`.
All three globs resolve to empty. Harmless today, silently wrong the moment
someone adds a launch file at the wrong path.

### 2.4 Package metadata is scaffolding

`carrier_control/package.xml`:

```xml
<description>TODO: Package description</description>
<maintainer email="shanmukha@todo.todo">shanmukha</maintainer>
```

Also: `rclpy` is declared twice as `exec_depend`, and `moveit_msgs` /
`shape_msgs` are declared but unused by the three committed nodes.

### 2.5 `config/waypoints.yaml` is decorative

The file exists at `UR5_Machine_Shop/config/waypoints.yaml`, but it is outside
both ROS packages, so it is never installed to `share/`. No node reads it —
`machine_shop_joint_cycle.py` hardcodes its own values. `task1_chat .md` §38
already flags this: *"Make waypoints.yaml the authoritative waypoint file."*
Not yet done.

---

## 3. Repository hygiene

### 3.1 No `.gitignore`

`task1_chat .md` §29 specifies exactly what one should contain
(`__pycache__/`, `*.pyc`, `build/`, `install/`, `log/`). It was never created.

### 3.2 114 MB repo, 37 MB of git history, for a project with ~1500 lines of code

| Category | Size |
|---|---|
| Experiment CSVs (6 files) | ~53 MB |
| Screencasts (3 `.webm`) | ~14 MB |
| PDFs + docx | ~2 MB |
| Actual source code | < 200 KB |

The CSVs are raw `/joint_states` dumps at 100 Hz for ~460 s each. They are
committed as plain blobs — no Git LFS, no compression, no `.gitattributes`.
Every clone downloads all of it forever, including superseded versions.

### 3.3 Filenames with spaces and colons

```text
Task2/Screencast from 08-28-2026 02:16:43 AM.webm
Task2/Screencast from 08-28-2026 12:07:58 AM.webm
UR5_Machine_Shop/Screencast from 08-24-2026 10:10:25 PM.webm
UR5_Machine_Shop/docs/summary/task1_chat .md
```

Colons are illegal in filenames on Windows — these files **cannot be checked
out** on a Windows machine. The `.md` has a stray space before the extension.

### 3.4 Inconsistent experiment layout

| | exp01 | exp02 | exp03 |
|---|---|---|---|
| `physical_parameters_baseline.yaml` | ✅ | ✅ | ❌ missing |
| baseline metadata location | `results/` | package root | `results/` |
| number of URDFs | 3 | 3 | 1 |
| `summary.txt` | ❌ | ✅ | ❌ |

Three experiments, three different folder conventions.

### 3.5 Git history is largely web-UI uploads

Seven of 22 commits are `Add files via upload` or `Create <file>.md`, and four
are renames of documents that were then re-uploaded. The branch strategy
documented in `TASKS_ALLOC.md` §5 (`development`, `feature/kinematics`, …) does
not exist — `main` is the only branch, and there are no PRs.

---

## 4. What is genuinely good

Worth keeping explicitly, because the restructure should not lose it:

- **The core engineering narrative is strong.** Cartesian waypoints failed →
  diagnosed as unreachable/ill-conditioned IK targets → switched to interactive
  RViz teaching + `/joint_states` capture → cycle executes reliably. That is a
  real problem→diagnosis→redesign→result story, and it is written up well in
  `task1_chat .md` §37.
- **The mass sensitivity study is properly caveated.** `Task2_Summary.md` §3
  states plainly that baseline and experiment runs have different sample counts
  and durations, so results are trajectory *statistics*, not synchronized
  trajectory error — and explicitly warns against reading them as torque or
  actuator measurements. That honesty is unusual and valuable.
- **The scope discipline is correct.** Deferring the real bimanual arm design
  until carrier, flange, workspace, and placement are settled (CA → CF → BM) is
  the right call, and the decision not to run EXP04 is justified rather than
  drifted into.
- **The hardcoded `/home/shanmukha/` path was actually fixed.** Flagged in
  `task1_chat .md` §28, and `plot_machine_shop_path.py` now writes a relative
  filename. Verified — no absolute home paths remain in any `.py`, `.yaml`, or
  `.xacro`.
