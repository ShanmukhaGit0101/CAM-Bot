#!/usr/bin/env python3

import numpy as np
import pandas as pd
from pathlib import Path

BASE = Path(__file__).resolve().parent
DATA = BASE / "data"
RESULTS = BASE / "results"

BASELINE = DATA / "baseline_8.393_2.330kg.csv"
EXPERIMENT = DATA / "exp03_shoulder_4.070kg.csv"

OUT = RESULTS / "exp03_shoulder_mass_10pct_analysis.txt"

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


def analyze(path):
    df = pd.read_csv(path)

    t = df["time"].to_numpy()
    t = t - t[0]

    result = {
        "samples": len(df),
        "duration": t[-1],
        "positions": {},
        "velocities": {},
        "accelerations": {},
    }

    for joint in JOINTS:
        q = df[f"{joint}_pos"].to_numpy()

        v = np.gradient(q, t)
        a = np.gradient(v, t)

        result["positions"][joint] = {
            "min": np.min(q),
            "max": np.max(q),
            "range": np.max(q) - np.min(q),
        }

        result["velocities"][joint] = {
            "min": np.min(v),
            "max": np.max(v),
            "max_abs": np.max(np.abs(v)),
        }

        result["accelerations"][joint] = {
            "min": np.min(a),
            "max": np.max(a),
            "max_abs": np.max(np.abs(a)),
        }

    return result


b = analyze(BASELINE)
e = analyze(EXPERIMENT)


def pct(base, exp):
    if abs(base) < 1e-12:
        return 0.0
    return (exp - base) / abs(base) * 100.0


lines = []

lines.append("=" * 80)
lines.append("UR5 EXPERIMENT 03 — BASELINE vs +10% SHOULDER MASS")
lines.append("=" * 80)

lines.append("")
lines.append("MASS CONFIGURATION")
lines.append("-" * 80)
lines.append("Baseline shoulder mass : 3.7000 kg")
lines.append("Experiment shoulder    : 4.0700 kg")
lines.append("Mass increase          : +0.3700 kg")
lines.append("Percentage increase    : +10.00%")
lines.append("")
lines.append("Other masses unchanged:")
lines.append("Upper-arm mass         : 8.3930 kg")
lines.append("Forearm mass           : 2.3300 kg")

lines.append("")
lines.append("DATASET")
lines.append("-" * 80)
lines.append(f"Baseline samples       : {b['samples']}")
lines.append(f"Experiment samples     : {e['samples']}")
lines.append(f"Baseline duration      : {b['duration']:.6f} s")
lines.append(f"Experiment duration    : {e['duration']:.6f} s")

lines.append("")
lines.append("POSITION COMPARISON")
lines.append("-" * 80)
lines.append(
    f"{'Joint':<20}"
    f"{'Base Range':>14}"
    f"{'Exp Range':>14}"
    f"{'Range Δ %':>12}"
)

for joint, label in zip(JOINTS, LABELS):
    br = b["positions"][joint]["range"]
    er = e["positions"][joint]["range"]

    lines.append(
        f"{label:<20}"
        f"{br:>14.6f}"
        f"{er:>14.6f}"
        f"{pct(br, er):>12.2f}"
    )

lines.append("")
lines.append("VELOCITY COMPARISON")
lines.append("-" * 80)
lines.append(
    f"{'Joint':<20}"
    f"{'Base |v|max':>16}"
    f"{'Exp |v|max':>16}"
    f"{'v Δ %':>12}"
)

for joint, label in zip(JOINTS, LABELS):
    bv = b["velocities"][joint]["max_abs"]
    ev = e["velocities"][joint]["max_abs"]

    lines.append(
        f"{label:<20}"
        f"{bv:>16.6f}"
        f"{ev:>16.6f}"
        f"{pct(bv, ev):>12.2f}"
    )

lines.append("")
lines.append("ACCELERATION COMPARISON")
lines.append("-" * 80)
lines.append(
    f"{'Joint':<20}"
    f"{'Base |a|max':>16}"
    f"{'Exp |a|max':>16}"
    f"{'a Δ %':>12}"
)

for joint, label in zip(JOINTS, LABELS):
    ba = b["accelerations"][joint]["max_abs"]
    ea = e["accelerations"][joint]["max_abs"]

    lines.append(
        f"{label:<20}"
        f"{ba:>16.6f}"
        f"{ea:>16.6f}"
        f"{pct(ba, ea):>12.2f}"
    )

lines.append("")
lines.append("INTERPRETATION")
lines.append("-" * 80)
lines.append(
    "The experiment changes only the shoulder_link mass from 3.7000 kg "
    "to 4.0700 kg (+10%)."
)
lines.append(
    "Upper-arm and forearm masses remain at their baseline values."
)
lines.append(
    "Position, velocity and acceleration metrics are calculated "
    "independently for the recorded baseline and experiment trials."
)

lines.append("")
lines.append("NOTE")
lines.append("-" * 80)
lines.append(
    "Acceleration is numerically derived from position using two successive "
    "numpy.gradient() operations."
)
lines.append(
    "The two recordings have slightly different durations and sample counts."
)
lines.append(
    "Therefore this comparison evaluates recorded trajectory statistics, "
    "not point-by-point synchronized trajectory error."
)

lines.append("")
lines.append("=" * 80)
lines.append("END OF EXPERIMENT 03 ANALYSIS")
lines.append("=" * 80)

text = "\n".join(lines) + "\n"

OUT.write_text(text)

print("=" * 80)
print("UR5 EXPERIMENT 03 — ANALYSIS COMPLETE")
print("=" * 80)
print(f"Baseline dataset  : {BASELINE}")
print(f"Experiment dataset: {EXPERIMENT}")
print(f"Results           : {OUT}")
print("=" * 80)
