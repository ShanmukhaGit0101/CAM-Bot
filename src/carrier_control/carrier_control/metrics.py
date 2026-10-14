"""Machine-tending trial record validation and append-only CSV output."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Dict


FIELDS = (
    "schema_version",
    "trial_id",
    "timestamp_utc",
    "mode",
    "cycle_time_s",
    "success",
    "failure_stage",
    "carrier_motion_count",
    "carrier_joint_travel_rad",
    "workpiece_final_state",
    "runtime_verified",
    "end_to_end_verified",
    "notes",
)


class TrialRecordError(ValueError):
    """Raised when evidence would overstate the verification achieved."""


def validate_trial_record(record: Dict[str, Any]) -> None:
    missing = [field for field in FIELDS[:-1] if field not in record]
    extra = sorted(set(record) - set(FIELDS))
    if missing or extra:
        raise TrialRecordError(f"record fields invalid; missing={missing}, extra={extra}")
    if record["schema_version"] != "1.0":
        raise TrialRecordError("schema_version must be '1.0'")
    if record["mode"] not in ("controller", "visual_simulation"):
        raise TrialRecordError("mode must be controller or visual_simulation")
    if record["cycle_time_s"] < 0 or record["carrier_motion_count"] < 0:
        raise TrialRecordError("times and counts cannot be negative")
    if record["mode"] == "visual_simulation":
        if record["runtime_verified"] or record["end_to_end_verified"]:
            raise TrialRecordError("visual simulation cannot be runtime/end-to-end verified")
        if record["carrier_joint_travel_rad"] is not None:
            raise TrialRecordError("visual simulation cannot claim carrier joint travel")
    if record["end_to_end_verified"] and not (
            record["mode"] == "controller"
            and record["success"]
            and record["runtime_verified"]):
        raise TrialRecordError(
            "end-to-end verification requires successful controller runtime evidence"
        )


def append_trial(path: Path | str, record: Dict[str, Any]) -> None:
    """Validate then append a record, creating a header when needed."""
    validate_trial_record(record)
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    needs_header = not output.exists() or output.stat().st_size == 0
    with output.open("a", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, extrasaction="raise")
        if needs_header:
            writer.writeheader()
        writer.writerow({field: record.get(field, "") for field in FIELDS})
