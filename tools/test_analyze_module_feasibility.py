"""Independent geometric fixtures for the preliminary module diagnostics."""

from pathlib import Path
import tempfile
import unittest

import numpy as np

from tools.analyze_module_feasibility import Module, analyze, box_gap, clearance
from tools.analyze_workspace import ROOT, pose


class ModuleFeasibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = Module((ROOT / 'experiments/workspace/runs/model-study-20261107/model.urdf').read_text())

    def box(self, center, half=(1, 1, 1), rpy=(0, 0, 0)):
        return np.array(center, dtype=float), pose([0, 0, 0], rpy)[:3, :3], np.array(half)

    def test_separated_touching_and_overlapping_boxes(self):
        a = self.box([0, 0, 0])
        self.assertAlmostEqual(box_gap(a, self.box([3, 0, 0])), 1)
        self.assertAlmostEqual(box_gap(a, self.box([2, 0, 0])), 0)
        self.assertLess(box_gap(a, self.box([1, 0, 0])), 0)
        # SAT gap is a bound, not Euclidean distance for diagonal separation.
        self.assertAlmostEqual(box_gap(a, self.box([3, 3, 0])), 1)

    def test_rotated_box_and_rigid_transform_invariance(self):
        a = self.box([0, 0, 0], (1, .1, .1))
        b = self.box([0, 1, 0], (1, .1, .1), (0, 0, np.pi / 2))
        self.assertLess(box_gap(a, b), 0)
        transform = pose([5, -3, 1], [.2, -.7, 1.1])
        def moved(box):
            center, rotation, half = box
            return transform[:3, :3] @ center + transform[:3, 3], transform[:3, :3] @ rotation, half
        self.assertAlmostEqual(box_gap(a, b), box_gap(moved(a), moved(b)), places=12)

    def test_known_placeholder_endpoint(self):
        for arm, x in (('left', -.22), ('right', .22)):
            np.testing.assert_allclose(self.model.endpoint(arm, [0, 0])[:3, 3], [x, .47, .05])
            np.testing.assert_allclose(self.model.endpoint(arm, [0, 1])[:3, 3],
                                       [x, .25 + .22 * np.cos(1), .05 + .22 * np.sin(1)])

    def test_ik_recovers_pose_with_orientation(self):
        target = self.model.endpoint('left', [-.8, .9])
        result = self.model.inverse('left', target[:3, 3], target[:3, :3])
        self.assertEqual(result['status'], 'SOLUTION_FOUND')
        self.assertLess(result['position_error_m'], 1e-6)
        self.assertLess(result['orientation_error_rad'], 1e-6)
        np.testing.assert_allclose(result['joints_rad'], [-.8, .9], atol=1e-5)

    def test_incompatible_orientation_and_distant_point_fail(self):
        target = self.model.endpoint('right', [.3, .5])
        wrong = target[:3, :3] @ pose([0, 0, 0], [0, 0, np.pi])[:3, :3]
        self.assertEqual(self.model.inverse('right', target[:3, 3], wrong)['status'], 'NO_SOLUTION_FOUND')
        self.assertEqual(self.model.inverse('right', [10, 10, 10])['status'], 'NO_SOLUTION_FOUND')

    def test_rejects_invalid_ik_input_and_out_of_limits(self):
        for target in ([float('nan'), 0, 0], [1, 2]):
            with self.assertRaises(ValueError):
                self.model.inverse('left', target)
        with self.assertRaises(ValueError):
            self.model.inverse('left', [0, 0, 0], np.zeros((3, 3)))
        with self.assertRaises(ValueError):
            self.model.endpoint('left', [2, 0])
        with self.assertRaises(ValueError):
            self.model.inverse('left', [0, 0, 0], position_tolerance=0)

    def test_obstacle_and_self_collision_are_reported(self):
        boxes = self.model.boxes([0, 0, 0, 0], np.eye(4))
        check = clearance(boxes, {'obstacle': self.box([-.22, .3, .05], (.1, .1, .1))})
        self.assertTrue(any(p['second'] == 'obstacle' for p in check['pairs_below_margin']))
        # Opposed shoulders cross the two straight arms.
        crossed = self.model.boxes([-1, 0, 1, 0], np.eye(4))
        check = clearance(crossed, {})
        self.assertTrue(any('left' in p['first'] and 'right' in p['second']
                            for p in check['pairs_below_margin']))

    def test_unsupported_geometry_fails_closed(self):
        xml = (ROOT / 'experiments/workspace/runs/model-study-20261107/model.urdf').read_text()
        # Change every box: no silent skipping of unknown shapes.
        with self.assertRaises(ValueError):
            Module(xml.replace('<box ', '<mesh '))

    def test_refuses_overwriting_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            with self.assertRaises(FileExistsError):
                analyze(path, path, path, path)


if __name__ == '__main__':
    unittest.main()
