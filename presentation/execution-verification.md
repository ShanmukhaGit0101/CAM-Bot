# Execution and packaging verification

Verified on 2026-11-15, from base `b5d47f2` plus the new execution/presentation
helpers. [Retained logs and source hashes](../docs/evidence/DELIVERY/execution_20261115/verification.json)
identify the tested working changes. The robot implementation under `src/` and
all prior sealed evidence are unchanged.

| Check actually executed | Result |
|---|---|
| Workbench `build`, Docker backend, separate execution copy | Both core packages built |
| Workbench `test` | 75 results, 0 errors/failures, 2 existing copyright-header skips; installed checker passed |
| Workbench `offline-test` | 24 tool/presentation/geometry tests + 14 analysis tests passed |
| Presentation/workbench tests inside lean Humble image | 7 passed without requiring PowerPoint export dependencies |
| Additional documentation-checker regressions | 5 passed (entry-point suite has 12 total including 7 overlapping tests) |
| Workbench `analysis` | Five attempts; regenerated metrics JSON exactly matches archived metrics |
| Workbench `analyze-run` with retained CSV as fixture | Passed into another fresh output; no new live trial claimed |
| Workbench `workspace` | 20,000 random + 6 known samples; numerical results match prior report; provenance/version metadata differs |
| Workbench `mock-build` and `mock-test` | Three packages built; 8 carrier + 7 bimanual real-JTC/GenericSystem cases passed; one broadcaster, empty residual graph |
| Existing offline FSM trace used by F5 | Success reaches `FINISHED_AT_S5`; injected load failure correctly returns FAILURE |
| Workbench presentation server | Served embedded HTML on loopback port 8765 |
| Shell syntax / Python compilation / task JSON | Passed |
| Documentation, source inventory and local links | Passed |
| Live GUI launch preflight in test container | Correctly refused unset DISPLAY, exit 2; no fresh GUI run |
| Browser deck/navigation/replay/notes/export | 12 slides; replay completion/pause/reset passed; no JavaScript errors; 12-page PDF and PPTX notes checked |

The first mock-task attempt failed because the available controller image lacked
Git LFS when Git inspected the copied checkout. Its failure log is retained.
Installing `git-lfs` 3.0.2-1ubuntu0.3 in the disposable test container fixed the
retry. The Docker recipe now includes that dependency; the full updated image
was **not rebuilt** in this verification. Core build/test used the image before
that addition. [Mock replay logs](../docs/evidence/DELIVERY/execution_20261115/mock-replay/launch.log)
retain controller errors intentionally injected by the tests.

The same Bash entry points used by VS Code were executed, rather than claiming
that someone manually clicked every task in the editor. F5's underlying Python
trace was executed; interactive breakpoint controls were not manually tested.
No new patched-RViz GUI acceptance or physical test is claimed. Use the existing
accepted Humble image and perform one GUI rehearsal on the presentation laptop.

The HTML browser test used loopback HTTP because the managed Chromium policy
blocks `file://`. External network requests were blocked. To reproduce packaging
checks in a **new generated directory**, install `playwright` and `PyMuPDF` in
addition to `tools/workbench-requirements.txt`, provide Chromium, then run:

```bash
python tools/build_presentation.py --output /tmp/cambot-deck-NEW
python tools/validate_presentation.py /tmp/cambot-deck-NEW --chromium /usr/bin/chromium
```

The validator writes PDF, screenshots and `verification.json` in that generated
directory. [Deck provenance](sources.json) ties the displayed results to the
unaltered source captures. [Artifact manifest](manifest.json) hashes this package.
