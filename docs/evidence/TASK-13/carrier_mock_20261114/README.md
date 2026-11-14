# Repeated synthetic carrier baseline

Agent-run 2026-11-14, ROS Humble GenericSystem in the Task-7 image
`sha256:2e84a6c6578634cfd3983b7968ea19a793213e18dcb62689a5b170ff06d01856`,
domain 119. The eight existing controller protocol checks passed first;
the benchmark then measured 20 synthetic outbound/return cycles. This run
used a development checkout; [source qualification](source.json) records the
base commit, added tool hashes and subsequent matching implementation commit.

Results: **20 attempted, 20 successful, 0 failed**, each with position feedback.
Mean cycle duration 1.15978002490001 s; sample SD 0.001075012436322022 s;
minimum 1.157048873000349 s; maximum 1.1629737890002616 s.
Timing includes both action requests/results and the final 0.05 s observation.
Planning time is null because no planner was used.

[Raw cycles](run/benchmark/cycles.csv), [summary](run/benchmark/summary.json),
[controller feedback/protocol results](run/probe/result.json),
[launch](run/launch.log), [runner](runner.log) and the empty
[residual node record](run/residual_nodes.txt) are retained. CSV counts and mean
were independently recomputed before committing; all feedback counts are positive.
Manager/RSP shutdown and one broadcaster were checked by the owning runner.

The joints move 0.05 rad from their observed starting configuration and return.
This has no grasp, station interaction, planner, collision model or physics.
It extends Task 13's carrier baseline only; full tending baseline acceptance
remains pending Task 10. All physical/grasp/end-to-end verification flags remain
false. This dataset is separate from AY-10 and changes none of its results.
