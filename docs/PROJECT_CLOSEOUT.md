# Project closeout — visual demonstrator and presentation

**Decision: 2026-11-15 (Asia/Calcutta).** The user chose to conclude the project
at its primary visual-simulation objective and prioritize demonstrating the
integrated work and contributions. Completion does not require implementing
all later controller, hardware and manufacturing extensions.

The accepted delivery scope is a reproducible **ROS 2 Humble visual machine-
tending demonstrator**, its measured visual results, supporting engineering
studies, and a presentation/report package. AY-01–AY-13 are complete within
that scope. The independent visual acceptance remains the existing recorded
review; this closeout does not invent another review or hardware result.

## Final deliverables

- Existing five-station workflow, carrier/local coordination, visual workpiece
  progression, start/cancel/reset interfaces and event logging.
- Five sealed visual trials and reproducible analysis; scoped validation and
  independent reproduction evidence.
- Retained carrier, mass, workspace, controller-mock and mechanical studies,
  with their original limitations and failed attempts.
- [Presentation package](../presentation/README.md): editable slides, offline
  browser presentation/replay, PDF, speaker notes, demo guide and final report.
- [Contribution record](../presentation/CONTRIBUTIONS.md) grounded in documented
  roles, repository artifacts and honest authorship boundaries.

- [VS Code execution guide](VSCODE.md): build/test tasks, live demo controls,
  topic logging, fresh analysis and offline FSM debugging.

## Scope freeze

Tasks 7–15 are **deferred extensions, not final-project completion blockers**.
Their technical states remain visible in [STATUS.md](STATUS.md). Partial work
is retained; physical trials, complete controller-backed tending, validated
workspace/placement and manufacturing acceptance are not declared complete.

No further robotics features, robot-chain changes or new CAD revisions are
required for this delivery. Keep the accepted visual demo stable. Address a
presentation-blocking defect if demonstrated, but do not expand scope merely
to make every future-work item green. Keep the current feature branch for this
package; no automatic merge into main is performed.

Before the actual presentation, rehearse the prepared demo once and test the
HTML/PDF fallback on the presentation machine. This is event preparation, not
another research milestone. A live GUI run on the audience's machine cannot
be promised by offline packaging checks.


## User-requested presentation extension — 2026-11-16

The user subsequently requested three additional visual scenes with increasing
layout/coordination complexity. [These scenarios](DEMO_SCENARIOS.md) extend the
presentation within visual scope. They do not reopen the deferred physical
engineering tasks or change the sealed five-trial experiment.
