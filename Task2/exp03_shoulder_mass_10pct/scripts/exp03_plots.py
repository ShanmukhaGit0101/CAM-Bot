#!/usr/bin/env python3

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

BASE = Path(__file__).resolve().parent
DATA = BASE / "data"
PLOTS = BASE / "plots"

PLOTS.mkdir(exist_ok=True)

baseline = pd.read_csv(DATA / "baseline_8.393_2.330kg.csv")
experiment = pd.read_csv(DATA / "exp03_shoulder_4.070kg.csv")

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


def get_data(df):
    t = df["time"].to_numpy()
    t -= t[0]

    positions = {}
    velocities = {}
    accelerations = {}

    for joint in joints:
        q = df[f"{joint}_pos"].to_numpy()
        v = np.gradient(q, t)
        a = np.gradient(v, t)

        positions[joint] = q
        velocities[joint] = v
        accelerations[joint] = a

    return t, positions, velocities, accelerations


tb, pb, vb, ab = get_data(baseline)
te, pe, ve, ae = get_data(experiment)

# 1. POSITION
plt.figure(figsize=(12, 7))

for joint, label in zip(joints, labels):
    plt.plot(tb, pb[joint], label=f"{label} — Baseline")
    plt.plot(te, pe[joint], "--", label=f"{label} — Exp 03")

plt.xlabel("Time (s)")
plt.ylabel("Joint Position (rad)")
plt.title("UR5 Exp 03 — Joint Position Comparison")
plt.legend(fontsize=8)
plt.grid(True)
plt.tight_layout()
plt.savefig(PLOTS / "exp03_joint_positions_comparison.png", dpi=200)
plt.close()

# 2. VELOCITY
plt.figure(figsize=(12, 7))

for joint, label in zip(joints, labels):
    plt.plot(tb, vb[joint], label=f"{label} — Baseline")
    plt.plot(te, ve[joint], "--", label=f"{label} — Exp 03")

plt.xlabel("Time (s)")
plt.ylabel("Joint Velocity (rad/s)")
plt.title("UR5 Exp 03 — Joint Velocity Comparison")
plt.legend(fontsize=8)
plt.grid(True)
plt.tight_layout()
plt.savefig(PLOTS / "exp03_joint_velocities_comparison.png", dpi=200)
plt.close()

# 3. ACCELERATION
plt.figure(figsize=(12, 7))

for joint, label in zip(joints, labels):
    plt.plot(tb, ab[joint], label=f"{label} — Baseline")
    plt.plot(te, ae[joint], "--", label=f"{label} — Exp 03")

plt.xlabel("Time (s)")
plt.ylabel("Joint Acceleration (rad/s²)")
plt.title("UR5 Exp 03 — Derived Joint Acceleration Comparison")
plt.legend(fontsize=8)
plt.grid(True)
plt.tight_layout()
plt.savefig(PLOTS / "exp03_joint_accelerations_comparison.png", dpi=200)
plt.close()

# 4. POSITION RANGE
base_ranges = [
    np.ptp(pb[j]) for j in joints
]

exp_ranges = [
    np.ptp(pe[j]) for j in joints
]

x = np.arange(len(joints))
width = 0.35

plt.figure(figsize=(12, 7))

plt.bar(x - width / 2, base_ranges, width, label="Baseline")
plt.bar(x + width / 2, exp_ranges, width, label="Exp 03")

plt.xticks(x, labels)
plt.xlabel("Joint")
plt.ylabel("Position Range (rad)")
plt.title("UR5 Exp 03 — Joint Position Range Comparison")
plt.legend()
plt.grid(axis="y")
plt.tight_layout()
plt.savefig(PLOTS / "exp03_joint_range_comparison.png", dpi=200)
plt.close()

print("=" * 72)
print("UR5 EXPERIMENT 03 — PLOTS COMPLETE")
print("=" * 72)
print(f"Plots saved: {PLOTS}")
print("=" * 72)
