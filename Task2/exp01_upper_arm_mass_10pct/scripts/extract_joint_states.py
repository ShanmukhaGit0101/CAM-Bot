#!/usr/bin/env python3

import csv
from pathlib import Path
import rosbag2_py
from rclpy.serialization import deserialize_message
from sensor_msgs.msg import JointState

BASE = Path(__file__).resolve().parent

BAGS = {
    "baseline_8.393kg": BASE.parent / "baseline_8kg" / "baseline_bag",
    "experiment_9.2323kg": BASE / "experiment_bag",
}

OUTPUT = BASE / "data"
OUTPUT.mkdir(parents=True, exist_ok=True)

EXPECTED_JOINTS = [
    "shoulder_pan_joint",
    "shoulder_lift_joint",
    "elbow_joint",
    "wrist_1_joint",
    "wrist_2_joint",
    "wrist_3_joint",
]


def extract(label, bag_path):
    print("=" * 72)
    print(f"EXTRACTING: {label}")
    print(f"BAG: {bag_path}")
    print("=" * 72)

    reader = rosbag2_py.SequentialReader()

    storage_options = rosbag2_py.StorageOptions(
        uri=str(bag_path),
        storage_id="sqlite3",
    )

    converter_options = rosbag2_py.ConverterOptions(
        input_serialization_format="cdr",
        output_serialization_format="cdr",
    )

    reader.open(storage_options, converter_options)

    output_file = OUTPUT / f"{label}.csv"

    rows = []
    first_timestamp = None

    while reader.has_next():
        topic, data, timestamp = reader.read_next()

        if topic != "/joint_states":
            continue

        msg = deserialize_message(data, JointState)

        if first_timestamp is None:
            first_timestamp = timestamp

        t = (timestamp - first_timestamp) / 1e9

        values = {
            name: (msg.position[i], msg.velocity[i], msg.effort[i])
            for i, name in enumerate(msg.name)
            if i < len(msg.position)
        }

        row = {"time": t}

        for joint in EXPECTED_JOINTS:
            pos, vel, effort = values.get(joint, (float("nan"), float("nan"), float("nan")))

            row[f"{joint}_pos"] = pos
            row[f"{joint}_vel"] = vel
            row[f"{joint}_eff"] = effort

        rows.append(row)

    fields = ["time"]

    for joint in EXPECTED_JOINTS:
        fields += [
            f"{joint}_pos",
            f"{joint}_vel",
            f"{joint}_eff",
        ]

    with open(output_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    duration = rows[-1]["time"] if rows else 0.0

    print(f"Samples  : {len(rows)}")
    print(f"Duration : {duration:.6f} s")
    print(f"CSV      : {output_file}")
    print()


for label, bag in BAGS.items():
    extract(label, bag)

print("=" * 72)
print("JOINT-STATE EXTRACTION COMPLETE")
print("=" * 72)
