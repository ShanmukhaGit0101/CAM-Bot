#!/usr/bin/env python3

import pandas as pd
import numpy as np
from pathlib import Path

BASE = Path(__file__).resolve().parent
DATA = BASE / "data" / "exp02_forearm_2.563kg.csv"
RESULTS = BASE / "results"
RESULTS.mkdir(parents=True, exist_ok=True)

OUT = RESULTS / "exp02_forearm_mass_10pct_analysis.txt"

df = pd.read_csv(DATA)

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

t = df["time"].to_numpy(dtype=float)
t = t - t[0]

lines = []

def add(x=""):
    print(x)
    lines.append(str(x))

add("=" * 72)
add("UR5 EXPERIMENT 02 — FOREARM MASS +10%")
add("=" * 72)
add("")
add("EXPERIMENT")
add("-" * 72)
add("Baseline forearm mass : 2.3300 kg")
add("Modified forearm mass : 2.5630 kg")
add("Mass increase         : +0.2330 kg")
add("Percentage increase   : +10.00%")
add("")

add("DATASET")
add("-" * 72)
add(f"Source file : {DATA}")
add(f"Samples     : {len(df)}")
add(f"Duration    : {t[-1]:.6f} s")

dt = np.diff(t)

add(f"Mean dt     : {np.mean(dt):.9f} s")
add(f"Min dt      : {np.min(dt):.9f} s")
add(f"Max dt      : {np.max(dt):.9f} s")
add(f"Rate        : {1.0 / np.mean(dt):.3f} Hz")
add("")

add("JOINT POSITION ANALYSIS")
add("-" * 72)
add(
    f"{'Joint':20s}"
    f"{'Minimum (rad)':>18s}"
    f"{'Maximum (rad)':>18s}"
    f"{'Range (rad)':>16s}"
)

for joint, label in zip(joints, labels):
    x = df[f"{joint}_pos"].to_numpy(dtype=float)

    mn = np.min(x)
    mx = np.max(x)
    rng = mx - mn

    add(
        f"{label:20s}"
        f"{mn:18.6f}"
        f"{mx:18.6f}"
        f"{rng:16.6f}"
    )

add("")
add("JOINT VELOCITY ANALYSIS")
add("-" * 72)
add(
    f"{'Joint':20s}"
    f"{'Minimum (rad/s)':>20s}"
    f"{'Maximum (rad/s)':>20s}"
    f"{'Max |v| (rad/s)':>20s}"
)

velocity_data = {}

for joint, label in zip(joints, labels):
    col = f"{joint}_pos"

    x = df[col].to_numpy(dtype=float)

    v = np.gradient(x, t)
    velocity_data[joint] = v

    mn = np.min(v)
    mx = np.max(v)
    max_abs = np.max(np.abs(v))

    add(
        f"{label:20s}"
        f"{mn:20.6f}"
        f"{mx:20.6f}"
        f"{max_abs:20.6f}"
    )

add("")
add("DERIVED JOINT ACCELERATION ANALYSIS")
add("-" * 72)
add(
    f"{'Joint':20s}"
    f"{'Minimum (rad/s²)':>20s}"
    f"{'Maximum (rad/s²)':>20s}"
    f"{'Max |a| (rad/s²)':>20s}"
)

for joint, label in zip(joints, labels):
    v = velocity_data[joint]

    a = np.gradient(v, t)

    mn = np.min(a)
    mx = np.max(a)
    max_abs = np.max(np.abs(a))

    add(
        f"{label:20s}"
        f"{mn:20.6f}"
        f"{mx:20.6f}"
        f"{max_abs:20.6f}"
    )

add("")
add("JOINT START / END VALUES")
add("-" * 72)

for joint, label in zip(joints, labels):
    x = df[f"{joint}_pos"].to_numpy(dtype=float)

    add(
        f"{label:20s}"
        f"start={x[0]: .6f} rad   "
        f"end={x[-1]: .6f} rad"
    )

add("")
add("NOTES")
add("-" * 72)
add("Position values are taken directly from the recorded /joint_states dataset.")
add("Velocity is numerically derived from joint position using numpy.gradient().")
add("Acceleration is numerically derived from the calculated velocity.")
add("This is Experiment 02 with forearm mass increased by 10%.")
add("The corresponding baseline dataset is the 2.3300 kg forearm trial.")
add("")
add("=" * 72)
add("END OF EXPERIMENT 02 ANALYSIS")
add("=" * 72)

OUT.write_text("\n".join(lines) + "\n")

print("")
print("=" * 72)
print("EXPERIMENT 02 ANALYSIS COMPLETE")
print("=" * 72)
print(f"Results saved : {OUT}")
print("=" * 72)
