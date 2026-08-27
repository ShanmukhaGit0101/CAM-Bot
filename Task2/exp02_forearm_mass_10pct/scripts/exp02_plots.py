#!/usr/bin/env python3

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

BASE = Path(__file__).resolve().parent
DATA = BASE / "data"
PLOTS = BASE / "plots"

PLOTS.mkdir(parents=True, exist_ok=True)

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

# Normalize time independently to each recording.
tb = baseline["time"].to_numpy()
te = experiment["time"].to_numpy()

tb = tb - tb[0]
te = te - te[0]

# ============================================================
# 1. JOINT POSITIONS
# ============================================================

plt.figure(figsize=(12, 7))

for joint, label in zip(joints, labels):
    plt.plot(
        tb,
        baseline[f"{joint}_pos"].to_numpy(),
        label=f"{label} — Baseline"
    )
    plt.plot(
        te,
        experiment[f"{joint}_pos"].to_numpy(),
        linestyle="--",
        label=f"{label} — +10% Forearm"
    )

plt.xlabel("Time (s)")
plt.ylabel("Joint Position (rad)")
plt.title("Exp 02 — Joint Position Comparison")
plt.legend(ncol=2, fontsize=8)
plt.grid(True)
plt.tight_layout()
plt.savefig(PLOTS / "exp02_joint_positions_comparison.png", dpi=200)
plt.close()

# ============================================================
# 2. DERIVED JOINT VELOCITIES
# ============================================================

plt.figure(figsize=(12, 7))

for joint, label in zip(joints, labels):

    qb = baseline[f"{joint}_pos"].to_numpy()
    qe = experiment[f"{joint}_pos"].to_numpy()

    vb = np.gradient(qb, tb)
    ve = np.gradient(qe, te)

    plt.plot(
        tb,
        vb,
        label=f"{label} — Baseline"
    )

    plt.plot(
        te,
        ve,
        linestyle="--",
        label=f"{label} — +10% Forearm"
    )

plt.xlabel("Time (s)")
plt.ylabel("Joint Velocity (rad/s)")
plt.title("Exp 02 — Derived Joint Velocity Comparison")
plt.legend(ncol=2, fontsize=8)
plt.grid(True)
plt.tight_layout()
plt.savefig(PLOTS / "exp02_joint_velocities_comparison.png", dpi=200)
plt.close()

# ============================================================
# 3. DERIVED JOINT ACCELERATIONS
# ============================================================

plt.figure(figsize=(12, 7))

for joint, label in zip(joints, labels):

    qb = baseline[f"{joint}_pos"].to_numpy()
    qe = experiment[f"{joint}_pos"].to_numpy()

    vb = np.gradient(qb, tb)
    ve = np.gradient(qe, te)

    ab = np.gradient(vb, tb)
    ae = np.gradient(ve, te)

    plt.plot(
        tb,
        ab,
        label=f"{label} — Baseline"
    )

    plt.plot(
        te,
        ae,
        linestyle="--",
        label=f"{label} — +10% Forearm"
    )

plt.xlabel("Time (s)")
plt.ylabel("Joint Acceleration (rad/s²)")
plt.title("Exp 02 — Derived Joint Acceleration Comparison")
plt.legend(ncol=2, fontsize=8)
plt.grid(True)
plt.tight_layout()
plt.savefig(PLOTS / "exp02_joint_accelerations_comparison.png", dpi=200)
plt.close()

# ============================================================
# 4. POSITION RANGE COMPARISON
# ============================================================

baseline_ranges = []
experiment_ranges = []

for joint in joints:
    b = baseline[f"{joint}_pos"].to_numpy()
    e = experiment[f"{joint}_pos"].to_numpy()

    baseline_ranges.append(np.max(b) - np.min(b))
    experiment_ranges.append(np.max(e) - np.min(e))

x = np.arange(len(joints))
width = 0.38

plt.figure(figsize=(12, 7))

plt.bar(
    x - width / 2,
    baseline_ranges,
    width,
    label="Baseline"
)

plt.bar(
    x + width / 2,
    experiment_ranges,
    width,
    label="+10% Forearm"
)

plt.xticks(x, labels)
plt.xlabel("Joint")
plt.ylabel("Position Range (rad)")
plt.title("Exp 02 — Joint Position Range Comparison")
plt.legend()
plt.grid(True, axis="y")
plt.tight_layout()
plt.savefig(PLOTS / "exp02_joint_range_comparison.png", dpi=200)
plt.close()

print("=" * 72)
print("UR5 EXPERIMENT 02 — PLOTS COMPLETE")
print("=" * 72)
print(f"Baseline dataset : {DATA / 'baseline_2.330kg.csv'}")
print(f"Experiment dataset: {DATA / 'exp02_forearm_2.563kg.csv'}")
print(f"Plots saved       : {PLOTS}")
print("=" * 72)
