"""Check concept validity and finite positive structural mass, not hardware safety."""

import importlib.util
import json
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('concept', Path(__file__).with_name('build_module_concept.py'))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ConceptTests(unittest.TestCase):
    def parameters(self):
        return json.loads((Path(__file__).resolve().parents[2] /
                           'design/bimanual_concept/parameters.json').read_text())

    def test_valid_parts_and_symmetric_link_volumes(self):
        p = self.parameters()
        shapes = module.build(p)
        self.assertEqual(len(shapes), 7)
        self.assertTrue(all(s.isValid() and s.Volume() > 0 for s in shapes.values()))
        for link in ['upper', 'forearm', 'shoulder_envelope']:
            self.assertAlmostEqual(shapes['left_' + link].Volume(),
                                   shapes['right_' + link].Volume())
        expected_base = (p['base_length']*p['base_width'] -
                         (p['base_length']-2*p['base_border'])*
                         (p['base_width']-2*p['base_border']))*p['base_thickness']
        self.assertAlmostEqual(shapes['base_frame'].Volume(), expected_base)

    def test_impossible_wall_and_nonfinite_dimension_rejected(self):
        p = self.parameters()
        p['wall'] = 100
        with self.assertRaises(ValueError):
            module.build(p)
        p = self.parameters()
        p['upper_length'] = float('nan')
        with self.assertRaises(ValueError):
            module.build(p)


if __name__ == '__main__':
    unittest.main()
