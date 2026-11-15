# Preliminary small UR5-mounted bimanual module

Generated 2026-11-15, **layout concept only**. The user supplied an SDA20D CAD
package as a reference for designing the small module, while retaining CAM-BOT's
UR5 carrier. [Reference assessment](../../docs/evidence/CAD/SDA20D/README.md).

[Parameters](parameters.json) make every dimension and material assumption
explicit. The symmetric two-arm layout uses the existing placeholder's 420 mm
base length, 280 mm width, ±220 mm shoulder offsets and 250/220 mm arm lengths.
New assumptions are a 5 mm open-frame plate, 32/28 mm hollow square beams with
2 mm walls, and cylindrical shoulder envelopes. These are not selected motors,
bearings, grippers or a verified scaling of the reference robot.

Artifacts:

- [Named STEP assembly](generated/module_concept.step).
- [Static preview](generated/module_concept.svg) and [PNG](generated/preview.png).
- [Structural mass and missing-design report](generated/design_report.json).

The assembly is a static zero-pose arrangement. The current four-joint module
uses shoulder Z and elbow X axes; the STEP assembly does not create live joint
constraints. The seven solids are geometric envelopes. In particular, the
shoulder locations lie outside the base edge; shoulder brackets and the complete
mounting load path remain undeveloped. Do not fabricate or load this layout.

The mass worksheet multiplies modeled volumes by assumed 2,700 kg/m³ density.
It excludes the UR5 adapter, actuators/gearboxes, bearings, fasteners, grippers,
cables, guards, brackets and workpieces. It is not total assembly mass or a
claim that the UR5 payload/moment limits are met. Payload, torque and actuator
ratings remain null. Do not treat the placeholder's URDF effort limits as
actuator ratings. Detailed sizing needs worst-case gravity, acceleration,
transmission efficiency, duty and structural stiffness/load analysis.

## Regenerate without overwriting

From a checkout with `tools/cad/requirements.txt` dependencies installed:

```bash
python3 tools/cad/build_module_concept.py \
  design/bimanual_concept/parameters.json /tmp/cambot-module-new
python3 -m unittest discover -s tools/cad -p 'test_*.py' -v
```

Use a new output directory. Four fresh CAD-tool tests passed. The generated
STEP contains seven named parts, all geometrically valid; no joint or collision
feasibility is inferred. The preview was rendered from SVG with system PySide2
QSvgRenderer after the ImageMagick SVG delegate was unavailable.

## Inputs needed before detailed design

1. Workpiece payload per arm, dimensions, grip surfaces, grasp force/friction
   assumptions, required tool orientation, reach, accuracy and cycle duty.
2. Exact UR5 variant/calibration and manufacturer payload, centre-of-gravity and
   allowable moment/inertia envelope, plus flange mounting specification.
3. Actuator/gearbox and gripper models or design constraints: torque/speed,
   backlash, encoder/effort feedback, braking and communication interfaces.
4. Mounting envelope, module mass/centre-of-gravity allocation, cabling/power,
   bearing arrangements, fasteners and load-path design.
5. Reviewed CAD and calculations, tolerance stack-up, collision/clearance study,
   then fabrication and supervised physical validation.

The [Tasks 7–15 dependencies](../../docs/CONTROLLER_NEXT_STEPS.md) still apply.
Reference CAD advances Task 15's concept preparation, not completed mechanical
validation. It does not supply controller/grasp feedback (Tasks 7–8), articulated
IK/collision models (9), complete tending evidence (10/13), physical trials (11),
or validated workspace/placement recommendations (12/14). Existing AY-13 visual
acceptance and runtime configuration remain unchanged.
