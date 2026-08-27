#!/usr/bin/env python3

import csv
from pathlib import Path
import rosbag2_py
from rclpy.serialization import deserialize_message
from sensor_msgs.msg import JointState

BASE = Path(__file__).resolve().parent
OUTPUT = BASE / "data"

BAGS = {
    "baseline_8.393_2.330kg":
        BASE.parent / "baseline_8kg" / "baseline_bag",

    "exp03_shoulder_4.070kg":
        BASE / "experiment_bag",
}

JOINTS = [
    "shoulder_pan_joint",
    "shoulder_lift_joint",
    "elbow_joint",
    "wrist_1_joint",
    "wrist_2_joint",
    "wrist_3_joint",
]

OUTPUT.mkdir(parents=True, exist_ok=True)


def extract(name, bag):
    print("=" * 72)
    print(f"EXTRACTING: {name}")
    print(f"BAG: {bag}")
    print("=" * 72)

    storage = rosbag2_py.StorageOptions(
        uri=str(bag),
        storage_id="sqlite3"
    )

    converter = rosbag2_py.ConverterOptions(
        input_serialization_format="cdr",
        output_serialization_format="cdr"
    )

    reader = rosbag2_py.SequentialReader()
    reader.open(storage, converter)

    rows = []
    first_time = None

    while reader.has_next():
        topic, data, timestamp = reader.read_next()

        if topic != "/joint_states":
            continue

        msg = deserialize_message(data, JointState)

        if first_time is None:
            first_time = timestamp

        row = {
            "time": (timestamp - first_time) / 1e9
        }

        positions = dict(zip(msg.name, msg.position))

        for joint in JOINTS:
            row[f"{joint}_pos"] = positions.get(joint, float("nan"))

        rows.append(row)

    output = OUTPUT / f"{name}.csv"

    fields = ["time"] + [
        f"{joint}_pos"
        for joint in JOINTS
    ]

    with open(output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    duration = rows[-1]["time"] if rows else 0.0

    print(f"Samples  : {len(rows)}")
    print(f"Duration : {duration:.6f} s")
    print(f"CSV      : {output}")
    print()


for name, bag in BAGS.items():
    extract(name, bag)

print("=" * 72)
print("EXP 03 EXTRACTION COMPLETE")
print("=" * 72)
