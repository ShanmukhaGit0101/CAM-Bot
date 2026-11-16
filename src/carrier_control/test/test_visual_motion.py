"""Angular winding, model limits and side-exchange regression fixtures."""

import json
import math
from pathlib import Path
import unittest

from carrier_control.visual_motion import (
    nearest_visual_route, swapped_arm_plan, UR5_VISUAL_LIMITS,
)


CONFIG = Path(__file__).parents[1] / 'config/machine_tending.json'


class TestVisualMotion(unittest.TestCase):
    def test_ninety_degree_turn_avoids_two_hundred_seventy_degree_route(self):
        _, goal = nearest_visual_route([0.0], [math.radians(270)], [(-math.tau, math.tau)])
        self.assertAlmostEqual(goal[0], -math.pi / 2)
        _, backward = nearest_visual_route([0.0], [math.radians(-270)],
                                           [(-math.tau, math.tau)])
        self.assertAlmostEqual(backward[0], math.pi / 2)

    def test_signed_wrap_boundary_is_continuous_and_goal_is_equivalent(self):
        goal = nearest_visual_route([math.radians(179)], [math.radians(-179)],
                                    [(-math.tau, math.tau)])[1][0]
        self.assertAlmostEqual(math.degrees(goal), 181)
        self.assertAlmostEqual(math.sin(goal), math.sin(math.radians(-179)))
        self.assertAlmostEqual(math.cos(goal), math.cos(math.radians(-179)))

    def test_limits_can_require_the_long_route(self):
        goal = nearest_visual_route([math.radians(179)], [math.radians(-179)],
                                    [(-math.pi, math.pi)])[1][0]
        self.assertAlmostEqual(math.degrees(goal), -179)

    def test_actual_workflow_uses_nearest_valid_representations(self):
        plan = json.loads(CONFIG.read_text())
        current = list(plan['stations']['HOME']['visual_carrier_joints'])
        for step in plan['workflow']:
            if not step.get('station'):
                continue
            configured = plan['stations'][step['station']]['visual_carrier_joints']
            rebased, selected = nearest_visual_route(current, configured)
            for start, end, target, (lower, upper) in zip(
                    rebased, selected, configured, UR5_VISUAL_LIMITS):
                self.assertTrue(lower <= end <= upper)
                self.assertLessEqual(abs(end - start), abs(target - start) + 1e-12)
                self.assertAlmostEqual(math.cos(end), math.cos(target))
                self.assertAlmostEqual(math.sin(end), math.sin(target))
                for turns in (-2, -1, 0, 1, 2):
                    alternative = target + turns * math.tau
                    if lower <= alternative <= upper:
                        self.assertLessEqual(abs(end - start), abs(alternative - start) + 1e-12)
            self.assertLessEqual(abs(selected[0] - rebased[0]), math.pi + 1e-12)
            for a, b in zip(current, rebased):
                self.assertAlmostEqual(math.sin(a), math.sin(b))
                self.assertAlmostEqual(math.cos(a), math.cos(b))
            current = selected

    def test_nonfinite_outside_limits_and_mismatched_vectors_are_rejected(self):
        for start, goal, limits in (([0], [float('nan')], [(-1, 1)]),
                                    ([2], [0], [(-1, 1)]), ([0], [2], [(-1, 1)]),
                                    ([0], [], [(-1, 1)])):
            with self.assertRaises(ValueError):
                nearest_visual_route(start, goal, limits)

    def test_side_exchange_keeps_original_plan_and_controller_targets(self):
        plan = json.loads(CONFIG.read_text())
        original = json.dumps(plan, sort_keys=True)
        swapped = swapped_arm_plan(plan)
        self.assertEqual(original, json.dumps(plan, sort_keys=True))
        self.assertEqual(swapped['workspace']['left'], plan['workspace']['right'])
        self.assertEqual(swapped['workspace']['right'], plan['workspace']['left'])
        self.assertEqual(swapped['stations'], plan['stations'])
        for name, pose in plan['bimanual_poses'].items():
            self.assertEqual(swapped['bimanual_poses'][name], pose[2:] + pose[:2])
        with self.assertRaises(ValueError):
            swapped_arm_plan(swapped)


if __name__ == '__main__':
    unittest.main()
