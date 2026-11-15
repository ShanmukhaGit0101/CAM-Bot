#!/usr/bin/env python3
"""Generate a separate static four-joint concept and structural mass worksheet."""

import argparse
import hashlib
import json
import math
from pathlib import Path

import cadquery as cq


def build(p):
    for name in ['base_length', 'base_width', 'base_thickness', 'base_border',
                 'shoulder_offset_x', 'shoulder_height', 'upper_length', 'upper_width',
                 'forearm_length', 'forearm_width', 'wall', 'assumed_structure_density_kg_m3']:
        if isinstance(p[name], bool) or not isinstance(p[name], (int, float)) or not math.isfinite(p[name]) or p[name] <= 0:
            raise ValueError(name + ' must be finite and positive')
    if 2 * p['base_border'] >= min(p['base_length'], p['base_width']):
        raise ValueError('base border consumes the opening')
    if 2 * p['wall'] >= min(p['upper_width'], p['forearm_width']):
        raise ValueError('wall consumes the link bore')
    if p['shoulder_offset_x'] <= p['base_length'] / 2:
        raise ValueError('shoulder axes must clear the base edge in this concept')
    parts = {}
    base = cq.Workplane('XY').rect(p['base_length'], p['base_width']).rect(
        p['base_length'] - 2*p['base_border'], p['base_width'] - 2*p['base_border']).extrude(p['base_thickness'])
    parts['base_frame'] = base.val()
    # Static zero-pose only. Ring/beam solids omit motors, bearings and fasteners.
    for side, sign in [('left', -1), ('right', 1)]:
        x, z = sign * p['shoulder_offset_x'], p['shoulder_height']
        riser = cq.Workplane('XY').circle(20).circle(17).extrude(z).translate((x, 0, 0))
        parts[side + '_shoulder_envelope'] = riser.val()
        for label, length, width, y in [
            ('upper', p['upper_length'], p['upper_width'], 0),
            ('forearm', p['forearm_length'], p['forearm_width'], p['upper_length'])]:
            beam = cq.Workplane('XZ').rect(width, width).rect(
                width - 2*p['wall'], width - 2*p['wall']).extrude(-length)
            parts[side + '_' + label] = beam.translate((x, y, z)).val()
    return parts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('parameters', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('output must not exist')
    p = json.loads(args.parameters.read_text())
    parts = build(p)
    args.output.mkdir(parents=True, exist_ok=False)
    assembly = cq.Assembly(name='CAMBOT_preliminary_module')
    rows = []
    for name, shape in parts.items():
        assert shape.isValid(), name
        assembly.add(shape, name=name)
        mass = shape.Volume() * 1e-9 * p['assumed_structure_density_kg_m3']
        rows.append({'part': name, 'volume_mm3': shape.Volume(), 'assumed_structure_mass_kg': mass})
    assembly.export(str(args.output / 'module_concept.step'))
    cq.exporters.export(cq.Compound.makeCompound(list(parts.values())),
                        str(args.output / 'module_concept.svg'),
                        opt={'width': 900, 'height': 700, 'projectionDir': (1, -2, 1), 'showHidden': False})
    report = {
        'classification': p['classification'],
        'parameter_sha256': hashlib.sha256(args.parameters.read_bytes()).hexdigest(),
        'all_component_shapes_valid': True, 'parts': rows,
        'assumed_structure_mass_kg': sum(r['assumed_structure_mass_kg'] for r in rows),
        'total_assembly_mass_kg': None,
        'excluded': ['UR5 adapter/flange', 'motors and gearboxes', 'bearings', 'fasteners',
                     'grippers', 'cables', 'guards', 'workpieces', 'shoulder-to-base brackets'],
        'design_gaps': ['No bolt pattern, bearing seats, gearbox interfaces or bracket details',
                        'Open-frame concept has no verified mounting load path',
                        'No stress, fatigue, stiffness or cable-routing validation'],
        'actuator_sizing_equation': 'tau_static = g*(payload*r_payload + sum(m_i*r_i)); add inertia, friction, gearing efficiency and duty margins',
        'static_torque_Nm': None, 'payload_compatibility': 'NOT_ESTABLISHED',
        'manufacturing_ready': False, 'physical_operation_verified': False,
    }
    (args.output / 'design_report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
