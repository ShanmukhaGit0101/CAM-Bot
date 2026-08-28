#!/usr/bin/env python3

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

BASE = Path(__file__).resolve().parent
DATA = BASE / "data"
PLOTS = BASE / "plots"

PLOTS.mkdir(parents=True, exist_ok=True)

FILES = {
    "Baseline — 8.393 kg": DATA / "baseline_8.393kg.csv",
    "Experiment — 9.2323 kg": DATA / "experiment_9.2323kg.csv",
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


datasets = {}

for name, path in FILES.items():
    df = pd.read_csv(path)

    t = df["time"].to_numpy(dtype=float)
    t = t - t[0]

    datasets[name] = (df, t)


# ============================================================
# 1. JOINT POSITIONS
# ============================================================

for joint, label in zip(JOINTS, LABELS):

    plt.figure(figsize=(12, 6))

    for name, (df, t) in datasets.items():
        plt.plot(
            t,
            df[f"{joint}_pos"].to_numpy(dtype=float),
            label=name
        )

    plt.xlabel("Time (s)")
    plt.ylabel("Joint Position (rad)")
    plt.title(f"UR5 Experiment 01 — {label} Position")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    plt.savefig(
        PLOTS / f"{joint}_position_comparison.png",
        dpi=200
    )
    plt.close()


# ============================================================
# 2. JOINT VELOCITIES
# ============================================================

for joint, label in zip(JOINTS, LABELS):

    plt.figure(figsize=(12, 6))

    for name, (df, t) in datasets.items():
        plt.plot(
            t,
            df[f"{joint}_vel"].to_numpy(dtype=float),
            label=name
        )

    plt.xlabel("Time (s)")
    plt.ylabel("Joint Velocity (rad/s)")
    plt.title(f"UR5 Experiment 01 — {label} Velocity")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    plt.savefig(
        PLOTS / f"{joint}_velocity_comparison.png",
        dpi=200
    )
    plt.close()


# ============================================================
# 3. JOINT ACCELERATIONS
# ============================================================

for joint, label in zip(JOINTS, LABELS):

    plt.figure(figsize=(12, 6))

    for name, (df, t) in datasets.items():

        velocity = df[f"{joint}_vel"].to_numpy(dtype=float)

        acceleration = np.gradient(
            velocity,
            t
        )

        plt.plot(
            t,
            acceleration,
            label=name
        )

    plt.xlabel("Time (s)")
    plt.ylabel("Joint Acceleration (rad/s²)")
    plt.title(f"UR5 Experiment 01 — {label} Acceleration")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    plt.savefig(
        PLOTS / f"{joint}_acceleration_comparison.png",
        dpi=200
    )
    plt.close()


# ============================================================
# 4. ALL JOINT POSITIONS — OVERVIEW
# ============================================================

plt.figure(figsize=(13, 8))

for name, (df, t) in datasets.items():

    for joint, label in zip(JOINTS, LABELS):

        plt.plot(
            t,
            df[f"{joint}_pos"].to_numpy(dtype=float),
            label=f"{name} — {label}"
        )

plt.xlabel("Time (s)")
plt.ylabel("Joint Position (rad)")
plt.title("UR5 Experiment 01 — All Joint Positions")
plt.legend(fontsize=7)
plt.grid(True)
plt.tight_layout()

plt.savefig(
    PLOTS / "all_joint_positions_comparison.png",
    dpi=200
)
plt.close()


# ============================================================
# 5. POSITION RANGE COMPARISON
# ============================================================

ranges = {
    "Baseline — 8.393 kg": [],
    "Experiment — 9.2323 kg": [],
}

for name, (df, t) in datasets.items():

    for joint in JOINTS:

        position = df[f"{joint}_pos"].to_numpy(dtype=float)

        ranges[name].append(
            np.ptp(position)
        )

x = np.arange(len(JOINTS))
width = 0.35

plt.figure(figsize=(12, 6))

plt.bar(
    x - width / 2,
    ranges["Baseline — 8.393 kg"],
    width,
    label="Baseline — 8.393 kg"
)

plt.bar(
    x + width / 2,
    ranges["Experiment — 9.2323 kg"],
    width,
    label="Experiment — 9.2323 kg"
)

plt.xticks(x, LABELS, rotation=20)
plt.xlabel("Joint")
plt.ylabel("Position Range (rad)")
plt.title("UR5 Experiment 01 — Joint Position Range")
plt.legend()
plt.grid(True, axis="y")
plt.tight_layout()

plt.savefig(
    PLOTS / "position_range_comparison.png",
    dpi=200
)
plt.close()


print("=" * 72)
print("UR5 EXPERIMENT 01 COMPARISON PLOTS COMPLETE")
print("=" * 72)
print(f"Plots saved: {PLOTS}")
print("=" * 72)

