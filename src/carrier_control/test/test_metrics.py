"""Offline evidence-integrity tests for trial records."""

import csv
from pathlib import Path
import tempfile
import unittest

from carrier_control.metrics import TrialRecordError, append_trial, validate_trial_record


def visual_record():
    return {
        "schema_version": "1.0",
        "trial_id": "visual-001",
        "timestamp_utc": "2026-10-15T00:00:00Z",
        "mode": "visual_simulation",
        "cycle_time_s": 1.25,
        "success": True,
        "failure_stage": None,
        "carrier_motion_count": 0,
        "carrier_joint_travel_rad": None,
        "workpiece_final_state": "FINISHED_AT_S5",
        "runtime_verified": False,
        "end_to_end_verified": False,
        "notes": "visual state-machine exercise only",
    }


class TestMetrics(unittest.TestCase):
    def test_positive_append_writes_one_header_and_rows(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "trials.csv"
            append_trial(path, visual_record())
            append_trial(path, {**visual_record(), "trial_id": "visual-002"})
            with path.open(newline="", encoding="utf-8") as stream:
                rows = list(csv.DictReader(stream))
            self.assertEqual([row["trial_id"] for row in rows], ["visual-001", "visual-002"])

    def test_negative_visual_mode_cannot_claim_runtime_verification(self):
        record = {**visual_record(), "runtime_verified": True}
        with self.assertRaisesRegex(TrialRecordError, "visual simulation"):
            validate_trial_record(record)

    def test_negative_visual_mode_cannot_claim_joint_travel(self):
        record = {**visual_record(), "carrier_joint_travel_rad": 2.5}
        with self.assertRaisesRegex(TrialRecordError, "cannot claim carrier joint travel"):
            validate_trial_record(record)


if __name__ == "__main__":
    unittest.main()
