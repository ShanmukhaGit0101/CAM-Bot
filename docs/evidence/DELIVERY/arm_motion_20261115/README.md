# Exchanged arms and shortest visual turns — 2026-11-15

Implements the user's requested left/right exchange and avoids long-way visual
carrier rotation on `fix/arm-presentation`. This is a new visual arrangement,
not a new physical-grasp or manufacturing acceptance record.

The effective [run plan](run/plan.json) exchanges the arm pose pairs and proxy
labels. The renderer exchanges shoulder origins and mirrors the right elbow
axis; both elbows fold in the same direction. The original installed config,
carrier kinematic chain and physical-controller targets are unchanged.

Visual carrier routing considers equivalent start/end angle representations
inside the stock model's limits. It minimizes angular travel, retaining the
chosen endpoint in final TF publications. A full-turn *number* change can be
necessary to choose a valid winding interval; its orientation is identical.
Previous angles, configured targets and effective route endpoints are logged.
Do not interpret that numerical rebase as a physical unwind or send the derived
visual route to a hardware controller.

## Observed results

- [Package tests](tests-final.log): **90 results, zero errors/failures, two
  existing copyright skips**. New tests cover 270°/90° routing, wrap boundaries,
  joint-limit constraints, no endpoint snap, cancellation, controller-mode
  exclusion, plan immutability and mirrored-arm mounting/folding.
- [Headless RViz observer](visual/result.json): one successful cycle,
  `FINISHED_AT_S5`, one authoritative joint-state publisher. [Grasp illustration](visual/S1_GRASP.png),
  [S3 transfer](visual/S3_LOAD.png), [S5](visual/S5_PLACE.png).
- [Route and joint-sample check](route-check.json): 711 samples; every recorded
  base route <=180°. S3→S4 takes **89.260798°**. Maximum adjacent per-joint
  orientation change is 0.117572 rad; full-turn numeric representation changes
  are measured modulo 2π. The exact 270°→−90° case is also a regression fixture.
- [Unreachable](failure-cases/unreachable/probe.jsonl),
  [injected load failure](failure-cases/load_failure/probe.jsonl) and
  [cancellation](failure-cases/cancelled/probe.jsonl) all pass existing observers.
  Each stops before inappropriate workpiece advancement and leaves an empty graph.
- [Normal launch shutdown](visual/launch.log) and all three failure-case launch
  shutdowns have clean exits for RSP, coordinator and RViz. Residual-node records
  are empty. No assertion is made about five active-interruption repetitions.
- [Separate one-trial analysis](analysis/metrics.json): one success, five visual
  repositions, **20.430742479 s** using the existing timing boundary. All 14
  [analysis regression tests](analysis-tests.log) pass. There is no comparative
  throughput claim and the prior sealed five-cycle result remains unchanged.

The first package test attempt found formatting issues, repaired before the
final suite. Its [log](tests-initial.log) is retained. The raw CSV identifies
base `854f056` plus this working patch; use the [source hashes/snapshots](verification.json)
to identify the exact tested implementation, rather than the base SHA alone.
Capture harnesses are retained with the explicit temporary paths used; use new
output directories if adapting them for another replay.

The disposable local image contains apt Humble RViz 11.2.29, Xvfb and software
rendering, without the independent review's pinned overlay. These four launches
shut down cleanly, but this record does not replace the pinned-image suite or
claim another human review. The user's existing patched GUI image should still
be used on the laptop.

Gripper outlines are passive. Object placement/transfer remains visual state
interpolation; verified contact, collision-free transit and grasp feedback are
still outside the demonstration's accepted scope. This change corrects arm
sidedness/folding and visible carrier rotation, not those deferred capabilities.
