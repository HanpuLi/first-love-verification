#!/usr/bin/env python3
"""Local release-to-recording offset from burned-in subtitle activity.

The rate term is fixed at 0.96 recording seconds per release second.  This
script estimates only the local offset in one recording window by correlating:
- a binary burned-in-subtitle activity signal from the FilmFour frames; and
- a binary cue-activity signal from the release SRT.

It does not estimate the 0.96 rate term, establish whole-film linearity, or
bridge retained ad breaks.  Script 12 independently audits the relative rate.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import cv2
import numpy as np

DEFAULT_START, DEFAULT_END = 2100.0, 2400.0
RATE = 0.96
DEFAULT_SEARCH_START = 300.0
DEFAULT_SEARCH_END = 470.0
DEFAULT_SEARCH_STEP = 0.1


def to_sec(value: str) -> float:
    hours, minutes, rest = value.split(":")
    seconds, millis = rest.split(",")
    return (
        int(hours) * 3600
        + int(minutes) * 60
        + int(seconds)
        + int(millis) / 1000
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--video",
        type=Path,
        default=Path("first_love_FilmFour_2026-01-12.mp4"),
    )
    parser.add_argument("--srt", type=Path, default=Path("first_love_en.srt"))
    parser.add_argument("--start", type=float, default=DEFAULT_START)
    parser.add_argument("--end", type=float, default=DEFAULT_END)
    parser.add_argument(
        "--search-start", type=float, default=DEFAULT_SEARCH_START
    )
    parser.add_argument("--search-end", type=float, default=DEFAULT_SEARCH_END)
    parser.add_argument("--search-step", type=float, default=DEFAULT_SEARCH_STEP)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    if not args.video.is_file():
        raise FileNotFoundError(f"missing analysis input: {args.video}")
    if not args.srt.is_file():
        raise FileNotFoundError(f"missing subtitle input: {args.srt}")

    cap = cv2.VideoCapture(str(args.video))
    if not cap.isOpened():
        raise RuntimeError(f"OpenCV could not open video: {args.video}")
    fps = cap.get(cv2.CAP_PROP_FPS)
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    if fps <= 0 or height <= 0 or width <= 0:
        cap.release()
        raise RuntimeError(
            f"invalid video metadata: fps={fps}, width={width}, height={height}"
        )

    cap.set(cv2.CAP_PROP_POS_MSEC, args.start * 1000)
    step = max(1, int(round(fps / 10)))
    times, bright = [], []
    frame_index = 0

    while True:
        ok, image = cap.read()
        if not ok:
            break
        t = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
        if t > args.end:
            break
        if frame_index % step == 0:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            roi = gray[
                int(height * 0.78) : int(height * 0.99),
                int(width * 0.10) : int(width * 0.90),
            ]
            times.append(t)
            bright.append((roi > 205).mean())
        frame_index += 1
    cap.release()

    if not bright:
        raise RuntimeError(
            f"no decodable frames sampled in {args.start}-{args.end} s"
        )

    times_array = np.asarray(times)
    bright_array = np.asarray(bright)
    brightness_threshold = max(0.006, np.percentile(bright_array, 55))
    present = (bright_array > brightness_threshold).astype(float)
    if present.std() < 1e-6:
        raise RuntimeError(
            "subtitle-activity mask is constant; local correlation is undefined"
        )

    text = args.srt.read_text(encoding="utf-8-sig", errors="ignore")
    cues = [
        (to_sec(start), to_sec(end))
        for start, end in re.findall(
            r"(\d\d:\d\d:\d\d,\d+) --> (\d\d:\d\d:\d\d,\d+)",
            text,
        )
    ]
    if not cues:
        raise RuntimeError(f"no SRT cues parsed from {args.srt}")

    search = np.arange(args.search_start, args.search_end, args.search_step)
    best_offset = None
    best_correlation = -np.inf
    correlations = []

    for offset in search:
        release_times = (times_array - offset) / RATE
        reference = np.zeros(len(release_times))
        for cue_start, cue_end in cues:
            reference[
                (release_times >= cue_start) & (release_times <= cue_end)
            ] = 1.0
        if reference.std() < 1e-6:
            continue

        correlation = float(np.corrcoef(reference, present)[0, 1])
        if np.isfinite(correlation):
            correlations.append(
                {
                    "offset_s": float(offset),
                    "correlation": correlation,
                }
            )
            if correlation > best_correlation:
                best_offset = float(offset)
                best_correlation = correlation

    if best_offset is None:
        raise RuntimeError(
            "no valid subtitle correlation found in the configured search range"
        )

    reference_release_times = {
        "Your phone.": 1865.0,
        "JULIE threat insert": 1926.0,
        "Don't get out of this by dying!": 2017.0,
        "Yasu.": 2022.0,
        "What's happening?": 2042.0,
    }
    predictions = {
        label: RATE * release_s + best_offset
        for label, release_s in reference_release_times.items()
    }

    result = {
        "analysis": "local burned-in subtitle activity timebase alignment",
        "video": args.video.name,
        "srt": args.srt.name,
        "recording_window_s": [args.start, args.end],
        "fixed_rate": RATE,
        "search": {
            "offset_start_s": args.search_start,
            "offset_end_s_exclusive": args.search_end,
            "offset_step_s": args.search_step,
        },
        "sampled_frames": len(times_array),
        "nominal_sampling_hz": 10.0,
        "subtitle_present_fraction": float(present.mean()),
        "brightness_threshold_fraction": float(brightness_threshold),
        "best_offset_s": best_offset,
        "best_correlation": best_correlation,
        "mapping": (
            f"t_recording = {RATE} * t_release + {best_offset:.1f}"
        ),
        "predicted_recording_times_s": predictions,
        "correlations": correlations,
        "environment": {
            "python": sys.version.split()[0],
            "opencv": cv2.__version__,
            "numpy": np.__version__,
        },
    }

    print(
        f"Sampled {len(times_array)} frames in "
        f"{args.start:.1f}-{args.end:.1f} s"
    )
    print(f"Subtitle-present fraction: {present.mean():.2f}")
    print(f"Fixed rate: {RATE:.2f} recording seconds per release second")
    print(
        f"Best offset: {best_offset:.1f} s   "
        f"correlation: {best_correlation:.3f}"
    )
    print(f"  {result['mapping']}")
    for label, predicted in predictions.items():
        print(f"  {label}: {predicted:.1f} s")

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(result, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"saved {args.output}")


if __name__ == "__main__":
    main()
