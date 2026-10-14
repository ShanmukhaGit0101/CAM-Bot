# AY-01…AY-13 traceability

The authoritative mapping is
`/home/ayush/TOPS/CAM-BOT_Ayush_Individual_Task_Document.pdf`. The earlier
project-local inferred mapping is superseded and must not be used for acceptance.

| ID | PDF-defined task | Current disposition after first gate |
|---|---|---|
| AY-01 | Obtain and integrate Phase 4 source | BLOCKED — source found; clean Humble reproduction not run |
| AY-02 | Repository / GitHub integration | BLOCKED — clean checkout/build/launch not verified |
| AY-03 | Single-command launch | BLOCKED — launch/TF/joints/motion/shutdown not runtime-tested |
| AY-04 | Five-station workcell integration | BLOCKED — assumed geometry exists; Tanmay geometry and runtime launch missing |
| AY-05 | Machine-tending state machine | BLOCKED — offline transitions exist; execution/reset not runtime-tested |
| AY-06 | Carrier ↔ dual-arm coordination | BUILD required — current fixed sequence has no reachability/re-check decision |
| AY-07 | Workspace / reachability decision logic | BUILD required — no explicit tested workspace rule exists |
| AY-08 | Integrate coordination with simulation | BLOCKED on AY-06/07 and ROS runtime |
| AY-09 | Experiment logger | REPAIR required — schema/CSV exist but lack all PDF fields and runtime proof |
| AY-10 | Run at least five trials | BLOCKED — no qualifying measured trials |
| AY-11 | Calculate performance metrics | BUILD required after AY-10 dataset |
| AY-12 | Result plots and tables | BUILD required after AY-11 metrics |
| AY-13 | Technical documentation | REPAIR required — traceability corrected; runtime/results records pending |

The five-station locations and placeholder dimensions remain configurable visual
simulation assumptions, not measurements from Tanmay or a real cell.

