"""Visual-only angular routing and exchanged, mirrored local-arm poses."""

import argparse
from copy import deepcopy
import json
import math
from pathlib import Path

from carrier_control.workflow import load_plan, validate_plan


# Stock Humble UR5 model limits, not physical controller configuration.
UR5_VISUAL_LIMITS = ((-math.tau, math.tau), (-math.tau, math.tau),
                     (-math.pi, math.pi), (-math.tau, math.tau),
                     (-math.tau, math.tau), (-math.tau, math.tau))
ARM_LAYOUT = 'swapped_mirrored'


def nearest_visual_route(start, configured_goal, limits=UR5_VISUAL_LIMITS):
    """
    Return equivalent start/goal angles with the shortest bounded visual route.

    A wide-range joint may need its start representation shifted by a full turn
    first; this changes no rendered orientation. Both ends stay within limits.
    Narrow bounded joints can still require the long route. This is solely a
    visual winding choice, never a physical controller or collision-free plan.
    """
    if len(start) != len(configured_goal) or len(start) != len(limits):
        raise ValueError('joint vectors and limits must have matching lengths')
    starts, goals = [], []
    for current, goal, (lower, upper) in zip(start, configured_goal, limits):
        if (any(isinstance(x, bool) or not math.isfinite(x)
                for x in (current, goal, lower, upper)) or lower > upper or
                not lower <= current <= upper or not lower <= goal <= upper):
            raise ValueError('visual joint angle outside finite model limits')

        def equivalents(angle):
            first = math.ceil((lower - angle) / math.tau)
            last = math.floor((upper - angle) / math.tau)
            return [angle + turns * math.tau for turns in range(first, last + 1)]

        candidates = [(a, b) for a in equivalents(current) for b in equivalents(goal)]
        a, b = min(candidates, key=lambda pair: (
            round(abs(pair[1] - pair[0]), 12), abs(pair[0] - current),
            abs(pair[1] - goal)))
        starts.append(a)
        goals.append(b)
    return starts, goals


def swapped_arm_plan(plan):
    """Exchange mount-side command pairs and proxy labels without editing input."""
    if plan.get('visual_arm_layout'):
        raise ValueError('arm layout is already selected; start from the original plan')
    result = deepcopy(plan)
    result['visual_arm_layout'] = ARM_LAYOUT
    result['assumption_note'] += (
        ' Presentation profile: arm sides and pose pairs exchanged; right elbow '
        'axis mirrored. Visual illustration only, no verified contact or grasp.')
    workspace = result['workspace']
    workspace['left'], workspace['right'] = workspace['right'], workspace['left']
    result['bimanual_poses'] = {
        name: values[2:] + values[:2] for name, values in result['bimanual_poses'].items()}
    validate_plan(result)
    return result


def main():
    """Write a separate effective plan so the actual run configuration is retained."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    plan = swapped_arm_plan(load_plan(args.source))
    with args.output.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(plan, indent=2) + '\n')


if __name__ == '__main__':
    main()
