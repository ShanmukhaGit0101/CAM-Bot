"""Analytic mass/load fixtures and incomplete-input acceptance boundaries."""

import copy
import json
import math
from pathlib import Path
import tempfile
import unittest

import numpy as np

from tools.cad.assess_module_loads import G, REQUIRED_GROUPS, assess, mass_properties, run


class StaticLoadTests(unittest.TestCase):
    def inputs(self):
        return {'component_groups': {g: {'mass_kg': 0, 'center_of_mass_m': [0, 0, 0],
                                         'source': 'synthetic zero-mass test fixture only'} for g in REQUIRED_GROUPS},
                'module_pose_in_flange': {'translation_xyz_m': [0, 0, 0], 'rotation_rpy_rad': [0, 0, 0],
                                          'source': 'synthetic identity test fixture'},
                'carrier_limits': {'model': 'TEST_ONLY', 'mass_limit_kg': 5,
                                   'static_moment_limit_Nm': 50, 'source': 'test constants; not a UR rating'}}

    def structure(self):
        return [{'name': 'a', 'mass_kg': 2, 'center_of_mass_m': [1, 0, 0]},
                {'name': 'b', 'mass_kg': 1, 'center_of_mass_m': [-1, 0, 0]}]

    def test_analytic_mass_centre_and_gravity_envelope(self):
        result = mass_properties(self.structure())
        self.assertEqual(result['mass_kg'], 3)
        np.testing.assert_allclose(result['center_of_mass_m'], [1/3, 0, 0])
        self.assertAlmostEqual(result['max_static_gravity_moment_Nm'], G)
        self.assertAlmostEqual(result['static_gravity_force_N'], 3*G)

    def test_mount_rotation_translation_changes_flange_moment(self):
        inputs = self.inputs()
        inputs['module_pose_in_flange']['rotation_rpy_rad'] = [0, 0, math.pi/2]
        inputs['module_pose_in_flange']['translation_xyz_m'] = [0, 1, 0]
        result = assess(self.structure(), inputs)['known_subtotal_in_flange_frame']
        np.testing.assert_allclose(result['center_of_mass_m'], [0, 4/3, 0], atol=1e-14)
        self.assertAlmostEqual(result['max_static_gravity_moment_Nm'], 4*G)

    def test_unknown_mass_cannot_be_treated_as_zero(self):
        inputs = self.inputs()
        inputs['component_groups']['grippers']['mass_kg'] = None
        result = assess(self.structure(), inputs)
        self.assertEqual(result['status'], 'INCOMPLETE_INPUTS')
        self.assertIsNone(result['total_assembly_mass_kg'])
        self.assertIsNone(result['static_limit_comparison'])
        self.assertFalse(result['hardware_execution_authorized_by_this_report'])

    def test_provenance_and_mount_are_required(self):
        for kind in ('component', 'mount', 'limit'):
            inputs = self.inputs()
            if kind == 'component': inputs['component_groups']['workpieces']['source'] = ''
            if kind == 'mount': inputs['module_pose_in_flange'] = None
            if kind == 'limit': inputs['carrier_limits']['source'] = None
            with self.subTest(kind=kind):
                self.assertEqual(assess(self.structure(), inputs)['status'], 'INCOMPLETE_INPUTS')

    def test_fail_and_static_pass_do_not_authorize_hardware(self):
        inputs = self.inputs()
        self.assertEqual(assess(self.structure(), inputs)['status'],
                         'STATIC_SCREEN_PASS_REQUIRES_DYNAMIC_AND_PHYSICAL_VALIDATION')
        for key, value in [('mass_limit_kg', 2), ('static_moment_limit_Nm', G/2)]:
            fixture = copy.deepcopy(inputs)
            fixture['carrier_limits'][key] = value
            result = assess(self.structure(), fixture)
            self.assertEqual(result['status'], 'STATIC_SCREEN_FAIL')
            self.assertFalse(result['manufacturing_ready'])
            self.assertFalse(result['physical_operation_verified'])

    def test_nonfinite_negative_missing_groups_and_bad_transforms_rejected(self):
        for mass in (-1, float('nan'), float('inf'), True):
            inputs = self.inputs()
            inputs['component_groups']['adapter']['mass_kg'] = mass
            with self.subTest(mass=mass), self.assertRaises(ValueError):
                assess(self.structure(), inputs)
        inputs = self.inputs()
        del inputs['component_groups']['adapter']
        with self.assertRaises(ValueError): assess(self.structure(), inputs)
        inputs = self.inputs()
        inputs['module_pose_in_flange']['rotation_rpy_rad'] = [0, 0]
        with self.assertRaises(ValueError): assess(self.structure(), inputs)

    def test_current_unknown_template_retains_partial_result_and_units(self):
        root = Path(__file__).resolve().parents[2]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)/'new'
            run(root/'design/bimanual_concept/parameters.json',
                root/'design/bimanual_concept/load_inputs.template.json',output)
            report = json.loads((output/'static_loads.json').read_text())
            self.assertEqual(report['status'], 'INCOMPLETE_INPUTS')
            self.assertAlmostEqual(report['known_subtotal_in_module_frame']['mass_kg'],1.021657531828086)
            # Both arms extend along positive Y; symmetry cancels X only.
            cg = report['known_subtotal_in_module_frame']['center_of_mass_m']
            self.assertAlmostEqual(cg[0],0,places=12)
            self.assertGreater(cg[1],0.1)
            self.assertLess(cg[1],0.47)
            self.assertIsNone(report['known_subtotal_in_flange_frame'])
            with self.assertRaises(FileExistsError): run(Path('missing'),Path('missing'),output)


if __name__ == '__main__':
    unittest.main()
