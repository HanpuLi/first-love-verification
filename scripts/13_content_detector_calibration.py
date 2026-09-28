#!/usr/bin/env python3
"""Calibrate PySceneDetect ContentDetector across the two source copies.

The calibration interval is a stretch known from the 2026-08-26 audio alignment
to be present in both copies without an intervening ad/delete discontinuity:

    92.9-minute copy: 1260.0-1500.0 s
    FilmFour copy:    1817.8-2047.9 s

The two tables deliberately use reciprocal operational reference sets:
- 92.9-copy threshold 27.0 as the reference for FilmFour threshold sensitivity.
- FilmFour threshold 18.0 as the reference for 92.9-copy threshold sensitivity.

These are detector-calibration reference sets, not manually annotated ground truth.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import scenedetect
from scenedetect import SceneManager, open_video
from scenedetect.detectors import ContentDetector

COPY_A_START, COPY_A_END = 1260.0, 1500.0
COPY_B_START, COPY_B_END = 1817.8, 2047.9
RATE = 1.0416666
RATE_CORRECTED_OFFSET = 633.4
MATCH_TOLERANCE_S = 0.6


def cuts(path: Path, start: float, end: float, threshold: float) -> list[float]:
    if not path.is_file():
        raise FileNotFoundError(f"missing analysis input: {path}")
    video = open_video(str(path))
    manager = SceneManager()
    manager.add_detector(ContentDetector(threshold=threshold))
    video.seek(start)
    manager.detect_scenes(video, end_time=end)
    return [scene[0].seconds for scene in manager.get_scene_list()][1:]


def match(reference: list[float], observed: list[float]) -> dict:
    matched = 0
    used: set[int] = set()
    for expected in reference:
        best = None
        for index, actual in enumerate(observed):
            if index in used:
                continue
            if abs(actual - expected) < MATCH_TOLERANCE_S and (
                best is None
                or abs(actual - expected) < abs(observed[best] - expected)
            ):
                best = index
        if best is not None:
            used.add(best)
            matched += 1

    return {
        "observed_cuts": len(observed),
        "matched": matched,
        "missed": len(reference) - matched,
        "extra": len(observed) - matched,
        "match_rate": matched / len(reference),
    }


def scene_stats(path: Path, start: float, end: float, threshold: float) -> dict:
    video = open_video(str(path))
    manager = SceneManager()
    manager.add_detector(ContentDetector(threshold=threshold))
    video.seek(start)
    manager.detect_scenes(video, end_time=end)
    durations = [
        scene_end.seconds - scene_start.seconds
        for scene_start, scene_end in manager.get_scene_list()
    ]
    if not durations:
        raise RuntimeError(f"no scene segments in {start}-{end} at threshold {threshold}")
    return {
        "threshold": threshold,
        "segments": len(durations),
        "asl_recording_s": sum(durations) / len(durations),
        "asl_rate_corrected_s": (sum(durations) / len(durations)) / 0.96,
        "longest_s": max(durations),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--copy-a", type=Path, default=Path("first_love.mp4"))
    parser.add_argument(
        "--copy-b",
        type=Path,
        default=Path("first_love_FilmFour_2026-01-12.mp4"),
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    reference_a = cuts(args.copy_a, COPY_A_START, COPY_A_END, 27.0)
    predicted_on_b = [
        (cut + RATE_CORRECTED_OFFSET) / RATE for cut in reference_a
    ]
    b_thresholds = {}
    for threshold in (27.0, 22.0, 18.0, 15.0, 12.0, 10.0, 8.0, 6.0):
        observed = cuts(args.copy_b, COPY_B_START, COPY_B_END, threshold)
        b_thresholds[f"{threshold:.1f}"] = match(predicted_on_b, observed)

    reference_b = cuts(args.copy_b, COPY_B_START, COPY_B_END, 18.0)
    predicted_on_a = [
        cut * RATE - RATE_CORRECTED_OFFSET for cut in reference_b
    ]
    a_thresholds = {}
    for threshold in (27.0, 22.0, 18.0, 15.0):
        observed = cuts(args.copy_a, COPY_A_START, COPY_A_END, threshold)
        a_thresholds[f"{threshold:.1f}"] = match(predicted_on_a, observed)

    # This complete-broadcast window was fixed in the same audit after timebase
    # mapping. It is retained here as a sensitivity check, not as a unique
    # detector-independent estimate of the sequence's "true" ASL.
    full_melee_window = (6048.0, 6703.8)
    melee_sensitivity = [
        scene_stats(args.copy_b, *full_melee_window, threshold)
        for threshold in (18.0, 22.0)
    ]

    result = {
        "analysis": "ContentDetector cross-copy calibration",
        "copy_a": args.copy_a.name,
        "copy_b": args.copy_b.name,
        "calibration_interval": {
            "copy_a_s": [COPY_A_START, COPY_A_END],
            "copy_b_s": [COPY_B_START, COPY_B_END],
            "rate": RATE,
            "rate_corrected_offset_s": RATE_CORRECTED_OFFSET,
            "match_tolerance_s": MATCH_TOLERANCE_S,
        },
        "broadcast_against_copy_a_threshold_27_reference": {
            "reference_cuts": len(reference_a),
            "thresholds": b_thresholds,
        },
        "copy_a_against_broadcast_threshold_18_reference": {
            "reference_cuts": len(reference_b),
            "thresholds": a_thresholds,
        },
        "complete_broadcast_melee_sensitivity": {
            "window_s": list(full_melee_window),
            "note": (
                "Window coordinates were fixed in the 2026-08-26 timebase audit; "
                "this table tests detector sensitivity within that fixed window."
            ),
            "results": melee_sensitivity,
        },
        "environment": {
            "python": sys.version.split()[0],
            "scenedetect": scenedetect.__version__,
        },
    }

    print(
        "FilmFour threshold 27.0 vs copy-A@27 reference:",
        b_thresholds["27.0"],
    )
    print(
        "FilmFour threshold 18.0 vs copy-A@27 reference:",
        b_thresholds["18.0"],
    )
    print(
        "92.9 copy threshold 27.0 vs FilmFour@18 reference:",
        a_thresholds["27.0"],
    )
    print(
        "92.9 copy threshold 22.0 vs FilmFour@18 reference:",
        a_thresholds["22.0"],
    )
    for item in melee_sensitivity:
        print(
            f"complete broadcast threshold {item['threshold']:.1f}: "
            f"{item['segments']} segments, "
            f"ASL={item['asl_recording_s']:.4f}s recording / "
            f"{item['asl_rate_corrected_s']:.4f}s rate-corrected"
        )

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(result, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"saved {args.output}")


if __name__ == "__main__":
    main()
