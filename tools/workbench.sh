#!/usr/bin/env bash
# Shared entry point for VS Code tasks and ordinary terminals.
set -eo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"
command_name="${1:-help}"
case "$command_name" in
  help|--help)
    echo 'Usage: bash tools/workbench.sh COMMAND [argument]'
    echo 'Host: doctor, offline-test, analysis, analyze-run CSV, workspace, presentation'
    echo 'Humble: build, test, launch, start, cancel, observe, graph, mock-build, mock-test'
    echo 'ROS commands use native Humble or the running cambot-vscode container.'
    exit 0 ;;
  doctor)
    printf 'Checkout: %s\n' "$root"
    git status --short --branch
    python3 --version
    if [[ -f /opt/ros/humble/setup.bash ]]; then echo 'Native Humble: available';
    else echo 'Native Humble: absent (use prepared container; no Jazzy required)'; fi
    if command -v docker >/dev/null; then
      docker inspect --format 'Container: {{.Name}} Running={{.State.Running}} Image={{.Config.Image}}' \
        "${CAMBOT_CONTAINER:-cambot-vscode}" || true
    fi
    echo 'See docs/VSCODE.md for setup, dependencies and demo order.'
    exit 0 ;;
  offline-test|analysis|analyze-run|workspace|presentation) ;;
  build|test|launch|start|cancel|observe|graph|mock-build|mock-test)
    if [[ "${CAMBOT_WORKBENCH_INSIDE:-0}" != 1 ]] && \
       { [[ -n "${CAMBOT_CONTAINER:-}" ]] || [[ ! -f /opt/ros/humble/setup.bash ]]; }; then
      container="${CAMBOT_CONTAINER:-cambot-vscode}"
      command -v docker >/dev/null || { echo 'Docker/Humble unavailable. Read docs/VSCODE.md.' >&2; exit 2; }
      [[ "$(docker inspect --format '{{.State.Running}}' "$container" 2>/dev/null)" == true ]] || {
        echo "Start the prepared GUI container $container using docs/VSCODE.md first." >&2; exit 2;
      }
      # Require this exact checkout to be mounted; do not accidentally run an older clone.
      mounted="$(docker inspect --format '{{range .Mounts}}{{if eq .Destination "/workspace/CAM-BOT"}}{{.Source}}{{end}}{{end}}' "$container")"
      [[ "$(realpath "$mounted")" == "$root" ]] || {
        echo 'Container mounts a different checkout; recreate it using docs/VSCODE.md.' >&2; exit 2;
      }
      tty_args=()
      [[ ! -t 0 || ! -t 1 ]] || tty_args=(-t)
      exec docker exec -i "${tty_args[@]}" -w /workspace/CAM-BOT \
        -e CAMBOT_WORKBENCH_INSIDE=1 -e ROS_DOMAIN_ID="${ROS_DOMAIN_ID:-109}" \
        "$container" bash tools/workbench.sh "$@"
    fi
    [[ -f /opt/ros/humble/setup.bash ]] || { echo 'ROS Humble is required.' >&2; exit 2; }
    source /opt/ros/humble/setup.bash
    [[ ! -f /opt/cambot/rviz/setup.bash ]] || source /opt/cambot/rviz/setup.bash
    export ROS_DOMAIN_ID="${ROS_DOMAIN_ID:-109}" ROS_LOCALHOST_ONLY=1
    if [[ "$command_name" != build && "$command_name" != mock-build ]]; then
      [[ -f install/setup.bash ]] || { echo 'Run the Build task first.' >&2; exit 2; }
      source install/setup.bash
    fi ;;
  *) echo "Unknown command: $command_name (use --help)" >&2; exit 2 ;;
esac
export PYTHONPATH="$root/src/carrier_control:$root/src/carrier_description:${PYTHONPATH:-}"
export MPLBACKEND=Agg
case "$command_name" in
  offline-test|analysis|analyze-run|workspace|presentation)
    [[ ! -x "$root/.venv/bin/python3" ]] || export PATH="$root/.venv/bin:$PATH" ;;
esac
new_output() {
  mkdir -p "$root/.cambot-runs"
  output="$(mktemp -d "$root/.cambot-runs/$1.XXXXXX")"
  git rev-parse HEAD > "$output/source-commit.txt"
  git status --porcelain > "$output/working-tree.txt"
  printf 'New output: %s\n' "$output"
}
case "$command_name" in
  build|mock-build)
    packages=(carrier_description carrier_control)
    [[ "$command_name" != mock-build ]] || packages+=(carrier_controller_testbed)
    colcon build --base-paths src --symlink-install --executor sequential --packages-select "${packages[@]}" ;;
  test)
    colcon test --base-paths src --executor sequential --return-code-on-test-failure \
      --packages-select carrier_description carrier_control
    colcon test-result --verbose
    python3 tools/check_ay13_docs.py --installed ;;
  offline-test)
    python3 tools/check_ay13_docs.py
    python3 -m unittest tools.test_build_presentation tools.test_workbench \
      tools.test_analyze_workspace tools.test_analyze_module_feasibility -v
    python3 -m unittest discover -s experiments/machine_tending/tests -v ;;
  launch|start|cancel)
    export CAMBOT_PRESENTATION_OUTPUT_ROOT="$root/.cambot-runs"
    exec bash tools/present_demo.sh "$command_name" ;;
  observe)
    # Subscribe before pressing Start. Ctrl-C stops only these observers.
    new_output observers
    pids=()
    cleanup() { for pid in "${pids[@]}"; do kill "$pid" 2>/dev/null || true; wait "$pid" 2>/dev/null || true; done; }
    trap cleanup EXIT
    trap 'exit 130' INT TERM
    for topic in task_state workpiece_state coordination_decision; do
      ros2 topic echo "/cambot/$topic" > "$output/$topic.log" 2>&1 & pids+=("$!")
    done
    echo 'Observing all three topics. Start the cycle in another task; Ctrl-C stops observers.'
    tail --pid="$$" -n +1 -F "$output/"*.log & pids+=("$!")
    wait ;;
  graph)
    ros2 node list --no-daemon
    ros2 topic info /joint_states --verbose ;;
  analysis|analyze-run)
    raw="$root/experiments/machine_tending/runs/ay10-visual-20261015-03/raw/trials.csv"
    qualify=(--qualify)
    if [[ "$command_name" == analyze-run ]]; then
      [[ $# == 2 && -f "$2" ]] || { echo 'Supply the new run trials.csv path.' >&2; exit 2; }
      raw="$(realpath "$2")"; qualify=()
    fi
    new_output analysis
    python3 experiments/machine_tending/scripts/analyze_trials.py "$raw" \
      --output "$output/analysis" "${qualify[@]}" | tee "$output/runner.log" ;;
  workspace)
    new_output workspace
    python3 tools/analyze_workspace.py \
      --urdf experiments/workspace/runs/model-study-20261107/model.urdf \
      --placements experiments/workspace/placements.json --samples 20000 \
      --output "$output/study" | tee "$output/runner.log" ;;
  mock-test)
    new_output mock
    CAMBOT_RUN_BIMANUAL=1 bash tools/run_ur5_mock_controller.sh "$output/replay" | tee "$output/runner.log" ;;
  presentation)
    echo 'Open http://127.0.0.1:8765/CAM-BOT.html (Ctrl-C stops the server).'
    exec python3 -m http.server 8765 --bind 127.0.0.1 --directory "$root/presentation" ;;
esac
