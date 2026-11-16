"""Exercise units, topology inventory and non-overwriting CLI behavior."""

import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import cadquery as cq

spec = importlib.util.spec_from_file_location('inspect_step', Path(__file__).with_name('inspect_step.py'))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class StepInspectionTests(unittest.TestCase):
    def test_cube_units_volume_and_no_fabricated_kinematics(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'cube.step'
            cq.exporters.export(cq.Workplane('XY').box(10, 20, 30), str(source))
            _, report = module.inspect(source)
            self.assertEqual(report['solid_count'], 1)
            self.assertTrue(report['whole_shape_valid'])
            self.assertAlmostEqual(report['solids'][0]['volume_mm3'], 6000)
            for observed, expected in zip(report['bbox_extent_m'], [0.01, 0.02, 0.03]):
                self.assertAlmostEqual(observed, expected, places=7)
            self.assertIsNone(report['mass_kg'])
            self.assertIsNone(report['joint_axes'])
            self.assertFalse(report['task_7_to_15_complete'])
            result = subprocess.run([sys.executable, module.__file__, str(source), tmp],
                                    capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(b'output must be a new directory', result.stderr)

    def test_missing_units_rejected_before_import(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'invalid.step'
            source.write_text('ISO-10303-21; END-ISO-10303-21;')
            with self.assertRaisesRegex(ValueError, 'millimetre'):
                module.inspect(source)


if __name__ == '__main__':
    unittest.main()
