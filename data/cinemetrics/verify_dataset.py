#!/usr/bin/env python3
"""Check the public 17-shot CSV and FACT export without access to the film.

This checks transcription, arithmetic, frame alignment and agreement between
files. It cannot establish whether a marked boundary is an actual film edit.
"""
from __future__ import annotations

import csv
import json
from decimal import Decimal, InvalidOperation
from pathlib import Path
from statistics import median

HERE = Path(__file__).resolve().parent
CSV = HERE / "first-love-betrayal-filmfour-17-shots.csv"
CMSX = HERE / "first-love-betrayal-corrected.cmsx"
FPS = 25
EXPECTED_COUNT = 17
EXPECTED_START_FRAME = 53761
EXPECTED_END_FRAME = 57458


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def number(value: object, field: str) -> Decimal:
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError(f"invalid decimal {field}: {value!r}") from None
    require(result.is_finite(), f"non-finite decimal {field}")
    return result


def frame(value: Decimal, field: str) -> int:
    frame_value = value * FPS
    require(frame_value == frame_value.to_integral_value(),
            f"{field} does not fall on a {FPS} fps frame: {value}")
    return int(frame_value)


def verify(rows: list[dict[str, str]], export: dict) -> dict:
    require(len(rows) == EXPECTED_COUNT,
            f"CSV must contain {EXPECTED_COUNT} complete shots; got {len(rows)}")
    shots: list[tuple[int, int, Decimal]] = []
    for index, row in enumerate(rows, 1):
        require(int(row["complete_shot"]) == index, f"shot index mismatch in row {index}")
        start = number(row["source_recording_start_s"], f"start of shot {index}")
        end = number(row["source_recording_end_s"], f"end of shot {index}")
        duration = number(row["duration_s"], f"duration of shot {index}")
        start_frame = int(row["frame_start_at_25fps"])
        end_frame = int(row["frame_end_at_25fps"])
        require(end > start, f"shot {index} has no positive duration")
        require(duration == end - start, f"shot {index} duration does not match boundaries")
        require(start_frame == frame(start, f"shot {index} start") and
                end_frame == frame(end, f"shot {index} end"),
                f"shot {index} frame indices disagree with timecodes")
        require(end_frame - start_frame == frame(duration, f"shot {index} duration"),
                f"shot {index} frame duration mismatch")
        if shots:
            require(start_frame == shots[-1][1], f"gap or overlap before shot {index}")
        shots.append((start_frame, end_frame, duration))

    require(shots[0][0] == EXPECTED_START_FRAME, "unexpected first complete cut")
    require(shots[-1][1] == EXPECTED_END_FRAME, "unexpected final complete cut")
    total_frames = shots[-1][1] - shots[0][0]
    duration = Decimal(total_frames) / FPS
    require(duration == Decimal("147.88"), "unexpected complete-shot window")
    require(sum((s[2] for s in shots), Decimal(0)) == duration,
            "shot durations do not sum to the complete-shot window")

    require(export.get("tool") == "fact", "export is not marked as FACT")
    require(export.get("year") == "2019", "export film year mismatch")
    require(export.get("imdb") == "tt10228168", "export film identifier mismatch")
    require("EXCERPT ONLY" in export.get("comment", ""), "missing excerpt disclosure")
    markers = export.get("shotMarkers")
    require(isinstance(markers, list) and len(markers) == EXPECTED_COUNT,
            "FACT export must have exactly 17 shot-end markers")
    for index, (shot, marker) in enumerate(zip(shots, markers), 1):
        require(marker.get("typeIdx") == 0,
                f"shot {index} unexpectedly assigned a shot-scale category")
        timestamp = number(marker.get("ts"), f"FACT marker {index}")
        expected = Decimal(shot[1] - EXPECTED_START_FRAME) / FPS
        require(abs(timestamp - expected) < Decimal("0.005"),
                f"FACT marker {index} disagrees with CSV ({timestamp} versus {expected})")
    # FACT also writes a truncated, decisecond-precision legacy string. It is
    # checked for consistency, but never used to recalculate frame times.
    legacy = export.get("markers", "")
    parsed = [part.split(",", 1)[0] for part in legacy.split(";") if part]
    require(len(parsed) == EXPECTED_COUNT, "legacy marker count mismatch")
    for index, (marker, decisecond) in enumerate(zip(markers, parsed), 1):
        tick = number(decisecond, f"legacy marker {index}")
        require(tick == tick.to_integral_value(), f"legacy marker {index} is not an integer")
        expected_tick = int(number(marker["ts"], "timestamp") * 10)
        require(int(tick) == expected_tick, f"legacy marker {index} is inconsistent")

    lengths = [s[2] for s in shots]
    return {
        "shots": len(shots),
        "source_fps": FPS,
        "source_window_s": [str(Decimal(shots[0][0]) / FPS),
                            str(Decimal(shots[-1][1]) / FPS)],
        "duration_s": str(duration),
        "average_shot_length_s": str(duration / EXPECTED_COUNT),
        "median_shot_length_s": str(median(lengths)),
        "min_s": str(min(lengths)),
        "max_s": str(max(lengths)),
        "fact_markers": len(markers),
        "result": "arithmetic_and_export_consistent",
    }


def audit(csv_path: Path = CSV, cmsx_path: Path = CMSX) -> dict:
    with csv_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    with cmsx_path.open(encoding="utf-8") as handle:
        export = json.load(handle)
    return verify(rows, export)


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2))
