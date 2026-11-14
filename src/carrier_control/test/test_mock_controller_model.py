"""Check isolation and preservation of the kinematic description."""

import unittest
import xml.etree.ElementTree as ET

from carrier_control.mock_controller_model import JOINTS, mock_control_description


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
