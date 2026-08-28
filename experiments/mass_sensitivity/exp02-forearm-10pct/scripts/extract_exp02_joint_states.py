#!/usr/bin/env python3

import csv
from pathlib import Path
import rosbag2_py
from rclpy.serialization import deserialize_message
from sensor_msgs.msg import JointState

BASE = Path(__file__).resolve().parent
BAG = BASE / "experiment_bag"
OUTPUT = BASE / "data" / "exp02_forearm_2.563kg.csv"

EXPECTED_JOINTS = [
    "shoulder_pan_joint",
    "shoulder_lift_joint",
    "elbow_joint",
    "wrist_1_joint",
    "wrist_2_joint",
    "wrist_3_joint",
]

reader = rosbag2_py.SequentialReader()

storage_options = rosbag2_py.StorageOptions(
    uri=str(BAG),
    storage_id="sqlite3"
)

converter_options = rosbag2_py.ConverterOptions(
    input_serialization_format="cdr",
    output_serialization_format="cdr"
)

reader.open(storage_options, converter_options)

rows = []

while reader.has_next():
    topic, data, timestamp = reader.read_next()

    if topic != "/joint_states":
        continue

    msg = deserialize_message(data, JointState)

    joint_map = dict(zip(msg.name, msg.position))

    if not all(j in joint_map for j in EXPECTED_JOINTS):
        continue

    rows.append({
        "time": timestamp / 1e9,
        **{
            f"{joint}_pos": joint_map[joint]
            for joint in EXPECTED_JOINTS
        }
    })

if not rows:
    raise RuntimeError("No valid /joint_states samples found.")

t0 = rows[0]["time"]

for row in rows:
    row["time"] -= t0

OUTPUT.parent.mkdir(parents=True, exist_ok=True)

with open(OUTPUT, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

duration = rows[-1]["time"]

print("=" * 72)
print("UR5 EXPERIMENT 02 — JOINT STATE EXTRACTION")
print("=" * 72)
print(f"Bag      : {BAG}")
print(f"Samples  : {len(rows)}")
print(f"Duration : {duration:.6f} s")
print(f"CSV      : {OUTPUT}")
print("=" * 72)
