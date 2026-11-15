#!/usr/bin/env bash
# Presentation entry point for the accepted visual demo, inside prepared Humble.
set -eo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
mode="${1:-launch}"
if [[ "$mode" == --help ]]; then
  echo 'Usage: bash tools/present_demo.sh [launch|start|cancel]'
  echo 'Run inside the prepared ROS 2 Humble GUI environment. Default: visual launch.'
  echo 'Use the same ROS_DOMAIN_ID in both terminals (default 109).'
  exit 0
fi
case "$mode" in launch|start|cancel) ;; *) echo 'Unknown command; use --help' >&2; exit 2 ;; esac
[[ -f /opt/ros/humble/setup.bash && -f "$root/install/setup.bash" ]] || {
  echo 'Use the prepared Humble environment and build the two core packages first.' >&2
  echo "Offline presentation: $root/presentation/CAM-BOT.html" >&2
  exit 2
}
source /opt/ros/humble/setup.bash
[[ ! -f /opt/cambot/rviz/setup.bash ]] || source /opt/cambot/rviz/setup.bash
source "$root/install/setup.bash"
export ROS_DOMAIN_ID="${ROS_DOMAIN_ID:-109}"
export ROS_LOCALHOST_ONLY=1
export QT_QPA_PLATFORM="${QT_QPA_PLATFORM:-xcb}"
export LIBGL_ALWAYS_SOFTWARE="${LIBGL_ALWAYS_SOFTWARE:-1}"
cd "$root"
if [[ "$mode" != launch ]]; then
  exec timeout 20s ros2 service call "/machine_tending_coordinator/$mode" std_srvs/srv/Trigger '{}'
fi
ros2 pkg prefix rviz2 >/dev/null 2>&1 || {
  echo 'RViz is missing. Use the prepared visual image, not the headless controller image.' >&2
  exit 2
}
[[ -n "${DISPLAY:-}" ]] || {
  echo 'DISPLAY is unset. Configure GUI forwarding using docs/VSCODE.md.' >&2
  exit 2
}
nodes="$(ros2 node list --no-daemon)"
[[ -z "$nodes" ]] || {
  echo "ROS domain $ROS_DOMAIN_ID is occupied. Choose an unused domain in both terminals." >&2
  printf '%s\n' "$nodes" >&2
  exit 2
}
base="${CAMBOT_PRESENTATION_OUTPUT_ROOT:-$HOME/cambot-presentations}"
mkdir -p "$base"
output="$(mktemp -d "$base/run.XXXXXX")"
git rev-parse HEAD > "$output/source-commit.txt"
printf 'Presentation evidence: %s\nROS domain: %s\n' "$output" "$ROS_DOMAIN_ID"
printf 'In another sourced terminal: ROS_DOMAIN_ID=%s bash tools/present_demo.sh start\n' "$ROS_DOMAIN_ID"
echo 'Wait for RViz, start one cycle, observe FINISHED_AT_S5 and HOME, then Ctrl-C here.'
export ROS_LOG_DIR="$output/ros"
exec ros2 launch carrier_description dual_arm_demo.launch.py \
  auto_start:=false enable_coordination:=true trial_count:=1 visual_time_scale:=1.0 \
  experiment_id:=cambot-presentation results_file:="$output/trials.csv"
