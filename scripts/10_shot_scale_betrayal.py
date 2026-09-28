#!/usr/bin/env python3
"""PySceneDetect + OpenCV YuNet audit of the betrayal sequence.

Window: 2147.4-2301.0 s on the complete off-air FilmFour recording.  The
window comes from the local subtitle-activity mapping in script 11:

    t_recording = 0.96 * t_release + 357.0

The default scene threshold is 18.0, selected by the cross-copy calibration
in script 13 for the lower-resolution FilmFour recording.  The face measure is
continuous: at five positions within each detected shot segment, record the
largest YuNet face height divided by frame height, then take the median of
successful samples.  No ECU/CU/MCU/MS/LS category thresholds are imposed here.

Media and the YuNet model are external inputs (see README).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import cv2
import numpy as np
import scenedetect
from scenedetect import SceneManager, open_video
from scenedetect.detectors import ContentDetector

MODEL_SHA256 = "8f2383e4dd3cfbb4553ea8718107fc0423210dc964f9f4280604804ed2552fa4"
START, END = 2147.4, 2301.0
SAMPLE_POSITIONS = (0.15, 0.30, 0.50, 0.70, 0.85)


def verify_model(model: Path) -> None:
    if not model.is_file():
        raise FileNotFoundError(f"missing YuNet model: {model}")
    digest = hashlib.sha256(model.read_bytes()).hexdigest()
    if digest != MODEL_SHA256:
        raise RuntimeError(
            f"unexpected YuNet model SHA-256: {digest}; expected {MODEL_SHA256}. "
            "Fetch the OpenCV Zoo Git LFS object rather than a pointer file."
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--video",
        type=Path,
        default=Path("first_love_FilmFour_2026-01-12.mp4"),
    )
    parser.add_argument(
        "--model",
        type=Path,
        default=Path("face_detection_yunet_2023mar.onnx"),
    )
    parser.add_argument("--threshold", type=float, default=18.0)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    if not args.video.is_file():
        raise FileNotFoundError(f"missing analysis input: {args.video}")
    verify_model(args.model)

    video = open_video(str(args.video))
    manager = SceneManager()
    manager.add_detector(ContentDetector(threshold=args.threshold))
    video.seek(START)
    manager.detect_scenes(video, end_time=END)
    scenes = [
        (scene_start.seconds, scene_end.seconds)
        for scene_start, scene_end in manager.get_scene_list()
    ]
    durations = [end - start for start, end in scenes]
    if not durations:
        raise RuntimeError(f"no shot segments detected in {START}-{END} s")

    cap = cv2.VideoCapture(str(args.video))
    if not cap.isOpened():
        raise RuntimeError(f"OpenCV could not open video: {args.video}")
    detector = cv2.FaceDetectorYN.create(
        str(args.model), "", (0, 0), 0.5, 0.3, 5000
    )

    rows = []
    for number, (start, end) in enumerate(scenes, 1):
        values = []
        for position in SAMPLE_POSITIONS:
            cap.set(
                cv2.CAP_PROP_POS_MSEC,
                (start + (end - start) * position) * 1000,
            )
            ok, image = cap.read()
            if not ok:
                continue
            detector.setInputSize((image.shape[1], image.shape[0]))
            _, faces = detector.detect(image)
            if faces is not None and len(faces):
                values.append(
                    max(float(face[3]) for face in faces) / image.shape[0]
                )
        median_ratio = float(np.median(values)) if values else None
        rows.append(
            {
                "segment": number,
                "start_s": start,
                "duration_s": end - start,
                "hits": len(values),
                "samples": len(SAMPLE_POSITIONS),
                "median_largest_face_height_ratio": median_ratio,
            }
        )
    cap.release()

    seen = [
        row
        for row in rows
        if row["median_largest_face_height_ratio"] is not None
    ]
    ratios = [row["median_largest_face_height_ratio"] for row in seen]
    result = {
        "analysis": "betrayal shot segmentation + YuNet face-height proxy",
        "video": args.video.name,
        "window_s": [START, END],
        "scene_detector_threshold": args.threshold,
        "sample_positions": list(SAMPLE_POSITIONS),
        "shot_segments": len(scenes),
        "covered_duration_s": sum(durations),
        "asl_s": sum(durations) / len(durations),
        "longest_segment_s": max(durations),
        "shortest_segment_s": min(durations),
        "segments_with_detected_face": len(seen),
        "median_face_height_ratio_across_seen_segments": (
            float(np.median(ratios)) if ratios else None
        ),
        "max_face_height_ratio": max(ratios) if ratios else None,
        "rows": rows,
        "model": {
            "name": args.model.name,
            "sha256": MODEL_SHA256,
        },
        "environment": {
            "python": sys.version.split()[0],
            "opencv": cv2.__version__,
            "numpy": np.__version__,
            "scenedetect": scenedetect.__version__,
        },
    }

    print(f"Shot segments: {len(scenes)}")
    print(f"ASL: {result['asl_s']:.3f} s")
    print(
        f"Longest: {result['longest_segment_s']:.2f} s   "
        f"Shortest: {result['shortest_segment_s']:.2f} s"
    )
    for row in rows:
        value = row["median_largest_face_height_ratio"]
        value_text = "none" if value is None else f"{value:.4f}"
        print(
            f"  segment {row['segment']:2d}  {row['start_s']:8.1f}s  "
            f"{row['duration_s']:6.2f}s  "
            f"largest-face-height={value_text:>6}  "
            f"detections={row['hits']}/{row['samples']}"
        )
    print(
        f"Segments with a detected face: "
        f"{len(seen)}/{len(rows)}"
    )
    if ratios:
        print(
            f"Median face-height ratio: {np.median(ratios):.3f}   "
            f"Max: {max(ratios):.3f}"
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
