#!/usr/bin/env bash
# Run inside the Task-7 image after scoped colcon build, in an unused ROS domain.
set -eo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
[[ $# == 1 && ! -e "$1" ]] || { echo 'Usage: NEW_OUTPUT_DIRECTORY'; exit 2; }
out="$(realpath -m "$1")"
mkdir -p "$out"
source /opt/ros/humble/setup.bash
source install/setup.bash
export ROS_LOCALHOST_ONLY=1
[[ -n "${ROS_DOMAIN_ID:-}" && "$ROS_DOMAIN_ID" != 0 ]] || {
  echo 'Select an unused nonzero ROS_DOMAIN_ID'; exit 2;
}
ros2 node list --no-daemon > "$out/preexisting_nodes.txt"
[[ ! -s "$out/preexisting_nodes.txt" ]] || { echo 'ROS domain is occupied'; exit 2; }
{
  git rev-parse HEAD
  git status --short
  dpkg-query -W ros-humble-controller-manager ros-humble-hardware-interface \
    ros-humble-joint-trajectory-controller ros-humble-joint-state-broadcaster \
    ros-humble-ur-description
  printf 'ROS_DOMAIN_ID=%s\n' "$ROS_DOMAIN_ID"
} > "$out/environment.txt"
bimanual_arg=false
if [[ "${CAMBOT_RUN_BIMANUAL:-0}" == 1 ]]; then
  bimanual_arg=true
fi
python3 tools/start_ros_session.py ros2 launch carrier_controller_testbed \
  ur5_mock_controller.launch.py "enable_bimanual_mock:=$bimanual_arg" > "$out/launch.log" 2>&1 &
launch_pid=$!
cleanup() {
  kill -INT "$launch_pid" 2>/dev/null || true
  for attempt in $(seq 1 100); do
    kill -0 "$launch_pid" 2>/dev/null || break
    sleep 0.1
  done
  if kill -0 "$launch_pid" 2>/dev/null; then
    echo 'Launch failed to stop within 10s' > "$out/shutdown_failure.txt"
    kill -TERM "$launch_pid" 2>/dev/null || true
  fi
  wait "$launch_pid" || true
}
trap cleanup EXIT
python3 tools/probe_ur5_mock_controller.py "$out/probe" > "$out/probe.log" 2>&1
if [[ "${CAMBOT_RUN_BIMANUAL:-0}" == 1 ]]; then
  python3 tools/probe_bimanual_mock_controller.py "$out/bimanual" > "$out/bimanual.log" 2>&1
fi
if [[ "${CAMBOT_RUN_BENCHMARK:-0}" == 1 ]]; then
  python3 tools/benchmark_mock_controller.py "$out/benchmark" > "$out/benchmark.log" 2>&1
fi
cleanup
trap - EXIT
[[ ! -e "$out/shutdown_failure.txt" ]]
ros2 node list --no-daemon > "$out/residual_nodes.txt"
[[ ! -s "$out/residual_nodes.txt" ]]
python3 - "$out/launch.log" <<'PY'
from pathlib import Path
import re
import sys
text = Path(sys.argv[1]).read_text()
for marker in ('Traceback', 'process has died', 'failed to terminate', 'escalating'):
    assert marker not in text, marker
for node in ('ros2_control_node', 'robot_state_publisher'):
    assert re.search(r'\[' + node + r'-\d+\]: process has finished cleanly', text), node
print('TASK7_MOCK_SHUTDOWN_PASS')
PY
cat "$out/probe/result.json"
