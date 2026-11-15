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
- Fully opaque station visuals, retaining the original colours and geometry.
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

## Exchanged arm arrangement and shorter carrier turns

The next update on the same branch implements the user's requested side swap.
The presentation wrapper now writes a fresh `plan.json` into each run directory:
left/right pose **pairs** and workspace labels are exchanged together. The visual
assembly exchanges the shoulder mount positions and mirrors the right elbow's
X axis. Both forearms therefore fold in the same local Z direction during
GRASP/HOLD, instead of one folding up and the other down. Joint names and the
UR5 chain remain intact. This is an intentional local assembly/motion change,
unlike the earlier styling-only layer described above.

The new `plan.json` is the effective configuration recorded in CSV/events; the
installed `machine_tending.json`, controller targets and sealed captures are not
edited. The assembly profile is selected by its `visual_arm_layout` field,
independently of `presentation_view`, which only selects drawing style.

Visual carrier motion now selects the shortest equivalent angular route inside
the stock UR5 model's limits. A wide-range joint may first need a full-turn
change of its *numeric representation* so the shorter path fits in the interval.
That preserves orientation; it is not a full-turn robot movement. The selected
endpoint is kept through the final TF publications, avoiding a snap back to the
old stored number. Logs retain previous/configured angles and the effective
start/goal so winding changes are explicit. All carrier interpolation entry
points use this policy; physical controller action goals are unchanged.

This policy is for visual joint publications only. It does not establish cable
winding, a valid hardware trajectory or collision-free transit. The mirrored
pose remains a visual illustration: tool contact, object attachment and grasp
feedback are not physically verified. The workpiece continues to follow the
existing visual state interpolation.

[New motion replay and measured turn angles](evidence/DELIVERY/arm_motion_20261115/README.md).
After pulling this update, rebuild the core packages and restart Launch/Observe;
the existing VS Code task sequence automatically uses the new effective plan.


## Opaque workcell preference

The user requested solid station bodies after viewing the new arrangement.
The latest renderer preserves their original material alpha of 1.0; no ghosting
is applied. Earlier retained screenshots remain translucent as historical
records. Rebuild and restart RViz to load the opaque view. This material-only
change does not alter the swapped arms, angular routing or prior trial metrics.
