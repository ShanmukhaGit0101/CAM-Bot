# Clearer arm presentation view

The November 15 screenshots show the original, deliberately simple placeholder:
large dark mounting boxes, grey box links and opaque station bodies. Those
visuals obscure the carrier and make the elbow articulation difficult to read.
This repair supplies a separate display profile rather than changing the tending
plan to make its unvalidated motion appear physically qualified.

`presentation_view:=true` on `dual_arm_demo.launch.py` selects:

- Slimmer **visual** flange/base covers, preserving the existing mounting frames.
- Blue left links and orange right links, cylindrical segments and visible
  shoulder/elbow housings, along the original link centre lines.
- Fixed passive tool outlines at the forearm tips, without added joints or grasp
  actuation. Their opening is illustrative and is not fitted to the workpiece.
- Translucent station visuals so the carrier remains visible behind stations.
- A dedicated RViz view with a correctly encoded camera focal point above the
  floor; TF axes are hidden to reduce visual clutter.

Every joint, transform, limit, collision shape and inertial element is preserved.
The official UR5 visuals are also preserved. The display covers are illustrative
and do not describe the original conservative collision envelopes. The existing
geometric reachability proxy, carrier targets, FSM and workpiece interpolation
are unchanged; this is not a contact, collision or manipulation-path repair.
The known limitations about arms not physically grasping the workpiece remain.

## Use from VS Code

Stop the old Launch and Observe tasks with Ctrl-C first. Update to the repair
branch or its merged main, then run:

1. **CAM-BOT: 01 Build visual demo**.
2. **CAM-BOT: 02 Test core packages**.
3. **CAM-BOT: 03 Launch RViz (wait for Start)**.
4. **CAM-BOT: 04 Observe workflow**, then **05 Start one cycle**.

The workbench's presentation wrapper enables this view automatically. No new
Docker image is necessary on an existing prepared Humble GUI environment; rebuild
the two repository packages. A running RViz process will not reload the changed
URDF merely because a file was updated: stop and relaunch it.

For the exact original display, invoke the existing launch directly with
`presentation_view:=false` (the launch argument defaults to false). Keep
`enable_coordination:=true`. Do not run both launches simultaneously.

Existing slides, images and sealed experiments retain their original appearance
and provenance. New screenshots/logs belong in fresh output directories.

[Retained visual run, previews and regression results](evidence/DELIVERY/arm_view_20261115/README.md).
