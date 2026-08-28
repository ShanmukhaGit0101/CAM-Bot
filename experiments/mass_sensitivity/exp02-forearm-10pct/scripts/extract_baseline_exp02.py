#!/usr/bin/env python3

import csv
from pathlib import Path

import rosbag2_py
from rclpy.serialization import deserialize_message
from sensor_msgs.msg import JointState

BASE = Path(__file__).resolve().parent

BAG = BASE.parent / "baseline_8kg" / "baseline_bag"
OUT = BASE / "data" / "baseline_2.330kg.csv"

JOINTS = [
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

topic_types = reader.get_all_topics_and_types()

type_map = {x.name: x.type for x in topic_types}

if "/joint_states" not in type_map:
    raise RuntimeError("/joint_states not found in baseline bag")

rows = []

first_time = None

while reader.has_next():
    topic, data, timestamp = reader.read_next()

    if topic != "/joint_states":
        continue

    msg = deserialize_message(data, JointState)

    values = dict(zip(msg.name, msg.position))

    if not all(j in values for j in JOINTS):
        continue

    t = timestamp / 1e9

    if first_time is None:
        first_time = t

    t -= first_time

    rows.append([
        t,
        *[values[j] for j in JOINTS]
    ])

OUT.parent.mkdir(parents=True, exist_ok=True)

with OUT.open("w", newline="") as f:
    writer = csv.writer(f)

    writer.writerow([
        "time",
        *[f"{j}_pos" for j in JOINTS]
    ])

    writer.writerows(rows)

print("=" * 72)
print("EXP 02 BASELINE EXTRACTION COMPLETE")
print("=" * 72)
print(f"Samples  : {len(rows)}")
print(f"Duration : {rows[-1][0]:.6f} s")
print(f"CSV      : {OUT}")
print("=" * 72)
