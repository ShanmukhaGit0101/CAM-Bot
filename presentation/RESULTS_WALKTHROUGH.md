# Present a completed CAM-BOT run

Lead with the robot demonstration, then show three plots and one result table.
The remaining files are supporting evidence for questions and reproducibility.
You do not need to display every JSON or log file during the talk.

## Your uploaded rehearsal: 15 November 2026

The uploaded `cambot-runs.zip` contains:

- Raw run: `.cambot-runs/run.WLd4dE/`.
- Observer messages: `.cambot-runs/observers.1maWqs/`.
- Analysis: `.cambot-runs/analysis.8OMKnc/analysis/`.
- Tested checkout: `e93ef2a0a85a8b7e527cb11b9bd0a528a5c59848`.
- One attempted visual cycle, one success, no attempted failure.
- Final workpiece: `FINISHED_AT_S5`; FSM returned to HOME.
- Five requested, five accepted and five completed visual carrier repositions.
- Event-derived cycle: **20.424234116 seconds**.
- Broader logger duration: **22.761415109 seconds**.

The analysis input hashes match the uploaded raw CSV/events. The two recorded
working-tree reports are empty. This verifies the provided output's consistency;
it is not another live run or proof of physical actuation. The archive was made
before shutdown: its launch log records startup, without clean-exit messages.

## Suggested six-minute demonstration

| Order | Show | Explain |
|---|---|---|
| 1 — 45 s | Presentation architecture/workcell slide | The UR5 handles station-to-station positioning; the small arms illustrate local manipulation. Identify S1–S5. |
| 2 — 60 s | RViz, Observe terminal, then Start task | Follow raw pick → staging → machine → output → finished placement → HOME. State that this is visual ROS simulation. |
| 3 — 30 s | `trial_outcomes.png` | This particular rehearsal attempted one cycle and completed it successfully. One observation does not establish statistical reliability. |
| 4 — 45 s | `cycle_time_by_trial.png` | The defined task cycle took about 20.424 s, from first S1 approach through final HOME completion, excluding initial HOME preparation. |
| 5 — 45 s | `carrier_repositions_by_trial.png` | Five visual reposition requests were accepted and completed. HOME return is counted separately. These are visual publications, not hardware action confirmations. |
| 6 — 30 s | `summary.csv`, optionally analyzed `trials.csv` | Connect the three plots to one machine-readable result; show COMPLETE, success=True, five repositions and cycle time. |
| 7 — 45 s | Contribution slide, optionally a code breakpoint | Explain each team's documented workstream and your integration, FSM, logging, tests and analysis. |
| 8 — 20 s | Conclusion slide | Delivered an integrated, reproducible visual demonstrator with recorded results. Mention physical grasp/controller validation as future work. |

For your current paths, open the PNG files under:

`/home/ayush/TOPS/CAM-BOT/.cambot-runs/analysis.8OMKnc/analysis/`

Use VS Code File → Open File or an ordinary image viewer, and zoom the plot so
its labels are readable. The one-trial bar is expected; do not duplicate it to
make the chart look fuller. Keep the presentation and plots open before starting
RViz so switching windows is quick.

## Short narration you can use

> CAM-BOT separates global positioning from local manipulation. The UR5 carries
> the mounted two-arm module through five tending stations, while our state
> machine coordinates the sequence and records state changes and movement
> decisions. Here we start one visual cycle and observe the finished part at S5
> followed by the return HOME. The analysis of this rehearsal shows one successful
> attempt, five completed visual carrier repositions and a task duration of
> approximately 20.424 seconds. These are simulation observations; verified
> physical gripping and industrial throughput improvement are future work.

For coordination, show a `CARRIER_REPOSITION` message followed by
`LOCAL_MANIPULATION` after the geometric-proxy recheck. Describe this as the
implemented decision rule, rather than a validated IK/collision planner.

## What the files are for

| File or folder | Purpose | Show live? |
|---|---|---|
| Three PNG plots | Readable result figures | Yes |
| `analysis/summary.csv` | Aggregate result for this one scenario | Yes, briefly |
| `analysis/trials.csv` | Per-attempt analyzed duration, outcomes and counts | If asked |
| `run.../trials.csv` | Original summary, including broader logger duration | Supporting evidence |
| `run.../trials.events.jsonl` | Full event chronology and timing/motion evidence | If asked how metrics were calculated |
| `run.../plan.json` | Exact effective arm/configuration profile | If asked about reproducibility |
| `observers.../*.log` | Live ROS topic observations | Show a few lines during demo |
| `metrics.json` | Timing boundary, input hashes, full numerical results | If asked about methods |
| `artifacts.json` | Plot observation counts and byte sizes | Keep as evidence |
| `source-commit.txt`, `working-tree.txt` | Checkout identity and recorded cleanliness | If asked about source version |
| `runner.log`, `ros/` | Analysis command output and runtime diagnostics | Keep for troubleshooting |

Observer logs produced by `ros2 topic echo` can abbreviate long messages with
`...`; use the full `trials.events.jsonl` when tracing an exact event or value.

The 22.761 s raw duration includes broader trial setup/HOME activity. It is not a
conflicting calculation of the 20.424 s event-defined duration. Use **20.424 s**
when discussing the task-cycle plot. With n=1, min/median/mean are the same and
sample standard deviation is undefined; do not call it zero variation.

The deck's historical result is **five visual trials, mean 19.579117 s** from a
different captured version. Label that as the archived experiment, and this
20.424 s result as the latest one-cycle rehearsal. Do not pool them or infer a
speed change from the two numbers. No controlled efficiency baseline exists.

## Finish and keep your evidence

After the demonstration, Ctrl-C in Observe and Launch. Verify the ROS graph is
empty using the command in `docs/VSCODE.md`; retain the completed launch log.
Make a new ZIP only after shutdown so it includes exit records. Keep the raw run,
matching observer folder and analysis together; send your evaluator the PDF or
PPTX, report, three result PNGs and summary CSV. Keep the complete ZIP available
as supplementary evidence, rather than presenting every log on screen.

The later opaque-station preference changes display material only. These retained
run outputs remain valid for their recorded checkout and appearance; do not edit
them to impersonate a later run. A fresh screenshot after rebuilding can show
the opaque view, clearly identified as the newer display.


## Present the three new scenes

Use [the scenario guide](../docs/DEMO_SCENARIOS.md) for tasks 13–15. Demonstrate
one scene at a time and show its own fresh standard plots and `motion/` chart.
The compact scene shows the local arms taking over between nearby stations
without another carrier reposition; the stepped scene shows changing work
heights; the precision scene shows rotated targets and tighter proxy bounds.
Explain that wrist midpoint/spacing checks concern the visual model, not verified
physical gripping. Keep results for different layouts separate. The motion
chart's reference bars are calculations rather than additional robot trials.
