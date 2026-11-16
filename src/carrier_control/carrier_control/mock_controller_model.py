"""Add a mock-only control block without changing the UR5 kinematic chain."""

import xml.etree.ElementTree as ET


JOINTS = (
    'shoulder_pan_joint', 'shoulder_lift_joint', 'elbow_joint',
    'wrist_1_joint', 'wrist_2_joint', 'wrist_3_joint',
)


BIMANUAL_JOINTS = (
    'left_shoulder_joint', 'left_elbow_joint',
    'right_shoulder_joint', 'right_elbow_joint',
)


def mock_control_description(description, include_bimanual=False):
    """Use GenericSystem only; this helper cannot select a physical driver."""
    robot = ET.fromstring(description)
    if robot.tag != 'robot' or len(robot.findall('ros2_control')) > 1:
        raise ValueError('expected robot with at most one ros2_control block')
    joints = {joint.get('name'): joint for joint in robot.findall('joint')}
    if any(name not in joints or joints[name].get('type') != 'revolute' for name in JOINTS):
        raise ValueError('expected all six UR5 revolute joints')
    controlled = JOINTS + (BIMANUAL_JOINTS if include_bimanual else ())
    if any(name not in joints or joints[name].get('type') != 'revolute'
           for name in controlled):
        raise ValueError('expected all selected mock revolute joints')
    # ur_description emits a physical-driver block even in a visual expansion.
    # Replace it entirely: no network driver, GPIO or robot address survives.
    for existing in robot.findall('ros2_control'):
        robot.remove(existing)
    control = ET.SubElement(robot, 'ros2_control', name='CAMBOTMockUR5', type='system')
    hardware = ET.SubElement(control, 'hardware')
    ET.SubElement(hardware, 'plugin').text = 'mock_components/GenericSystem'
    for name in controlled:
        joint = ET.SubElement(control, 'joint', name=name)
        ET.SubElement(joint, 'command_interface', name='position')
        position = ET.SubElement(joint, 'state_interface', name='position')
        ET.SubElement(position, 'param', name='initial_value').text = '0.0'
        ET.SubElement(joint, 'state_interface', name='velocity')
    return ET.tostring(robot, encoding='unicode')
