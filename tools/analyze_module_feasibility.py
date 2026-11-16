#!/usr/bin/env python3
"""Offline placeholder IK and box-clearance diagnostics; never a motion planner."""

import argparse
import hashlib
import itertools
import json
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET

import numpy as np
import scipy
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation

from tools.analyze_workspace import Chain, ROOT, pose
from carrier_control.workcell_model import target_world_xyz


MODULE_LINKS = ('dual_arm_base_link', 'left_upper_arm', 'left_forearm',
                'right_upper_arm', 'right_forearm')
ARM_NAMES = ('left', 'right')
ADJACENT = {frozenset(pair) for pair in (
    ('dual_arm_base_link', 'left_upper_arm'),
    ('dual_arm_base_link', 'right_upper_arm'),
    ('left_upper_arm', 'left_forearm'), ('right_upper_arm', 'right_forearm'))}


def box_gap(a, b):
    """Signed SAT projection gap; positive is a lower bound on box distance.

    Zero/negative means touching/overlap. Negative magnitude is NOT penetration
    depth. The 15 separating axes cover oriented boxes, not arbitrary meshes.
    """
    ca, ra, ha = a
    cb, rb, hb = b
    axes = [*ra.T, *rb.T, *(np.cross(x, y) for x in ra.T for y in rb.T)]
    gaps = []
    for axis in axes:
        length = np.linalg.norm(axis)
        if length < 1e-10:
            continue
        axis = axis / length
        gaps.append(abs(np.dot(cb - ca, axis)) -
                    np.dot(ha, np.abs(ra.T @ axis)) -
                    np.dot(hb, np.abs(rb.T @ axis)))
    return float(max(gaps))


def xyz_attr(node, key, default='0 0 0'):
    return [float(v) for v in (default if node is None else node.get(key, default)).split()]


class Module:
    """Use the existing expanded URDF; tool points are forearm box ends only."""

    def __init__(self, xml):
        robot = ET.fromstring(xml)
        self.chains = {link: Chain(xml, root='dual_arm_base_link', tip=link)
                       for link in MODULE_LINKS if link != 'dual_arm_base_link'}
        self.geometry = {}
        for link in MODULE_LINKS:
            collisions = robot.findall(f"link[@name='{link}']/collision")
            if len(collisions) != 1:
                raise ValueError(f'{link}: expected exactly one collision box')
            collision = collisions[0]
            box = collision.find('geometry/box')
            if box is None:
                raise ValueError(f'{link}: only box geometry supported')
            size = np.array(xyz_attr(box, 'size'))
            if size.shape != (3,) or not np.isfinite(size).all() or np.any(size <= 0):
                raise ValueError('invalid collision box')
            origin = collision.find('origin')
            transform = pose(xyz_attr(origin, 'xyz'), xyz_attr(origin, 'rpy'))
            self.geometry[link] = (transform, size / 2)
        self.tips = {}
        for arm in ARM_NAMES:
            transform, half = self.geometry[f'{arm}_forearm']
            # This is the distal centre of the box, not an actual gripper TCP.
            offset = np.eye(4)
            offset[:3, 3] = [0, half[1], 0]
            self.tips[arm] = transform @ offset

    def endpoint(self, arm, q):
        return self.chains[f'{arm}_forearm'].forward(q)[0] @ self.tips[arm]

    def inverse(self, arm, target, orientation=None, position_tolerance=0.001,
                angular_tolerance=0.01):
        """Bounded multistart IK; failure is not proof of global infeasibility."""
        target = np.asarray(target, dtype=float)
        if target.shape != (3,) or not np.isfinite(target).all():
            raise ValueError('target must be a finite position triple')
        if (not np.isfinite([position_tolerance, angular_tolerance]).all() or
                min(position_tolerance, angular_tolerance) <= 0):
            raise ValueError('tolerances must be positive and finite')
        if orientation is not None:
            orientation = np.asarray(orientation, dtype=float)
            if (orientation.shape != (3, 3) or not np.isfinite(orientation).all() or
                    not np.allclose(orientation.T @ orientation, np.eye(3), atol=1e-9) or
                    not np.isclose(np.linalg.det(orientation), 1, atol=1e-9)):
                raise ValueError('orientation must be a proper rotation')
        chain = self.chains[f'{arm}_forearm']

        def errors(q):
            tip = self.endpoint(arm, q)
            delta = tip[:3, 3] - target
            angular = (Rotation.from_matrix(orientation.T @ tip[:3, :3]).as_rotvec()
                       if orientation is not None else np.empty(0))
            return delta, angular

        def objective(q):
            delta, angular = errors(q)
            return np.r_[delta / position_tolerance, angular / angular_tolerance]

        best = None
        grids = [np.linspace(lo + 1e-8, hi - 1e-8, 3) for lo, hi in chain.limits]
        for seed in itertools.product(*grids):
            result = least_squares(objective, seed, bounds=chain.limits.T,
                                   max_nfev=100, ftol=1e-10, xtol=1e-10, gtol=1e-10)
            if best is None or np.linalg.norm(result.fun) < np.linalg.norm(best.fun):
                best = result
            delta, angular = errors(best.x)
            if np.linalg.norm(delta) <= position_tolerance and np.linalg.norm(angular) <= angular_tolerance:
                break
        delta, angular = errors(best.x)
        accepted = (np.linalg.norm(delta) <= position_tolerance and
                    np.linalg.norm(angular) <= angular_tolerance)
        return {'status': 'SOLUTION_FOUND' if accepted else 'NO_SOLUTION_FOUND',
                'joints_rad': best.x.tolist(), 'joint_names': chain.names,
                'position_error_m': float(np.linalg.norm(delta)),
                'orientation_required': orientation is not None,
                'orientation_error_rad': float(np.linalg.norm(angular)) if orientation is not None else None}

    def boxes(self, q, base):
        if np.shape(q) != (4,) or not np.isfinite(q).all():
            raise ValueError('expected four finite module joints')
        result = {}
        for link in MODULE_LINKS:
            transform = base.copy()
            if link != 'dual_arm_base_link':
                arm_q = q[:2] if link.startswith('left') else q[2:]
                chain = self.chains[link]
                transform = transform @ chain.forward(arm_q[:len(chain.names)])[0]
            origin, half = self.geometry[link]
            transform = transform @ origin
            result[link] = (transform[:3, 3], transform[:3, :3], half)
        return result


def station_boxes(plan):
    boxes = {}
    for name, station in plan['workcell']['stations'].items():
        half = np.asarray(station['size_xyz_m']) / 2
        transform = pose(station['pose_xyz_m'], station['pose_rpy_rad'])
        center = transform[:3, 3] + transform[:3, :3] @ [0, 0, half[2]]
        boxes[name] = (center, transform[:3, :3], half)
    return boxes


def clearance(boxes, obstacles, margin=0.005):
    pairs = [(a, b, box_gap(boxes[a], boxes[b]))
             for a, b in itertools.combinations(boxes, 2)
             if frozenset((a, b)) not in ADJACENT]
    pairs += [(a, b, box_gap(box, obstacle)) for a, box in boxes.items()
              for b, obstacle in obstacles.items()]
    return {'minimum_sat_gap_m': min(row[2] for row in pairs),
            'pairs_below_margin': [{'first': a, 'second': b, 'sat_gap_m': gap}
                                   for a, b, gap in pairs if gap < margin],
            'required_margin_m': margin}


def analyze(urdf, config, placements, output, samples=2000, seed=15):
    if output.exists():
        raise FileExistsError(f'refusing existing output: {output}')
    if samples < 1:
        raise ValueError('samples must be positive')
    xml = urdf.read_text()
    module, carrier = Module(xml), Chain(xml)
    plan = json.loads(config.read_text())
    positions = json.loads(placements.read_text())
    obstacles = station_boxes(plan)
    targets = {name: target_world_xyz(plan['workcell'], name)
               for station in plan['workcell']['stations'].values() for name in station['targets']}
    comparisons = []
    for candidate in positions:
        placement = pose(candidate['xyz_m'], candidate['rpy_rad'])
        rows = []
        for station_name, station in plan['stations'].items():
            if not station.get('workcell_station_id'):
                continue
            base = placement @ carrier.forward(station['visual_carrier_joints'])[0]
            for target_name in plan['workcell']['stations'][station['workcell_station_id']]['targets']:
                local = base[:3, :3].T @ (np.asarray(targets[target_name]) - base[:3, 3])
                solutions = {arm: module.inverse(arm, local) for arm in ARM_NAMES}
                q = [v for arm in ARM_NAMES for v in solutions[arm]['joints_rad']]
                rows.append({'station': station_name, 'target': target_name,
                             'target_in_module_m': local.tolist(), 'inverse': solutions,
                             'clearance_at_best_fit': clearance(module.boxes(q, base), obstacles),
                             'both_endpoints_within_1mm': all(
                                 s['status'] == 'SOLUTION_FOUND' for s in solutions.values())})
        comparisons.append({'placement': candidate, 'targets': rows,
                            'both_endpoint_matches': sum(row['both_endpoints_within_1mm'] for row in rows)})
    # Inspect actual visual waypoint transitions, not an invented collision-free path.
    previous_carrier = np.array(plan['stations']['HOME']['visual_carrier_joints'])
    previous_module = np.array(plan['bimanual_poses']['HOME'])
    segments = []
    for step in plan['workflow']:
        destination = (np.array(plan['stations'][step['station']]['visual_carrier_joints'])
                       if step['station'] else previous_carrier)
        module_destination = np.array(plan['bimanual_poses'][step['bimanual_pose']])
        count = max(2, int(np.ceil(max(np.max(np.abs(destination - previous_carrier)),
                                     np.max(np.abs(module_destination - previous_module))) / 0.05)) + 1)
        minimum, violations, first = float('inf'), 0, None
        for fraction in np.linspace(0, 1, count):
            q = previous_module + fraction * (module_destination - previous_module)
            base = carrier.forward(previous_carrier + fraction * (destination - previous_carrier))[0]
            check = clearance(module.boxes(q, base), obstacles)
            minimum = min(minimum, check['minimum_sat_gap_m'])
            if check['pairs_below_margin']:
                violations += 1
                if first is None:
                    first = {'fraction': float(fraction), **check}
        segments.append({'step': step['name'], 'samples': count, 'samples_below_margin': violations,
                         'minimum_sampled_sat_gap_m': minimum, 'first_violation': first})
        previous_carrier, previous_module = destination, module_destination
    # Sample simultaneous local joints; preserve both endpoint positions and gaps.
    rng = np.random.default_rng(seed)
    limits = np.vstack([module.chains[f'{arm}_forearm'].limits for arm in ARM_NAMES])
    cloud = []
    for q in rng.uniform(limits[:, 0], limits[:, 1], (samples, 4)):
        check = clearance(module.boxes(q, np.eye(4)), {})
        cloud.append([*q, *module.endpoint('left', q[:2])[:3, 3],
                      *module.endpoint('right', q[2:])[:3, 3], check['minimum_sat_gap_m']])
    output.mkdir(parents=True)
    np.savetxt(output / 'local_joint_samples.csv', cloud, delimiter=',',
               header='left_shoulder,left_elbow,right_shoulder,right_elbow,left_x,left_y,left_z,right_x,right_y,right_z,self_sat_gap_m', comments='')
    report = {
        'classification': 'ASSUMED_PLACEHOLDER_DIAGNOSTIC_NOT_MOTION_APPROVAL',
        'source_commit': subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip(),
        'source_status': subprocess.check_output(['git', '-C', str(ROOT), 'status', '--short'], text=True),
        'input_sha256': {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in (urdf, config, placements, Path(__file__))},
        'versions': {'python': sys.version, 'numpy': np.__version__, 'scipy': scipy.__version__},
        'position_tolerance_m': 0.001, 'required_box_margin_m': 0.005,
        'orientation_requirements_available': False, 'continuous_collision_checked': False,
        'carrier_collision_checked': False, 'gripper_collision_checked': False,
        'actuation_verified': False, 'grasp_verified': False, 'physical_placement_recommendation': None,
        'collision_scope': 'existing module boxes vs nonadjacent module boxes and solid station boxes; excludes UR5, flange, tools, cables and workpieces',
        'ik_scope': 'bounded numerical IK to distal forearm centres; common target is a proxy diagnostic, not a specified two-contact grasp',
        'path_scope': 'straight simultaneous joint interpolation at <=0.05 rad increments; sampled only, not the live timing law',
        'placements': comparisons, 'visual_path_segments': segments,
        'local_workspace': {'samples': samples, 'seed': seed,
                            'self_clearance_at_least_5mm': sum(row[-1] >= 0.005 for row in cloud),
                            'measured_boundary_uncertainty_m': None},
    }
    (output / 'report.json').write_text(json.dumps(report, indent=2, allow_nan=False) + '\n')
    print(json.dumps({'matches_by_placement': {p['placement']['name']: p['both_endpoint_matches'] for p in comparisons},
                      'path_segments_with_clearance_violations': sum(s['samples_below_margin'] > 0 for s in segments),
                      'local_workspace': report['local_workspace']}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--urdf', type=Path, required=True)
    parser.add_argument('--config', type=Path, default=ROOT / 'src/carrier_control/config/machine_tending.json')
    parser.add_argument('--placements', type=Path, default=ROOT / 'experiments/workspace/placements.json')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--samples', type=int, default=2000)
    parser.add_argument('--seed', type=int, default=15)
    args = parser.parse_args()
    analyze(args.urdf, args.config, args.placements, args.output, args.samples, args.seed)
