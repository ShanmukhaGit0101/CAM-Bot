# Static mass and centre-of-gravity worksheet

This extends the preliminary seven-part concept with a reproducible **single-pose
static screen**, not detailed mechanism approval. It does not copy SDA20D mass,
actuator ratings or mounting geometry. Run from the repository root with the
existing `tools/cad/requirements.txt` environment:

```bash
python tools/cad/assess_module_loads.py \
  design/bimanual_concept/parameters.json \
  design/bimanual_concept/load_inputs.template.json \
  /tmp/cambot-static-loads-NEW
python -m unittest discover -s tools/cad -p 'test_*.py' -v
```

The output directory must be new. Leave the versioned template unchanged; make
a separate working copy for real component data. Unknown is `null`, not zero.
The command successfully writes a partial report for incomplete inputs; exit
code zero means calculation completed, **not** that a design passed. Consumers
must read `status` and `unknown_inputs`.

## Definitions and input requirements

The seven generated structural solids use assumed density 2,700 kg/m³.
CadQuery centres and volumes are converted from mm and mm³ to metres and m³.
The structure is in its original concept zero pose, with the arms extending
along module +Y. It excludes adapter, brackets, actuation, bearings/fasteners,
grippers, cabling/guards and workpieces.

Supply mass and centre of mass for **both arms combined** in each corresponding
`component_groups` entry. Centres are expressed in the **module concept frame**,
in metres. Include a datasheet, CAD mass-property record or measurement source.
Avoid double-counting parts already in the seven structural solids. A group may
be zero only when explicitly justified as absent in `source`; blank/unknown
entries cannot silently become zero. The prototype does require a mounting load
path even if a user-supplied static worksheet claims zero bracket mass.

`module_pose_in_flange` is a separate, sourced transform:

```json
{
  "translation_xyz_m": [0.0, 0.0, 0.0],
  "rotation_rpy_rad": [0.0, 0.0, 0.0],
  "source": "Replace with the actual mounting drawing/measurement; these zeros are syntax only"
}
```

It maps module coordinates to flange coordinates as
`p_flange = translation + Rz(yaw) Ry(pitch) Rx(roll) p_module`.
Do not adopt the illustrative identity transform as a measurement.

`carrier_limits` needs an exact model, sourced mass limit and sourced static
moment limit applicable to the load case. No default UR5 rating is supplied.
If the manufacturer specifies a coupled mass/CoG/inertia envelope instead of a
single moment limit, obtain the proper assessment; do not invent a scalar limit
to make this worksheet pass.

## Calculation and interpretation

For known components, `M = sum(m_i)`, `c = sum(m_i r_i)/M`, weight magnitude is
`M g`, and the maximum static gravity moment about the chosen origin is
`g ||sum(m_i r_i)||`, with `g = 9.80665 m/s²`. The maximum varies gravity direction
for this **fixed geometry**, not arm poses. The module origin is not automatically
the UR5 flange. A sourced mounting transform is required for flange results.

Unknown groups remain listed. Their absence prevents a total assembly mass and
a complete limit comparison. Known-subtotal moments are not upper/lower bounds
on a future completed assembly: added components can shift or cancel moments.
Malformed/nonfinite/negative masses and invalid transforms are rejected.

Even `STATIC_SCREEN_PASS_REQUIRES_DYNAMIC_AND_PHYSICAL_VALIDATION` establishes
only these two supplied scalar inequalities at one concept pose. It does not
establish actuator torque ratings, dynamic inertia, stress/deflection, joint
travel extremes, grip force, fatigue, coupled robot payload compliance, a
mechanical load path or physical operation. Manufacturing and hardware-execution
approval fields remain false for every result.
