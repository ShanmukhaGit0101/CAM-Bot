#!/usr/bin/env python3
"""Measure repeated synthetic carrier return cycles on the isolated mock JTC."""

import argparse
import csv
import json
from pathlib import Path
import statistics
import time

from action_msgs.msg import GoalStatus
import rclpy

from probe_ur5_mock_controller import Probe, JOINTS


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    parser.add_argument('--cycles', type=int, default=20)
    args = parser.parse_args()
    if not 10 <= args.cycles <= 100:
        parser.error('cycles must be between 10 and 100')
    args.output.mkdir(parents=True, exist_ok=False)
    rclpy.init()
    node = Probe()
    rows = []
    try:
        assert node.client.wait_for_server(timeout_sec=30)
        node.spin_for(0.5)
        assert node.joint_records
        origin = [node.joint_records[-1][j] for j in JOINTS]
        target = [q + 0.05 for q in origin]
        with (args.output / 'cycles.csv').open('x', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=[
                'cycle', 'duration_s', 'success', 'failure', 'feedback_samples'])
            writer.writeheader()
            for cycle in range(1, args.cycles + 1):
                started = time.monotonic()
                before = node.feedback_count
                failure = ''
                success = True
                for positions in (target, origin):
                    node.plan['stations']['PROBE']['carrier_joints'] = positions
                    if not node._move_carrier('PROBE', 0.5):
                        success = False
                        failure = node.last_motion_failure
                        break
                    result = node.wait(node.client.handles[-1].get_result_async())
                    if result.status != GoalStatus.STATUS_SUCCEEDED:
                        success, failure = False, f'action_status_{result.status}'
                        break
                node.spin_for(0.05)
                if success and any(abs(node.joint_records[-1][j] - q) > 0.002
                                   for j, q in zip(JOINTS, origin)):
                    success, failure = False, 'return_position_mismatch'
                row = {'cycle': cycle, 'duration_s': time.monotonic() - started,
                       'success': success, 'failure': failure,
                       'feedback_samples': node.feedback_count - before}
                rows.append(row)
                writer.writerow(row)
                stream.flush()
                if not success:
                    break  # retain the failed attempt; never continue with unknown state
    finally:
        durations = [r['duration_s'] for r in rows if r['success']]
        summary = {
            'scope': 'synthetic outbound/return carrier cycles on GenericSystem',
            'timing_boundary': 'before outbound action until return result and 0.05s observation',
            'planning_time_s': None, 'planning_note': 'no planner is used',
            'requested': args.cycles, 'attempted': len(rows),
            'successful': len(durations), 'failed': sum(not r['success'] for r in rows),
            'mean_success_duration_s': statistics.mean(durations) if durations else None,
            'sample_sd_s': statistics.stdev(durations) if len(durations) > 1 else None,
            'min_s': min(durations) if durations else None,
            'max_s': max(durations) if durations else None,
            'station_targets_validated': False, 'grasp_verified': False,
            'physical_operation_verified': False, 'end_to_end_verified': False,
            'complete': len(rows) == args.cycles and all(r['success'] for r in rows),
        }
        (args.output / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
        node.destroy_node()
        rclpy.shutdown()
    assert summary['complete'], 'benchmark failed; inspect retained attempts'
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
