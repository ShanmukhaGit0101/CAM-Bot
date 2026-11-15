#!/usr/bin/env python3
"""Replay visual scenario profiles in an empty Humble domain, retaining evidence."""

import argparse
import csv
import json
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import time

from check_ros_shutdown import check_shutdown

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {'original': 5, 'compact': 3, 'tiered': 5, 'precision': 5}


def replay(output, scenarios, screenshots=False):
    output.mkdir(parents=True, exist_ok=False)
    qt = None
    if screenshots:
        from PyQt5.QtWidgets import QApplication
        qt = QApplication([])
    for scenario in scenarios:
        case = output / scenario
        case.mkdir()
        log_path = case / 'launch.log'
        log = log_path.open('w')
        launch = subprocess.Popen(['bash', 'tools/present_demo.sh', 'launch', scenario],
                                  cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
                                  start_new_session=True)
        probe = None
        try:
            until = time.monotonic() + 30
            while 'VISUAL SIMULATION ONLY' not in log_path.read_text():
                if launch.poll() is not None or time.monotonic() > until:
                    raise RuntimeError(f'{scenario} failed to launch; inspect {log_path}')
                time.sleep(.1)
            probe_path = case / 'probe.jsonl'
            with probe_path.open('w') as probe_log:
                probe = subprocess.Popen(['python3', 'tools/ay0608_ros_probe.py'],
                                         cwd=ROOT, stdout=probe_log, stderr=subprocess.STDOUT)
                deadline = time.monotonic() + 90
                captured = False
                while probe.poll() is None:
                    if time.monotonic() > deadline:
                        raise TimeoutError(f'{scenario} probe timed out')
                    if qt and not captured and re.search(
                            r'"event": "STEP_COMPLETED".*"step": "S3_LOAD"', probe_path.read_text()):
                        qt.processEvents()
                        qt.primaryScreen().grabWindow(0).save(str(case / 'S3_LOAD.png'))
                        captured = True
                    time.sleep(.1)
                if probe.returncode != 0:
                    raise RuntimeError(f'{scenario} probe failed; inspect {probe_path}')
                if qt:
                    qt.primaryScreen().grabWindow(0).save(str(case / 'complete.png'))
        finally:
            if probe and probe.poll() is None:
                probe.terminate()
                probe.wait(timeout=10)
            if launch.poll() is None:
                launch.send_signal(signal.SIGINT)
            try:
                launch.wait(timeout=15)
            finally:
                log.close()
                match = re.search(r'Presentation evidence: (.+)', log_path.read_text())
                if match and Path(match.group(1)).is_dir():
                    shutil.copytree(Path(match.group(1)), case / 'run')
        if launch.returncode != 0:
            raise RuntimeError(f'{scenario} launch exited {launch.returncode}')
        check_shutdown(log_path.read_text())
        graph = subprocess.run(['ros2', 'node', 'list', '--no-daemon'], check=True,
                               capture_output=True, text=True, timeout=15).stdout
        (case / 'residual_nodes.txt').write_text(graph)
        if graph.strip():
            raise RuntimeError('residual ROS nodes remain')
        match = re.search(r'Presentation evidence: (.+)', log_path.read_text())
        run = Path(match.group(1))
        with (run / 'trials.csv').open() as stream:
            trials = list(csv.DictReader(stream))
        if (len(trials) != 1 or trials[0]['success'] != 'True' or
                trials[0]['workpiece_final_state'] != 'FINISHED_AT_S5' or
                int(trials[0]['carrier_repositions']) != EXPECTED[scenario]):
            raise RuntimeError(f'{scenario} unexpected trial result: {trials}')
        (case / 'result.json').write_text(json.dumps({
            'scenario': scenario, 'result': 'PASS', 'repositions': EXPECTED[scenario],
            'scope': 'visual ROS/TF/RViz only', 'shutdown': 'three clean exits',
            'one_joint_state_publisher': True, 'residual_nodes': [],
            'grasp_verified': False, 'physical_operation_verified': False,
        }, indent=2) + '\n')
        print(f'PASS {scenario}: {EXPECTED[scenario]} repositions, FINISHED_AT_S5, clean shutdown',
              flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    parser.add_argument('--scenarios', nargs='+', choices=tuple(EXPECTED), default=list(EXPECTED))
    parser.add_argument('--screenshots', action='store_true', help='requires PyQt5 and DISPLAY')
    args = parser.parse_args()
    replay(args.output.resolve(), args.scenarios, args.screenshots)
