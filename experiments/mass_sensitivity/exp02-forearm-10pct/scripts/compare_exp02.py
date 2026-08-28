#!/usr/bin/env python3

import pandas as pd
import numpy as np
from pathlib import Path

BASE = Path(__file__).resolve().parent
DATA = BASE / "data"
RESULTS = BASE / "results"
RESULTS.mkdir(exist_ok=True)

baseline = pd.read_csv(DATA / "baseline_2.330kg.csv")
experiment = pd.read_csv(DATA / "exp02_forearm_2.563kg.csv")

joints = [
    "shoulder_pan_joint",
    "shoulder_lift_joint",
    "elbow_joint",
    "wrist_1_joint",
    "wrist_2_joint",
    "wrist_3_joint",
]

labels = [
    "Shoulder Pan",
    "Shoulder Lift",
    "Elbow",
    "Wrist 1",
    "Wrist 2",
    "Wrist 3",
]

def metrics(df):
    t = df["time"].to_numpy(dtype=float)
    t -= t[0]

    result = {}

    for joint in joints:
        p = df[f"{joint}_pos"].to_numpy(dtype=float)
        v = np.gradient(p, t)
        a = np.gradient(v, t)

        result[joint] = {
            "pos_range": np.ptp(p),
            "max_velocity": np.max(np.abs(v)),
            "max_acceleration": np.max(np.abs(a)),
        }

    return result, t[-1], len(df)

b, b_duration, b_samples = metrics(baseline)
e, e_duration, e_samples = metrics(experiment)

out = RESULTS / "exp02_baseline_vs_forearm_10pct_comparison.txt"

lines = []

def add(s=""):
    print(s)
    lines.append(str(s))

add("=" * 80)
add("UR5 EXPERIMENT 02 — BASELINE vs +10% FOREARM MASS")
add("=" * 80)
add("")
add("MASS CONFIGURATION")
add("-" * 80)
add("Baseline forearm mass : 2.3300 kg")
add("Experiment forearm    : 2.5630 kg")
add("Mass increase         : +0.2330 kg")
add("Percentage increase   : +10.00%")
add("")

add("DATASET")
add("-" * 80)
add(f"Baseline samples      : {b_samples}")
add(f"Experiment samples    : {e_samples}")
add(f"Baseline duration     : {b_duration:.6f} s")
add(f"Experiment duration   : {e_duration:.6f} s")
add("")

add("COMPARISON")
add("-" * 80)
add(
    f"{'Joint':20s}"
    f"{'Base Range':>15s}"
    f"{'Exp Range':>15s}"
    f"{'Range Δ %':>13s}"
    f"{'Base |v|max':>15s}"
    f"{'Exp |v|max':>15s}"
    f"{'v Δ %':>11s}"
)

for joint, label in zip(joints, labels):

    br = b[joint]["pos_range"]
    er = e[joint]["pos_range"]

    bv = b[joint]["max_velocity"]
    ev = e[joint]["max_velocity"]

    br_pct = ((er - br) / br * 100) if br != 0 else 0.0
    bv_pct = ((ev - bv) / bv * 100) if bv != 0 else 0.0

    add(
        f"{label:20s}"
        f"{br:15.6f}"
        f"{er:15.6f}"
        f"{br_pct:13.2f}"
        f"{bv:15.6f}"
        f"{ev:15.6f}"
        f"{bv_pct:11.2f}"
    )

add("")
add("ACCELERATION COMPARISON")
add("-" * 80)
add(
    f"{'Joint':20s}"
    f"{'Base |a|max':>18s}"
    f"{'Exp |a|max':>18s}"
    f"{'Δ %':>12s}"
)

for joint, label in zip(joints, labels):

    ba = b[joint]["max_acceleration"]
    ea = e[joint]["max_acceleration"]

    pct = ((ea - ba) / ba * 100) if ba != 0 else 0.0

    add(
        f"{label:20s}"
        f"{ba:18.6f}"
        f"{ea:18.6f}"
        f"{pct:12.2f}"
    )

add("")
add("INTERPRETATION")
add("-" * 80)
add("The experiment changes only the forearm mass.")
add("The upper-arm mass remains at the 8.3930 kg baseline value.")
add("Position, velocity and acceleration metrics are calculated independently")
add("for the recorded baseline and modified trials.")
add("")
add("NOTE")
add("-" * 80)
add("Acceleration is numerically derived using numpy.gradient().")
add("The two recordings have slightly different durations and sample counts.")
add("Therefore this comparison evaluates recorded trajectory statistics,")
add("not point-by-point synchronized trajectory error.")
add("")
add("=" * 80)
add("END OF EXPERIMENT 02 COMPARISON")
add("=" * 80)

out.write_text("\n".join(lines) + "\n")

print("")
print("=" * 80)
print("EXP 02 COMPARISON COMPLETE")
print("=" * 80)
print(f"Results saved : {out}")
print("=" * 80)
