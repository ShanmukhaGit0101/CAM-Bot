# Arm presentation repair — 2026-11-15

The user reported that the grey box arms and oversized dark mounting plates were
hard to interpret in RViz. This opt-in display profile replaces only attachment
visuals, makes station bodies translucent, and corrects the camera focal point.
The workbench presentation launch enables it automatically. The original launch
view is retained with `presentation_view:=false`.

- [Idle preview](idle.png), [S1](S1_APPROACH.png), [S3](S3_LOAD.png), [S5](S5_PLACE.png).
- [Implementation and use](../../../ARM_PRESENTATION.md).
- [Exact tested sources/environment](verification.json) and [source snapshot](source/presentation_model.py).
- [Final package tests](tests-final.log): 80 results, zero errors/failures,
  two existing copyright skips. Five new tests check preserved joints,
  collisions/inertials, upstream visuals, arm geometry and station translucency.
- [Live observer result](result.json): normal coordinated visual cycle passed,
  one authoritative joint-state publisher, `FINISHED_AT_S5`.
- [Raw trial](run/trials.csv), [events](run/trials.events.jsonl),
  [analysis](analysis/metrics.json): one success, five visual repositions,
  20.574897155 s using the standard event timing boundary. This separate
  presentation run is not pooled with the sealed five-trial qualification.
- [Launch log](launch.log): all three children exited cleanly on SIGINT;
  [residual nodes](residual_nodes.txt) is empty.

The execution copy was based on `b5d47f2` plus working changes, while the repair
branch starts at merged main `f231278`. Those two commits have identical ROS
sources before this patch. The run's CSV source SHA alone does **not** identify
the modified renderer: the retained source snapshots/hashes are required.

The disposable controller image had apt RViz 11.2.29 available, with Xvfb/xauth
added for rendering. It did not have the accepted pinned RViz overlay. This run
checks normal completion/rendering/shutdown; it is not a new five-interruption
or independent-human acceptance suite. Continue using the existing prepared
patched Humble image on the user's laptop.

Initial lint/docstring failures and a stale inventory-hash check are retained
in `tests-initial.log` and `tests-intermediate.log`; those were repaired before
`tests-final.log`. A first capture harness invocation could not create a new
session because Docker exec already owned one. A subsequent observer started
before the launch's empty-domain preflight, which correctly rejected it. The
final attempt waits for launch readiness before creating its observer and
passes; no application motion changes were needed for these harness issues.

The style leaves physical contact, robot/workpiece alignment, IK and collision
validation at the existing visual-only scope. Fixed tool outlines are not
actuated grippers. No numerical archived results, coordinator logic, station
poses, controller targets or physical verification flags were altered.
