#!/usr/bin/env python3

import pandas as pd
import numpy as np
from pathlib import Path

BASE = Path(__file__).resolve().parent
DATA = BASE / "data"
RESULTS = BASE / "results"

RESULTS.mkdir(exist_ok=True)

FILES = {
    "baseline_8.393kg": DATA / "baseline_8.393kg.csv",
    "experiment_9.2323kg": DATA / "experiment_9.2323kg.csv",
}

JOINTS = [
    "shoulder_pan_joint",
    "shoulder_lift_joint",
    "elbow_joint",
    "wrist_1_joint",
    "wrist_2_joint",
    "wrist_3_joint",
]

LABELS = [
    "Shoulder Pan",
    "Shoulder Lift",
    "Elbow",
    "Wrist 1",
    "Wrist 2",
    "Wrist 3",
]


def load_data(path):
    df = pd.read_csv(path)

    t = df["time"].to_numpy(dtype=float)
    t = t - t[0]

    return df, t


def calculate_metrics(df, t, joint):

    position = df[f"{joint}_pos"].to_numpy(dtype=float)
    velocity = df[f"{joint}_vel"].to_numpy(dtype=float)

    acceleration = np.gradient(velocity, t)

    return {
        "position_min": np.min(position),
        "position_max": np.max(position),
        "position_range": np.ptp(position),

        "velocity_min": np.min(velocity),
        "velocity_max": np.max(velocity),
        "velocity_max_abs": np.max(np.abs(velocity)),

        "acceleration_min": np.min(acceleration),
        "acceleration_max": np.max(acceleration),
        "acceleration_max_abs": np.max(np.abs(acceleration)),
    }


# ============================================================
# LOAD DATA
# ============================================================

datasets = {}

for name, path in FILES.items():

    if not path.exists():
        raise FileNotFoundError(
            f"Required CSV not found:\n{path}"
        )

    datasets[name] = load_data(path)


# ============================================================
# CALCULATE
# ============================================================

metrics = {}

for name, (df, t) in datasets.items():

    metrics[name] = {}

    for joint in JOINTS:
        metrics[name][joint] = calculate_metrics(
            df,
            t,
            joint
        )


# ============================================================
# REPORT
# ============================================================

lines = []

lines.append("=" * 78)
lines.append(
    "UR5 EXPERIMENT 01 — UPPER ARM MASS +10% COMPARISON"
)
lines.append("=" * 78)

lines.append("")
lines.append("DATASETS")
lines.append("-" * 78)

for name, (df, t) in datasets.items():

    dt = np.diff(t)

    mean_dt = np.mean(dt)
    rate = 1.0 / mean_dt

    lines.append(
        f"{name:25s} "
        f"samples={len(df):6d} "
        f"duration={t[-1]:10.6f} s "
        f"rate={rate:8.3f} Hz"
    )


lines.append("")
lines.append("MASS CONFIGURATION")
lines.append("-" * 78)

lines.append(
    "Baseline upper_arm_link mass   : 8.3930 kg"
)

lines.append(
    "Experiment upper_arm_link mass : 9.2323 kg"
)

lines.append(
    "Mass increase                   : +0.8393 kg"
)

lines.append(
    "Mass increase                   : +10.00%"
)


# ============================================================
# COMPARISON TABLE
# ============================================================

lines.append("")
lines.append("PRIMARY COMPARISON")
lines.append("-" * 78)

lines.append(
    f"{'Joint':18s} "
    f"{'Metric':20s} "
    f"{'Baseline':>14s} "
    f"{'Experiment':>14s} "
    f"{'Delta':>14s} "
    f"{'Delta %':>10s}"
)

lines.append("-" * 110)


for joint, label in zip(JOINTS, LABELS):

    for key, metric_name in [
        ("position_range", "Position range"),
        ("velocity_max_abs", "Max |velocity|"),
        ("acceleration_max_abs", "Max |acceleration|"),
    ]:

        baseline = metrics["baseline_8.393kg"][joint][key]

        experiment = metrics["experiment_9.2323kg"][joint][key]

        delta = experiment - baseline

        if abs(baseline) > 1e-15:
            percent = (delta / abs(baseline)) * 100.0
        else:
            percent = float("nan")

        lines.append(
            f"{label:18s} "
            f"{metric_name:20s} "
            f"{baseline:14.8f} "
            f"{experiment:14.8f} "
            f"{delta:14.8f} "
            f"{percent:10.3f}"
        )


# ============================================================
# FULL EXTREMES
# ============================================================

lines.append("")
lines.append(
    "FULL JOINT POSITION / VELOCITY / ACCELERATION EXTREMES"
)
lines.append("-" * 78)

for joint, label in zip(JOINTS, LABELS):

    lines.append("")
    lines.append(label)

    for key, metric_name in [
        ("position_min", "Position minimum"),
        ("position_max", "Position maximum"),
        ("velocity_min", "Velocity minimum"),
        ("velocity_max", "Velocity maximum"),
        ("acceleration_min", "Acceleration minimum"),
        ("acceleration_max", "Acceleration maximum"),
    ]:

        baseline = metrics["baseline_8.393kg"][joint][key]

        experiment = metrics["experiment_9.2323kg"][joint][key]

        delta = experiment - baseline

        lines.append(
            f"  {metric_name:22s} "
            f"baseline={baseline: .9f} "
            f"experiment={experiment: .9f} "
            f"delta={delta: .9f}"
        )


# ============================================================
# NOTES
# ============================================================

lines.append("")
lines.append("ANALYSIS NOTES")
lines.append("-" * 78)

lines.append(
    "Baseline dataset : upper_arm_link = 8.3930 kg"
)

lines.append(
    "Experiment dataset : upper_arm_link = 9.2323 kg"
)

lines.append(
    "Position and velocity are taken directly from /joint_states."
)

lines.append(
    "Acceleration is numerically derived from velocity using "
    "numpy.gradient()."
)

lines.append(
    "Percentage changes are calculated relative to the 8.3930 kg baseline."
)

lines.append(
    "Both datasets are from completed recorded trials."
)

lines.append(
    "This script does NOT execute or publish any robot trajectory."
)

lines.append("=" * 78)


# ============================================================
# SAVE
# ============================================================

output = RESULTS / "exp01_mass_comparison.txt"

output.write_text(
    "\n".join(lines) + "\n"
)


print("=" * 78)
print("UR5 EXPERIMENT 01 COMPARISON COMPLETE")
print("=" * 78)
print(f"Baseline  : {FILES['baseline_8.393kg']}")
print(f"Experiment: {FILES['experiment_9.2323kg']}")
print(f"Results   : {output}")
print("=" * 78)
