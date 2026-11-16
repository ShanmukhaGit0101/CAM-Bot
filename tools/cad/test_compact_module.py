"""Verify original geometry, interface alignment, hinge clearance and export."""

import json
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

import numpy as np
import cadquery as cq

from tools.cad.build_compact_module import build, export_kinematic_model
from tools.analyze_workspace import Chain
from tools.cad.check_compact_motion import solid_clearance_mm


class CompactModuleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p=json.loads((Path(__file__).resolve().parents[2]/'design/compact_module/requirements.json').read_text())
        cls.parts,cls.mount,cls.pedestal=build(cls.p)

    def test_single_valid_solids_and_pedestals_touch_base(self):
        self.assertEqual(len(self.parts),14)
        for name,shape in self.parts.items():
            with self.subTest(part=name):
                self.assertTrue(shape.isValid())
                self.assertEqual(len(shape.Solids()),1)
                self.assertGreater(shape.Volume(),0)
        for side in ('left','right'):
            self.assertLess(self.parts[side+'_pedestal'].distance(self.parts['base_plate']),1e-6)
            self.assertLess(self.parts[side+'_pedestal'].intersect(self.parts['base_plate']).Volume(),1e-6)

    def test_mount_holes_align_and_remove_expected_volume(self):
        p=self.p
        for x,y in self.mount:
            self.assertAlmostEqual(np.hypot(x,y),p['mount_hole_pcd']/2)
        holes=4*np.pi*(p['mount_hole_diameter']/2)**2+8*np.pi*(p['fastener_hole_diameter']/2)**2
        expected=(p['base_length']*p['base_width']-holes)*p['base_thickness']
        self.assertAlmostEqual(self.parts['base_plate'].Volume(),expected,places=5)
        disc=(np.pi*(p['mount_disc_diameter']/2)**2-4*np.pi*(p['mount_hole_diameter']/2)**2)*p['mount_disc_thickness']
        self.assertAlmostEqual(self.parts['mount_disc'].Volume(),disc,places=5)

    def test_elbow_fork_does_not_intersect_forearm_at_sampled_angles(self):
        p=self.p
        for side,sign in [('left',-1),('right',1)]:
            pivot=(sign*p['shoulder_offset_x'],p['upper_length'],p['joint_axis_height'])
            end=(pivot[0]+1,pivot[1],pivot[2])
            for degrees in (-68.75,-45,0,45,68.75):
                moving=self.parts[side+'_forearm'].rotate(pivot,end,degrees)
                with self.subTest(side=side,degrees=degrees):
                    self.assertLess(moving.intersect(self.parts[side+'_upper']).Volume(),1e-5)

    def test_standalone_urdf_local_meshes_and_fk(self):
        with tempfile.TemporaryDirectory() as directory:
            output=Path(directory)
            export_kinematic_model(self.parts,self.p,output)
            xml=(output/'compact_module.urdf').read_text()
            robot=ET.fromstring(xml)
            self.assertEqual(len(robot.findall('joint[@type="revolute"]')),4)
            self.assertEqual(robot.findall('ros2_control'),[])
            for mesh in robot.findall('.//mesh'):
                self.assertEqual(mesh.get('scale'),'0.001 0.001 0.001')
                self.assertTrue((output/mesh.get('filename')).is_file())
            for side,sign in [('left',-1),('right',1)]:
                chain=Chain(xml,root='compact_module_base',tip=side+'_gripper_envelope_tip')
                np.testing.assert_allclose(chain.forward([0,0])[0,:3,3],[sign*.09,.306,.058],atol=1e-12)
                with self.assertRaises(ValueError): chain.forward([0,2])

    def test_clearance_detects_containment_and_known_gap(self):
        outer=cq.Workplane('XY').box(10,10,10).val()
        inner=cq.Workplane('XY').box(2,2,2).val()
        self.assertEqual(solid_clearance_mm(outer,inner),0)
        moved=inner.translate((8,0,0))
        self.assertAlmostEqual(solid_clearance_mm(outer,moved),2,places=8)

    def test_bad_support_mount_and_tube_dimensions_rejected(self):
        for key,value in [('shoulder_offset_x',120),('mount_hole_pcd',72),('wall',20),
                          ('joint_axis_height',30),('upper_length',10),('forearm_width',24),('base_thickness',True)]:
            with self.subTest(key=key),self.assertRaises(ValueError):
                build({**self.p,key:value})


if __name__=='__main__': unittest.main()
