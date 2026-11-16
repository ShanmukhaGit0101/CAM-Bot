# CAM-BOT speaker notes

Suggested running time: 10–12 minutes, including one demonstration.

## 1. CAM-BOT

Ayush opens (35 seconds). Our goal is to demonstrate the coordination architecture and make its behavior measurable. This is the completed visual-simulation project. We will show the live workflow or its retained event replay, then evidence and contributions.

## 2. Separate transit from local work

Shannu (40 seconds). Explain the carrier-assisted concept before discussing code. We investigate the architecture; we have not measured an efficiency advantage over a controlled conventional baseline.

## 3. One task-level coordinator

Shannu (50 seconds). Use the three architecture boxes. Global positioning and local actions meet in the coordinator. The accepted demonstration uses four placeholder joints and a geometric reachability proxy, not collision-aware grasp planning.

## 4. Five stations, one visible sequence

Ayush (40 seconds). Point out the carrier, mounted local arms and the five stations. Explain the simulated workpiece. This screenshot is retained evidence; switch to the prepared live RViz window if available.

## 5. Reposition only when the proxy requires it

Ayush or Shannu (45 seconds). Explain the actual decision contract. Local workspace checks are geometric proxies. The recorded scenario has five visual repositions per trial; do not call this globally optimal planning.

## 6. Watch one complete workflow

Ayush (90 seconds including the demo). For live mode: run bash tools/present_demo.sh in the prepared Humble environment, then the start command in a second terminal. Otherwise use Play recorded trial in the HTML. Say explicitly that this replays event timestamps and states, with a static screenshot—not live ROS or animated robot reconstruction. Let it finish before moving on.

## 7. Repeatable within the fixed visual scenario

Ayush (55 seconds). State the measurement boundary. The published 19.579117-second mean comes from events; the broader elapsed field in the raw CSV includes additional time. Five successes demonstrate this scenario, not industrial reliability, throughput or grasp accuracy.

## 8. Explore the design space

Shannu (55 seconds). Show the workspace image as a kinematic study, not a guaranteed collision-free reachable volume. Mass-study recordings were not time-aligned and derived accelerations are not force/torque measurements. These studies show engineering investigation and transparent limits.

## 9. Reproducibility is part of the result

Ayush (50 seconds). Distinguish independent visual acceptance from agent-run controller experiments. GenericSystem supplies mock positions. The 20 cycles are carrier protocol benchmarks, not full physical or controller-backed tending cycles. We preserved failed attempts as well as passes.

## 10. From placeholder to an original compact concept

Tanmay presents the mechanical workstream (50 seconds). Explain mounting, local-arm layout and design evolution. The recent original compact model was AI-assisted at Ayush’s direction; do not claim that it was manufactured or individually authored by another member. Do not call the allocated mass a verified UR5 load qualification.

## 11. Three workstreams, one integrated deliverable

All members (45 seconds total). These are documented workstreams and suggested speaking roles, not claims that every roadmap checkbox is complete. Use CONTRIBUTIONS.md to identify actual artifacts and attribution. Acknowledge upstream open-source tools and AI-assisted implementation/design support.

## 12. An integrated, reproducible visual demonstrator

Ayush closes (40 seconds). We are wrapping up the visual prototype, not asserting deployment readiness. Tasks 7–15 are future extensions outside this final delivery. The contribution is the integrated architecture, reproducible behavior, transparent measurements and documented engineering studies. Invite discussion.

