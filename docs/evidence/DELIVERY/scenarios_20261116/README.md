# Three additional visual scenarios — 2026-11-16

The user requested three different, progressively more complex block-cell
examples with efficient carrier and paired-arm movement. The original demo is
retained. [Use the new scenes](../../../DEMO_SCENARIOS.md) through VS Code tasks
13–15 or the existing workbench launch wrapper.

## Actual patched-overlay replay

One normal cycle was run per layout in a separate execution copy based on
`eb65d61` plus the scenario/telemetry changes. All four reached `FINISHED_AT_S5`,
exercised both coordination branches and live TF rechecks, had one authoritative
joint-state publisher, three clean process exits and empty residual graphs.

| Scenario | Completed cycles | Visual repositions | Event-defined cycle (s) | Carrier joint excursion (rad) | Local-arm excursion (rad) |
|---|---:|---:|---:|---:|---:|
| Original reference | 1/1 | 5 | 20.481115 | 41.614621 | 15.800000 |
| Compact shared workspace | 1/1 | 3 | 17.754321 | 35.660783 | 13.590543 |
| Stepped-height cell | 1/1 | 5 | 20.556384 | 41.184719 | 8.246297 |
| Precision transfer | 1/1 | 5 | 20.458640 | 41.873301 | 5.437275 |

These are different assumed layouts and one attempt each. They are not pooled,
statistical reliability evidence or a controlled throughput comparison. The
joint metric sums absolute changes over joints in completed visual segments,
including HOME; it is not a distance or energy measurement.

- Previews: [compact](patched-replay/compact/S3_LOAD.png),
  [stepped](patched-replay/tiered/S3_LOAD.png),
  [precision](patched-replay/precision/S3_LOAD.png).
- [Full numerical summary](summary.json), [source/environment](verification.json).
- Runtime evidence is retained under each `patched-replay/<scenario>/`: observer,
  launch/shutdown log, raw trial/events, exact effective plan and residual graph.
- Standard plots/metrics and the extra joint-motion report are under
  `reports/<scenario>/analysis/` and `reports/<scenario>/motion/`.
- Motion reports include explicitly labelled **calculated references**: raw
  stored-angle interpolation for the same carrier goals, and returning local
  arms HOME before each next local segment. Neither reference is a separately
  executed baseline. They do not establish physical performance improvement.

## Checks

- [Core package suite](tests-pass.log): **92 results, zero errors/failures,
  two existing copyright skips**. New adapter checks cover actual local-motion
  telemetry and cancellation without false completion.
- [Tool suite](tool-tests.log): **12 tests passed**. Checks include deterministic
  configuration regeneration, original-plan preservation, controller readiness
  rejection, actual mirrored two-arm FK/wrist anchors, proxy-based move counts,
  non-overlapping station rectangles and independent motion-report arithmetic.
- [Historical analyzer suite](analysis-tests.log): **14 passed**.
- [Build](build.log), [VS Code workbench analysis entry point](workbench-analysis.log),
  syntax, local documentation links and current source inventory passed.
- New layouts use opaque blocks, valid local joint ranges and stock carrier
  joint limits. Offline station rectangle separation is not robot/path collision
  validation. Tool contact and physically attached workpiece motion are not proven.

The first two package runs found formatting issues; both logs are retained.
The final package result follows those repairs. Runtime application code and
scenario source files match the retained execution-copy bytes. The raw CSV SHA
identifies the base commit plus this working patch, qualified by the [source
snapshots](source/machine_tending_coordinator.py) and hashes.

## RViz environment repair and failed attempt

The initial disposable image did not have the repository's pinned RViz overlay.
The original cycle passed; the compact cycle also completed, but its RViz child
aborted on shutdown (`corrupted size vs. prev_size`). That attempt is retained
under `unpatched-attempt/` and is **not** an accepted clean run.

The existing patch was applied to upstream revision
`4e2b27b7561da7eb03fbc7e92a74d4b3f1e0b054` (RViz 11.2.29), and `rviz_common` was
built into `/opt/cambot/rviz`, following `tools/cloud/Dockerfile.humble`. The
[build log](rviz-build.log) and [linker/library hash record](rviz-overlay.log)
confirm the overlay was loaded. All four cases then passed a fresh replay with
clean shutdown. No new RViz source patch or application motion workaround was
introduced. The user's prepared patched GUI image needs no rebuild for these
scenario configurations.

This is agent-run Humble/RViz rendering under Xvfb with software GL, not another
independent human acceptance, a fresh five-interruption suite or physical
controller/grasp verification. Earlier sealed captures and accepted AY statuses
are unchanged.
