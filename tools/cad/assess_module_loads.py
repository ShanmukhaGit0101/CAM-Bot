#!/usr/bin/env python3
"""Screen a single concept pose's static loads; never approve hardware use."""

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

import numpy as np

# Support both direct CLI use and unittest/package imports.
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.cad.build_module_concept import build  # noqa: E402


REQUIRED_GROUPS = (
    'adapter', 'shoulder_brackets', 'actuators_and_gearboxes',
    'bearings_and_fasteners', 'grippers', 'cables_and_guards', 'workpieces',
)
G = 9.80665


def scalar(value, name, positive=False):
    if (isinstance(value, bool) or not isinstance(value, (int, float)) or
            not math.isfinite(value) or value < 0 or (positive and value == 0)):
        raise ValueError(f'{name} must be finite and {"positive" if positive else "nonnegative"}')
    return float(value)


def vector(value, name):
    if (not isinstance(value, list) or len(value) != 3 or
            any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v)
                for v in value)):
        raise ValueError(f'{name} must be three finite numbers')
    return np.asarray(value, dtype=float)


def rotation(rpy):
    r, p, y = vector(rpy, 'rotation_rpy_rad')
    cr, sr, cp, sp, cy, sy = math.cos(r), math.sin(r), math.cos(p), math.sin(p), math.cos(y), math.sin(y)
    return np.array([[cy*cp, cy*sp*sr-sy*cr, cy*sp*cr+sy*sr],
                     [sy*cp, sy*sp*sr+cy*cr, sy*sp*cr-cy*sr],
                     [-sp, cp*sr, cp*cr]])


def mass_properties(components):
    masses = np.asarray([scalar(c['mass_kg'], 'mass_kg') for c in components])
    centers = np.asarray([vector(c['center_of_mass_m'], 'center_of_mass_m') for c in components])
    total = float(masses.sum())
    if total <= 0:
        raise ValueError('known mass must be positive')
    first_moment = (masses[:, None] * centers).sum(axis=0)
    return {'mass_kg': total, 'center_of_mass_m': (first_moment / total).tolist(),
            'first_moment_kg_m': first_moment.tolist(),
            # max over all gravity directions for this fixed geometry.
            'max_static_gravity_moment_Nm': float(G * np.linalg.norm(first_moment)),
            'static_gravity_force_N': G * total}


def assess(structure, inputs):
    """Keep partial known totals distinct from fully specified static screens."""
    unknown = []
    known = []
    if not structure or len({c['name'] for c in structure}) != len(structure):
        raise ValueError('structure must have uniquely named components')
    for item in structure:
        scalar(item['mass_kg'], item['name'])
        vector(item['center_of_mass_m'], item['name'])
        known.append(item)
    extras = inputs['component_groups']
    if set(extras) != set(REQUIRED_GROUPS):
        raise ValueError('component_groups must contain every required group exactly once')
    for group in REQUIRED_GROUPS:
        item = extras[group]
        # Malformed supplied values are errors even if another field is unknown.
        if item['mass_kg'] is not None:
            scalar(item['mass_kg'], group)
        if item['center_of_mass_m'] is not None:
            vector(item['center_of_mass_m'], group)
        source = item.get('source')
        if (item['mass_kg'] is None or item['center_of_mass_m'] is None or
                not isinstance(source, str) or not source.strip()):
            unknown.append(f'component_groups.{group}: mass, centre and provenance required')
        else:
            known.append({'name': group, 'mass_kg': item['mass_kg'],
                          'center_of_mass_m': item['center_of_mass_m']})
    module = mass_properties(known)
    mount = inputs['module_pose_in_flange']
    flange = None
    if mount is None:
        unknown.append('module_pose_in_flange')
    else:
        xyz = vector(mount['translation_xyz_m'], 'translation_xyz_m')
        rot = rotation(mount['rotation_rpy_rad'])
        if not isinstance(mount.get('source'), str) or not mount['source'].strip():
            unknown.append('module_pose_in_flange.source')
        else:
            flange = mass_properties([
                {**item, 'center_of_mass_m': (xyz + rot @ np.asarray(item['center_of_mass_m'])).tolist()}
                for item in known])
    robot = inputs['carrier_limits']
    limits_ready = True
    for key in ('model', 'source'):
        if not isinstance(robot.get(key), str) or not robot[key].strip():
            unknown.append('carrier_limits.' + key)
            limits_ready = False
    for key in ('mass_limit_kg', 'static_moment_limit_Nm'):
        if robot[key] is None:
            unknown.append('carrier_limits.' + key)
            limits_ready = False
        else:
            scalar(robot[key], key, positive=True)
    complete_mass = not any(u.startswith('component_groups.') for u in unknown)
    criteria = None
    if not unknown and flange is not None and limits_ready:
        criteria = {
            'mass_limit_kg': robot['mass_limit_kg'],
            'mass_margin_kg': robot['mass_limit_kg'] - flange['mass_kg'],
            'static_moment_limit_Nm': robot['static_moment_limit_Nm'],
            'static_moment_margin_Nm': robot['static_moment_limit_Nm'] - flange['max_static_gravity_moment_Nm'],
        }
    status = ('INCOMPLETE_INPUTS' if criteria is None else
              'STATIC_SCREEN_FAIL' if min(criteria['mass_margin_kg'], criteria['static_moment_margin_Nm']) < 0 else
              'STATIC_SCREEN_PASS_REQUIRES_DYNAMIC_AND_PHYSICAL_VALIDATION')
    return {
        'classification': 'SINGLE_POSE_STATIC_CONCEPT_SCREEN', 'status': status,
        'pose': 'concept zero pose; all component centres expressed in module frame',
        'gravity_m_s2': G, 'known_components': known,
        'known_subtotal_in_module_frame': module,
        'known_subtotal_in_flange_frame': flange,
        'total_assembly_mass_kg': module['mass_kg'] if complete_mass else None,
        'unknown_inputs': unknown, 'static_limit_comparison': criteria,
        'actual_actuator_torque_ratings_Nm': None,
        'limitations': [
            'structural mass uses an assumed density; not measured or supplier-certified',
            'fixed pose only: other joint configurations and carried-object positions can change centre of gravity',
            'maximum gravity moment varies gravity direction only, not geometry',
            'scalar supplied limits do not replace the manufacturer coupled payload/CoG/inertia envelope',
            'no inertial acceleration, impact, gearbox/friction, fatigue or duty-cycle calculation',
            'no bracket/fastener stress, deflection, cable or mounting-load-path qualification',
        ],
        'physical_operation_verified': False, 'manufacturing_ready': False,
        'hardware_execution_authorized_by_this_report': False,
    }


def run(parameters, inputs_path, output):
    if output.exists():
        raise FileExistsError(f'refusing to overwrite {output}')
    parameters_data = json.loads(parameters.read_text())
    parts = build(parameters_data)
    structure = []
    for name, shape in parts.items():
        if not shape.isValid():
            raise ValueError('invalid concept solid: ' + name)
        center = shape.Center()
        structure.append({'name': name,
                          'mass_kg': shape.Volume() * 1e-9 * parameters_data['assumed_structure_density_kg_m3'],
                          'center_of_mass_m': [center.x/1000, center.y/1000, center.z/1000]})
    report = assess(structure, json.loads(inputs_path.read_text()))
    report['input_sha256'] = {str(p): hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in (parameters, inputs_path, Path(__file__), Path(__file__).with_name('build_module_concept.py'))}
    output.mkdir(parents=True, exist_ok=False)
    (output / 'static_loads.json').write_text(json.dumps(report, indent=2, allow_nan=False) + '\n')
    print(json.dumps({key: report[key] for key in ('status', 'known_subtotal_in_module_frame', 'unknown_inputs')}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('parameters', type=Path)
    parser.add_argument('inputs', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    run(args.parameters, args.inputs, args.output)
