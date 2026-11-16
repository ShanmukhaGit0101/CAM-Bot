"""Hand-calculated visual joint-excursion fixtures and missing telemetry cases."""

import unittest
from tools.analyze_demo_motion import summarize


def event(action, start, end, result='COMPLETED', **extra):
    return {'action': action, 'result': result, 'details': {
        'start_joints_rad': start, 'goal_joints_rad': end,
        'final_joints_rad': end, **extra}}


class MotionAnalysisTests(unittest.TestCase):
    def test_independent_excursions_and_declared_references(self):
        plan = {'stations': {'HOME': {'visual_carrier_joints': [0, 0]},
                             'S1': {'visual_carrier_joints': [5, 1]}},
                'bimanual_poses': {'HOME': [0, 0]}}
        events = [event('CARRIER_MOTION', [0, 0], [-1, 1],
                        station='S1', is_reposition=True, nontrivial=True),
                  event('BIMANUAL_MOTION', [0, 0], [1, -1]),
                  event('BIMANUAL_MOTION', [1, -1], [2, -1])]
        result = summarize(events, plan)
        self.assertEqual(result['carrier_completed_joint_excursion_rad'], 2)
        self.assertEqual(result['carrier_stored_angle_reference_rad'], 6)
        self.assertEqual(result['local_completed_joint_excursion_rad'], 3)
        self.assertEqual(result['local_home_between_segments_reference_rad'], 7)
        self.assertEqual(result['carrier_repositions'], 1)
        self.assertFalse(result['grasp_verified'])

    def test_missing_local_telemetry_is_unknown_instead_of_zero(self):
        result = summarize([])
        self.assertIsNone(result['local_completed_joint_excursion_rad'])
        self.assertIsNone(result['local_home_between_segments_reference_rad'])
        self.assertIsNone(result['carrier_stored_angle_reference_rad'])

    def test_failed_segment_is_not_a_completed_movement(self):
        result = summarize([event('BIMANUAL_MOTION', [0], [1], result='FAILED')])
        self.assertEqual(result['local_completed_segments'], 0)
        self.assertIsNone(result['local_completed_joint_excursion_rad'])


if __name__ == '__main__':
    unittest.main()
