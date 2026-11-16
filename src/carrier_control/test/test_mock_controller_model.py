"""Check isolation and preservation of the kinematic description."""

import unittest
import xml.etree.ElementTree as ET

from carrier_control.mock_controller_model import (
    BIMANUAL_JOINTS, JOINTS, mock_control_description,
)


class MockModelTests(unittest.TestCase):
    def model(self):
        return '<robot name="fixture">' + ''.join(
            f'<joint name="{name}" type="revolute"><origin xyz="1 2 3"/></joint>'
            for name in JOINTS) + '</robot>'

    def test_preserves_chain_and_only_selects_mock_plugin(self):
        original = ET.fromstring(self.model())
        output = ET.fromstring(mock_control_description(self.model()))
        self.assertEqual([ET.tostring(j) for j in original],
                         [ET.tostring(j) for j in output if j.tag != 'ros2_control'])
        self.assertEqual(output.findtext('ros2_control/hardware/plugin'),
                         'mock_components/GenericSystem')
        self.assertEqual([j.get('name') for j in output.findall('ros2_control/joint')],
                         list(JOINTS))

    def test_rejects_multiple_hardware_blocks_and_missing_joints(self):
        with self.assertRaises(ValueError):
            model = self.model().replace('</robot>', '<ros2_control/><ros2_control/></robot>')
            mock_control_description(model)
        with self.assertRaises(ValueError):
            mock_control_description('<robot/>')

    def test_removes_physical_driver_and_network_parameters(self):
        hardware = (
            '<ros2_control><hardware><plugin>ur_robot_driver/Driver</plugin>'
            '<param name="robot_ip">192.0.2.1</param></hardware></ros2_control>')
        model = self.model().replace('</robot>', hardware + '</robot>')
        output = mock_control_description(model)
        self.assertNotIn('robot_ip', output)
        self.assertNotIn('ur_robot_driver', output)
        self.assertEqual(len(ET.fromstring(output).findall('ros2_control')), 1)

    def test_bimanual_is_opt_in_and_preserves_all_kinematics(self):
        model = self.model().replace('</robot>', ''.join(
            f'<joint name="{name}" type="revolute"><origin xyz="0 1 0"/></joint>'
            for name in BIMANUAL_JOINTS) + '</robot>')
        original = ET.fromstring(model)
        default = ET.fromstring(mock_control_description(model))
        expanded = ET.fromstring(mock_control_description(model, include_bimanual=True))
        self.assertEqual(len(default.findall('ros2_control/joint')), 6)
        self.assertEqual([j.get('name') for j in expanded.findall('ros2_control/joint')],
                         list(JOINTS + BIMANUAL_JOINTS))
        self.assertEqual([ET.tostring(j) for j in original],
                         [ET.tostring(j) for j in expanded if j.tag != 'ros2_control'])
        self.assertNotIn('gripper', ET.tostring(expanded, encoding='unicode'))

    def test_bimanual_missing_joints_rejected(self):
        with self.assertRaises(ValueError):
            mock_control_description(self.model(), include_bimanual=True)
