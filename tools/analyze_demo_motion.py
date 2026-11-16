#!/usr/bin/env python3
"""Report visual joint excursion and explicitly defined interpolation references."""

import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'src/carrier_control'))
from carrier_control.metrics import parameter_hash  # noqa: E402
from experiments.machine_tending.scripts.analyze_trials import analyze  # noqa: E402


def excursion(a, b):
    if len(a) != len(b):
        raise ValueError('joint dimensions differ')
    return sum(abs(x - y) for x, y in zip(a, b))


def summarize(events, plan=None):
    """Sum completed visual segment endpoint excursions, not measured robot work."""
    moves = [e for e in events if e['action'] == 'CARRIER_MOTION' and e['result'] == 'COMPLETED']
    local = [e for e in events if e['action'] == 'BIMANUAL_MOTION' and e['result'] == 'COMPLETED']
    carrier = sum(excursion(e['details']['start_joints_rad'],
                            e['details']['final_joints_rad']) for e in moves)
    custom = sum(excursion(e['details']['start_joints_rad'],
                           e['details']['final_joints_rad']) for e in local) if local else None
    # Reference A: linearly interpolate stored angles through the same visited goals.
    reference = None
    reset_reference = None
    if plan:
        previous = plan['stations']['HOME']['visual_carrier_joints']
        reference = 0.0
        for e in moves:
            target = plan['stations'][e['details']['station']]['visual_carrier_joints']
            reference += excursion(previous, target)
            previous = target
        # Reference B: return local arms HOME before each next local motion.
        # Same start and final targets as observed; no final extra HOME added.
        home = plan['bimanual_poses']['HOME']
        if local:
            reset_reference = sum(excursion(e['details']['start_joints_rad'], home) +
                                  excursion(home, e['details']['goal_joints_rad']) for e in local)
    return {
        'carrier_completed_joint_excursion_rad': carrier,
        'local_completed_joint_excursion_rad': custom,
        'carrier_stored_angle_reference_rad': reference,
        'local_home_between_segments_reference_rad': reset_reference,
        'carrier_repositions': sum(e['details']['is_reposition'] and e['details']['nontrivial']
                                  for e in moves),
        'local_completed_segments': len(local),
        'reference_scope': 'calculated references for the same run; not separately executed baselines',
        'metric_scope': 'sum absolute per-joint visual segment excursions; not distance, energy or hardware motion',
        'grasp_verified': False,
    }


def report(raw_csv, output):
    if output.exists():
        raise FileExistsError('choose a new output directory')
    raw_parent = raw_csv.resolve().parent
    if raw_parent == output.resolve() or raw_parent in output.resolve().parents:
        raise ValueError('motion output must be separate from immutable raw data')
    trials, _ = analyze(raw_csv)  # Existing integrity/schema/outcome checks apply first.
    events_path = raw_csv.with_suffix('.events.jsonl')
    grouped = defaultdict(list)
    for line in events_path.read_text().splitlines():
        event = json.loads(line)
        grouped[event['trial_id']].append(event)
    plan_path = raw_csv.parent / 'plan.json'
    plan = json.loads(plan_path.read_text()) if plan_path.is_file() else None
    summaries = []
    for trial in trials:
        if plan and parameter_hash(plan) != trial['scenario']['parameter_hash_sha256']:
            raise ValueError('effective plan hash does not match trial')
        summaries.append({'trial_id': trial['trial_id'], 'status': trial['status'],
                          **summarize(grouped[trial['trial_id']], plan)})
    data = {'trials': summaries, 'input_sha256': {
        str(path.name): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in (raw_csv, events_path)},
        'warning': 'Visual command logs only. References do not establish physical or timing efficiency.'}
    output.mkdir(parents=True)
    (output / 'motion_summary.json').write_text(json.dumps(data, indent=2) + '\n')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for ax, actual, ref, title, label in (
            (axes[0], 'carrier_completed_joint_excursion_rad', 'carrier_stored_angle_reference_rad',
             'Carrier', 'Stored-angle interpolation'),
            (axes[1], 'local_completed_joint_excursion_rad', 'local_home_between_segments_reference_rad',
             'Local arms', 'HOME between segments')):
        xs, values, labels = [], [], []
        for index, row in enumerate(summaries):
            for key, name in ((actual, 'Logged visual'), (ref, label)):
                if row[key] is not None:
                    xs.append(len(xs)); values.append(row[key]); labels.append(f'{index + 1}: {name}')
        if xs:
            ax.bar(xs, values, color=['#277b50' if 'Logged' in s else '#8093b5' for s in labels])
            ax.set_xticks(xs, labels, rotation=15, ha='right')
        else:
            ax.text(.5, .5, 'No local segment telemetry in this older capture',
                    ha='center', wrap=True, transform=ax.transAxes)
        ax.set_title(title)
        ax.set_ylabel('Sum of absolute joint excursions (rad)')
    fig.suptitle('Visual joint excursion; calculated references, no physical efficiency claim')
    fig.tight_layout()
    fig.savefig(output / 'motion_travel.png', dpi=150)
    plt.close(fig)
    print(json.dumps({'motion_output': str(output), 'trials': len(summaries)}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('raw_csv', type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    report(args.raw_csv, args.output)
