# CAD information needed for the small UR5-mounted module

The SDA20D files remain **reference geometry**. The eleven extracted files
resubmitted on 2026-11-15 match the prior package byte for byte. Providing them
individually resolves the download-size issue; it does not add specifications.
Native SolidWorks features and mates could not be decoded by the available
FreeCAD 1.0 importer. This is an importer limitation, not a finding of corruption.

## Neutral geometry export

In SolidWorks on a machine that resolves the original component references:

1. Open each assembly (`Assem2.SLDASM` and `ssss.SLDASM`), resolve missing
   references, and record any suppressed/missing components. Use Pack and Go to
   retain the native dependency package if useful.
2. Export each relevant assembly with **Save As → STEP AP214 or AP242**. Record
   the units and preserve component names/assembly structure where supported.
   Export the intended small-module revision separately from the reference robot.
3. If the assembly export flattens everything into one product, also export its
   moving parts separately and provide a component-to-link map. Include the
   mounting adapter, grippers and representative workpiece if already designed.
4. Supply a joint/frame table: parent and child link, joint type, origin and axis,
   limits, zero-pose transform, and left/right tool/contact frames. Static STEP
   faces and generic geometric axes do not establish robot articulation.
5. Include dimensioned mounting drawings and assigned material/mass-property
   reports. Record revision, source and whether values are measured, supplier
   data or design assumptions. The current STEP has an invalid solid; any repaired
   export must remain separate from the original and be checked again.

The screenshots show the reference arrangement but do not define the small
module's flange transform, actuator ratings, load paths or physical fit.

## Specifications that geometry alone does not provide

- Workpiece mass/dimensions, contact surfaces, required tool orientation,
  manipulation reach and task accuracy/duty.
- Exact carrier variant, calibration, controller/driver interface and applicable
  manufacturer payload/CoG/inertia limits.
- Intended arm actuators, transmissions and grippers: limits, encoder/effort and
  object-detection feedback, communication and stop/fault behavior.
- Actual station openings and approach/retreat paths; current solid-box station
  assumptions are insufficient for qualified machine access.

The [static load worksheet](../design/bimanual_concept/LOAD_SCREEN.md) accepts
sourced mass/centre-of-gravity and mounting inputs. The
[workcell survey](WORKCELL_SURVEY.md) accepts measured station information.
Neither intake changes validation flags or authorizes physical motion.

The next implementation step depends on these inputs: map usable geometry to
an articulated model, qualify targets and paths, bind actual manipulation
feedback, and then run complete controller-backed cycles. Hardware assembly,
calibration, physical trials and mechanical acceptance still need real equipment.
Current task dispositions remain in [STATUS.md](STATUS.md).
