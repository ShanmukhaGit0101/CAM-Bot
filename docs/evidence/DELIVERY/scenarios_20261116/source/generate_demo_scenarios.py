#!/usr/bin/env python3
"""Synthesize three assumed visual cells from retained UR5 forward kinematics."""

import argparse
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'src/carrier_control'))
from carrier_control.workflow import validate_plan  # noqa: E402
from carrier_control.workcell_model import target_world_xyz  # noqa: E402
from tools.analyze_workspace import Chain  # noqa: E402

MODEL = ROOT / 'experiments/workspace/runs/model-study-20261107/model.urdf'
SOURCE = ROOT / 'src/carrier_control/config/machine_tending.json'
SCENARIOS = {
    'compact': ('Compact shared workspace', 1,
                'Nearby station pairs reuse the carrier pose; local arms extend between them.'),
    'tiered': ('Stepped-height workcell', 2,
               'Five carrier poses and unequal-height stations require paired local pose changes.'),
    'precision': ('Precision transfer cell', 3,
                  'Rotated stations, alternating transfers and tighter geometric-proxy bounds.'),
}


def arm_pose(fold):
    """Synthesize symmetric wrist anchors 0.14 m apart in the mirrored assembly."""
    reach = .25 + .22 * math.cos(fold)
    shoulder = math.asin((.22 - .07) / reach)
    centre = np.array([0.0, math.sqrt(reach ** 2 - .15 ** 2), .05 + .22 * math.sin(fold)])
    hold = [-shoulder, -fold, shoulder, fold]  # swapped by the presentation wrapper
    opening = max(0.0, shoulder - .12)
    opened = [-opening, -fold, opening, fold]
    return centre, hold, opened


def generate(name):
    title, level, description = SCENARIOS[name]
    plan = json.loads(SOURCE.read_text())
    original = deepcopy(plan)
    chain = Chain(MODEL.read_text())
    names = list(plan['stations'])[1:]
    poses = [list(plan['stations'][key]['visual_carrier_joints']) for key in names]
    if name == 'compact':
        poses = [list(poses[i]) for i in (3, 3, 2, 4, 4)]
        folds = [1.35, .15, .9, 1.35, .15]
        yaws = [0, 0, .3, 0, 0]
        size = .14
    elif name == 'tiered':
        folds = [.3, .65, 1.1, .55, .9]
        yaws = [0, .25, 0, -.25, 0]
        size = .22
        for q, pan, lift in zip(poses, [.25, .6, .25, .2, -.3], [-.15, .22, -.12, .1, .12]):
            q[0] += pan
            q[1] += lift
    else:
        folds = [.45, .55, .65, .75, .85]
        yaws = [0, math.pi / 4, math.pi / 2, -math.pi / 4, math.pi]
        size = .18
        for q, pan, lift in zip(poses, [.3, .45, .2, -.35, .45], [.08, -.12, .1, .14, -.1]):
            q[0] += pan
            q[1] += lift
    pairs = {}
    for key, station, q, fold, yaw in zip(
            names, plan['workcell']['stations'].values(), poses, folds, yaws):
        local, hold, opened = arm_pose(fold)
        transform = chain.forward(q)[0]
        world = (transform @ np.append(local, 1))[:3]
        if not (.15 < world[2] < 1.45 and np.max(np.abs(world[:2])) < 1.4):
            raise ValueError(f'{name}/{key}: synthesized target outside display bounds: {world}')
        # Preserve a visible 6 cm clearance between the table top and cylinder centre.
        height = float(world[2] - .06)
        offset = [.025, -.02] if name == 'precision' else [0.0, 0.0]
        dx = math.cos(yaw) * offset[0] - math.sin(yaw) * offset[1]
        dy = math.sin(yaw) * offset[0] + math.cos(yaw) * offset[1]
        station['pose_xyz_m'] = [float(world[0] - dx), float(world[1] - dy), 0.0]
        station['pose_rpy_rad'] = [0.0, 0.0, yaw]
        station['size_xyz_m'] = [size, size, height]
        station['targets'] = {target: [*offset, height + .06] for target in station['targets']}
        plan['stations'][key]['visual_carrier_joints'] = q
        plan['stations'][key]['source'] = f'assumed {name} scenario synthesized by forward kinematics'
        plan['bimanual_poses'][key + '_HOLD'] = hold
        plan['bimanual_poses'][key + '_OPEN'] = opened
        pairs[key] = {'local_wrist_midpoint_m': local.tolist(), 'wrist_separation_m': .14,
                      'elbow_fold_rad': fold}
    # Keep HELD poses between stations; do not open/reset both arms on every transit.
    pose_for_step = {
        'S1_APPROACH': 'S1_RAW_OPEN', 'S1_GRASP': 'S1_RAW_HOLD',
        'S2_STAGE': 'S2_STAGING_HOLD', 'S3_LOAD': 'S3_MACHINE_HOLD',
        'S3_RELEASE': 'S3_MACHINE_OPEN', 'MACHINE_DWELL': 'S3_MACHINE_OPEN',
        'S3_REGRASP': 'S3_MACHINE_HOLD', 'S4_UNLOAD': 'S4_OUTPUT_HOLD',
        'S5_PLACE': 'S5_FINISHED_HOLD', 'S5_RELEASE': 'S5_FINISHED_OPEN',
    }
    for step in plan['workflow']:
        if step['name'] in pose_for_step:
            step['bimanual_pose'] = pose_for_step[step['name']]
    for side, sign in (('left', -1), ('right', 1)):
        plan['workspace'][side] = {
            'center_xyz_m': [sign * .22, 0.0, .05], 'max_radius_m': .60,
            'bounds_xyz_m': [[-.45, .02] if sign < 0 else [-.02, .45],
                             [.25, .50], [.05, .30]],
        }
        if name == 'precision':
            plan['workspace'][side]['bounds_xyz_m'] = [
                [-.45, .012] if sign < 0 else [-.012, .45], [.34, .45], [.13, .23]]
            plan['workspace'][side]['max_radius_m'] = .52
    plan['scenario'] = {
        'id': name, 'title': title, 'complexity_level': level, 'description': description,
        'geometry': 'assumed forward-synthesized layout, not measured geometry',
        'contact': 'symmetric wrist anchors only; tool contact/grasp unverified',
        'collision_checked': False, 'physical_operation_verified': False,
        'wrist_anchors': pairs,
        'source_config_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        'source_urdf_sha256': hashlib.sha256(MODEL.read_bytes()).hexdigest(),
    }
    # Controller inputs/flags are retained without promoting them to validated targets.
    for key in plan['stations']:
        assert plan['stations'][key]['carrier_joints'] == original['stations'][key]['carrier_joints']
        assert plan['stations'][key]['controller_validated'] == original['stations'][key]['controller_validated']
    validate_plan(plan)
    return plan


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(exist_ok=False, parents=True)
    for name in SCENARIOS:
        plan = generate(name)
        path = args.output / f'scenario_{name}.json'
        path.write_text(json.dumps(plan, indent=2) + '\n')
        heights = [s['size_xyz_m'][2] for s in plan['workcell']['stations'].values()]
        print(name, 'heights', [round(h, 3) for h in heights])


if __name__ == '__main__':
    main()
