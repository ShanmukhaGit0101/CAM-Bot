"""Test display styling against changes to motion, collision or upstream links."""

from copy import deepcopy
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

from carrier_description.presentation_model import presentation_description


ROOT = Path(__file__).resolve().parents[3]
MODEL = ROOT / 'experiments/workspace/runs/model-study-20261107/model.urdf'


class TestPresentationModel(unittest.TestCase):
    def setUp(self):
        self.original = ET.fromstring(MODEL.read_text())
        self.styled = ET.fromstring(presentation_description(MODEL.read_text()))

    def canonical(self, element):
        return (element.tag, sorted(element.attrib.items()),
                (element.text or '').strip(), [self.canonical(c) for c in element])

    def test_motion_collision_and_inertial_model_are_identical(self):
        before, after = deepcopy(self.original), deepcopy(self.styled)
        for tree in (before, after):
            for link in tree.findall('link'):
                for visual in list(link.findall('visual')):
                    link.remove(visual)
        self.assertEqual(self.canonical(before), self.canonical(after))

    def test_upstream_ur5_visuals_are_identical(self):
        before = {link.get('name'): link for link in self.original.findall('link')}
        changed = {'carrier_flange', 'dual_arm_base_link', 'left_upper_arm',
                   'right_upper_arm', 'left_forearm', 'right_forearm'}
        for link in self.styled.findall('link'):
            if link.get('name') not in changed and not link.get('name').startswith('station_'):
                self.assertEqual(self.canonical(before[link.get('name')]),
                                 self.canonical(link))

    def test_arms_follow_original_segments_and_have_distinct_colours(self):
        links = {link.get('name'): link for link in self.styled.findall('link')}
        colours = []
        for side in ('left', 'right'):
            for part, length in (('upper_arm', .25), ('forearm', .22)):
                link = links[f'{side}_{part}']
                rod = link.find('visual')
                self.assertEqual(float(rod.find('geometry/cylinder').get('length')), length)
                self.assertEqual(rod.find('origin').get('xyz'), f'0 {length / 2} 0')
            colours.append(links[f'{side}_upper_arm'].find('visual/material/color').get('rgba'))
        self.assertNotEqual(*colours)

    def test_station_geometry_is_identical_with_only_translucency_changed(self):
        before = {link.get('name'): deepcopy(link) for link in self.original.findall('link')}
        for link in self.styled.findall('link'):
            if link.get('name').startswith('station_'):
                original = before[link.get('name')]
                for colour in original.findall('visual/material/color'):
                    rgb = colour.get('rgba').split()[:3]
                    colour.set('rgba', ' '.join(rgb + ['0.30']))
                self.assertEqual(self.canonical(original), self.canonical(link))

    def test_unknown_model_is_rejected(self):
        with self.assertRaises(ValueError):
            presentation_description('<robot name="other"/>')


if __name__ == '__main__':
    unittest.main()
