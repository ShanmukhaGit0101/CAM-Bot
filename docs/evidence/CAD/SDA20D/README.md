# SDA20D reference CAD intake

Reviewed 2026-11-15 (Asia/Calcutta). The user explicitly selected this package
as a reference for a small UR5-mounted bimanual module. It does not replace the
UR5 carrier or establish compatibility of the complete SDA20D with its flange.

[Package manifest](package_manifest.json) inventories eleven unique uploaded
files: one STEP, two SolidWorks assemblies and eight SolidWorks parts. The
STEP was uploaded twice with identical bytes. Only the neutral source is
retained here; native files remain in the user's uploaded package. The runtime
cannot decode SolidWorks mates/features, so native assembly structure and
component completeness have not been verified. Native source filenames are not
joint definitions or a bill of materials.

## Neutral source findings

The [original STEP](source/SDA_20D.stp) is preserved unchanged with SHA-256
`f9ba3a690854f2d98fbba69be7bf02fbec57cdbcf4fbf2aae58225367804f859`.
Its AP214 header names Siemens UGS NX 6.0, timestamp 2010-11-01, with a single
product `Mart853475wx`. Filename and imagery suggest SDA20D, but product
metadata does not authenticate a robot model, revision or calibration.

[Geometry report](geometry.json) records CadQuery 2.7.0 / OpenCascade 7.8.1.1:

- Explicit length units: millimetres.
- Static extent in file axes: approximately **1.590 × 0.690 × 1.011 m**.
- 17 imported solids, 4,048 faces; solid index 14 fails validity checking.
- Whole-shape validity is false, independently checked.
- Eleven `MANIFOLD_SOLID_BREP` entities in the text become seventeen kernel
  solids; these counts describe different representations, not seventeen links.
- No `NEXT_ASSEMBLY_USAGE_OCCURRENCE`, `REVOLUTE_PAIR` or `KINEMATIC_JOINT`
  definitions were found. Generic geometric axis placements are not joint axes.
- No supported density/BOM, total mass, actuator specification, gripper sensing,
  mounting transform or UR5 payload qualification is established by this import.

Do not automatically heal the source or use its invalid body as accepted
collision geometry. Any repaired/re-exported model needs a separate file,
original-to-repair mapping and a fresh topology/dimension check. Volumes are
geometric values only and may overlap; summing them cannot establish robot mass.

## Reproduction and tests

Install the optional CAD dependencies from `tools/cad/requirements.txt` in a
separate environment. They are not ROS package dependencies. Run from root:

```bash
python3 tools/cad/inspect_step.py \
  docs/evidence/CAD/SDA20D/source/SDA_20D.stp /tmp/cambot-sda20-new
python3 -m unittest discover -s tools/cad -p 'test_*.py' -v
```

Choose an unused output directory. Per-solid inspection of this large model
can take minutes. The initial inspection generated geometry.json; an expensive
optional hidden-line SVG render was stopped after geometry inspection finished.
No reference SVG or successful rendering is claimed. The current CLI defaults
to geometry-only output; `--preview` explicitly requests the slower renderer.
The report's whole_shape_valid field was added from the independently executed
whole-shape check, as recorded in that field's basis note.

Fresh tests: four passed, covering cube dimensions/volume and mm-to-m units,
unknown-unit rejection, existing-output refusal, concept component validity,
symmetry and impossible/nonfinite dimensions. No fresh ROS test was needed:
this change adds standalone CAD tools and design evidence only.

## Small-module continuation

The separate [preliminary design](../../../../design/bimanual_concept/README.md)
uses CAM-BOT's existing dimensions and the reference's symmetric two-arm idea.
It does not scale down the SDA20D mechanism or claim to reproduce its joints.
Actual payload, reach/orientation requirements, robot model/flange limits,
actuator interfaces, bearing arrangements and measured workcell remain needed.
