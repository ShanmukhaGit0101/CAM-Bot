"""Independent layout, proxy-reuse and actual two-arm FK scenario checks."""

import json
import math
import unittest

import numpy as np

from tools.generate_demo_scenarios import generate, MODEL, SOURCE
from tools.analyze_workspace import Chain, proxy_margins
from carrier_control.visual_motion import swapped_arm_plan
from carrier_control.workcell_model import target_world_xyz
from carrier_control.workflow import WorkflowError, validate_plan
from carrier_description.presentation_model import reverse_arm_mounts


class ScenarioTests(unittest.TestCase):
    def test_regeneration_matches_committed_configs_and_preserves_default(self):
        before = SOURCE.read_bytes()
        for name in ('compact', 'tiered', 'precision'):
            stored = json.loads((SOURCE.parent / f'scenario_{name}.json').read_text())
            self.assertEqual(generate(name), stored)
            with self.assertRaises(WorkflowError):
                validate_plan(stored, require_controller_ready=True)
        self.assertEqual(before, SOURCE.read_bytes())

    def test_actual_mirrored_wrist_midpoints_match_generated_targets(self):
        xml = reverse_arm_mounts(MODEL.read_text())
        left = Chain(xml, root='dual_arm_base_link', tip='left_forearm')
        right = Chain(xml, root='dual_arm_base_link', tip='right_forearm')
        for name in ('compact', 'tiered', 'precision'):
            plan = swapped_arm_plan(generate(name))
            for station, spec in plan['scenario']['wrist_anchors'].items():
                q = plan['bimanual_poses'][station + '_HOLD']
                endpoints = [(chain.forward(values)[0] @ np.array([0, .22, 0, 1]))[:3]
                             for chain, values in ((left, q[:2]), (right, q[2:]))]
                np.testing.assert_allclose(np.mean(endpoints, axis=0),
                                           spec['local_wrist_midpoint_m'], atol=1e-12)
                self.assertAlmostEqual(np.linalg.norm(endpoints[0] - endpoints[1]), .14)

    def test_live_proxy_policy_requires_three_then_five_then_five_moves(self):
        chain = Chain(MODEL.read_text())
        for name, expected in (('compact', 3), ('tiered', 5), ('precision', 5)):
            plan = generate(name)
            q = plan['stations']['HOME']['visual_carrier_joints']
            count = 0
            for step in plan['workflow']:
                if not step.get('target'):
                    continue
                xyz = target_world_xyz(plan['workcell'], step['target'])
                if proxy_margins(xyz, chain.forward(q), plan['workspace'])[0] < 0:
                    self.assertIsNotNone(step['station'])
                    q = plan['stations'][step['station']]['visual_carrier_joints']
                    count += 1
                self.assertGreaterEqual(proxy_margins(xyz, chain.forward(q),
                                                     plan['workspace'])[0], 0)
            self.assertEqual(count, expected)

    def test_station_rectangles_do_not_overlap(self):
        for name in ('compact', 'tiered', 'precision'):
            stations = list(generate(name)['workcell']['stations'].values())
            for index, a in enumerate(stations):
                for b in stations[index + 1:]:
                    def axes(s):
                        yaw = s['pose_rpy_rad'][2]
                        return np.array([[math.cos(yaw), math.sin(yaw)],
                                         [-math.sin(yaw), math.cos(yaw)]])
                    aa, bb = axes(a), axes(b)
                    delta = np.array(b['pose_xyz_m'][:2]) - a['pose_xyz_m'][:2]
                    gaps = []
                    for axis in np.vstack((aa, bb)):
                        radii = sum(abs(aa @ axis) * np.array(a['size_xyz_m'][:2]) / 2)
                        radii += sum(abs(bb @ axis) * np.array(b['size_xyz_m'][:2]) / 2)
                        gaps.append(abs(delta @ axis) - radii)
                    self.assertGreater(max(gaps), 0, (name, index))

    def test_complexity_levels_have_distinct_layouts_and_tighter_final_proxy(self):
        plans = [generate(n) for n in ('compact', 'tiered', 'precision')]
        self.assertEqual([p['scenario']['complexity_level'] for p in plans], [1, 2, 3])
        self.assertEqual(len({json.dumps(p['workcell']) for p in plans}), 3)
        for side in ('left', 'right'):
            widths = [np.prod([hi - lo for lo, hi in p['workspace'][side]['bounds_xyz_m']])
                      for p in plans]
            self.assertLess(widths[-1], widths[-2])


if __name__ == '__main__':
    unittest.main()
