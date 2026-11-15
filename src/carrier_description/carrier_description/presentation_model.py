"""
Display-only styling for the accepted four-joint placeholder model.

Joint frames, limits, collision shapes and the upstream UR5 are preserved.
The passive tool outlines are illustrative, without actuation or grasp feedback.
"""

import xml.etree.ElementTree as ET


ARM_COLOURS = {'left': '0.12 0.55 0.90 1', 'right': '0.95 0.48 0.12 1'}
METAL = '0.72 0.78 0.84 1'
JOINT = '0.18 0.23 0.30 1'


def _visual(link, shape, dimensions, xyz, colour, rpy='0 0 0'):
    visual = ET.SubElement(link, 'visual')
    ET.SubElement(visual, 'origin', xyz=xyz, rpy=rpy)
    geometry = ET.SubElement(visual, 'geometry')
    ET.SubElement(geometry, shape, **dimensions)
    material = ET.SubElement(visual, 'material', name='presentation_' + colour.replace(' ', '_'))
    ET.SubElement(material, 'color', rgba=colour)


def _clear_visuals(link):
    for visual in list(link.findall('visual')):
        link.remove(visual)


def presentation_description(description):
    """
    Restyle only known attachment visuals, leaving motion geometry intact.

    The current accepted model has 0.25 m upper links and 0.22 m forearms.
    Derive those lengths from existing geometry rather than relocating joints.
    Reject unsupported geometry rather than silently drawing disconnected arms.
    """
    robot = ET.fromstring(description)
    links = {link.get('name'): link for link in robot.findall('link')}
    required = ['carrier_flange', 'dual_arm_base_link'] + [
        f'{side}_{part}' for side in ARM_COLOURS for part in ('upper_arm', 'forearm')]
    if any(name not in links for name in required):
        raise ValueError('presentation styling requires the accepted CAM-BOT attachment')
    lengths = {}
    for side in ARM_COLOURS:
        for part in ('upper_arm', 'forearm'):
            name = f'{side}_{part}'
            box = links[name].find('visual/geometry/box')
            if box is None:
                raise ValueError('presentation styling expects original box links: ' + name)
            lengths[name] = float(box.get('size').split()[1])
            if lengths[name] <= 0:
                raise ValueError('invalid arm length: ' + name)
    for name in required:
        _clear_visuals(links[name])
    _visual(links['carrier_flange'], 'box', {'size': '0.32 0.12 0.018'},
            '0 0 0.025', METAL)
    _visual(links['dual_arm_base_link'], 'box', {'size': '0.48 0.10 0.025'},
            '0 0 0.0125', METAL)
    for side, colour in ARM_COLOURS.items():
        upper = links[f'{side}_upper_arm']
        forearm = links[f'{side}_forearm']
        upper_length = lengths[f'{side}_upper_arm']
        forearm_length = lengths[f'{side}_forearm']
        # Cylinders are centred on the same +Y link segments as the old boxes.
        for link, length, radius in ((upper, upper_length, '0.023'),
                                     (forearm, forearm_length, '0.019')):
            _visual(link, 'cylinder', {'radius': radius, 'length': str(length)},
                    f'0 {length / 2} 0', colour, '1.5707963267948966 0 0')
        _visual(upper, 'cylinder', {'radius': '0.038', 'length': '0.065'},
                '0 0 0', JOINT)
        _visual(forearm, 'cylinder', {'radius': '0.033', 'length': '0.065'},
                '0 0 0', METAL, '0 1.5707963267948966 0')
        _visual(forearm, 'box', {'size': '0.065 0.025 0.025'},
                f'0 {forearm_length} 0', JOINT)
        for x in (-0.025, 0.025):
            _visual(forearm, 'box', {'size': '0.012 0.04 0.018'},
                    f'{x} {forearm_length + 0.025} 0', METAL)
    return ET.tostring(robot, encoding='unicode')


def reverse_arm_mounts(description):
    """
    Exchange local-arm sides and mirror the right elbow for paired folding.

    The matching plan must exchange left/right command pairs and proxy labels.
    The carrier and bimanual base frames remain unchanged. This is a new visual
    assembly arrangement, not a mechanically validated redesign.
    """
    robot = ET.fromstring(description)
    joints = {joint.get('name'): joint for joint in robot.findall('joint')}
    left = joints['left_shoulder_joint'].find('origin')
    right = joints['right_shoulder_joint'].find('origin')
    left_xyz, right_xyz = left.get('xyz'), right.get('xyz')
    left.set('xyz', right_xyz)
    right.set('xyz', left_xyz)
    joints['right_elbow_joint'].find('axis').set('xyz', '-1 0 0')
    return ET.tostring(robot, encoding='unicode')
