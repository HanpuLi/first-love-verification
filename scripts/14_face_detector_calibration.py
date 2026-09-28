#!/usr/bin/env python3
"""Compare Haar and YuNet on the known Julie close-up calibration window.

The window is 5900-6060 s on the complete FilmFour recording.  PySceneDetect
threshold 27.0 yields 14 shot segments.  The 5943.3 s segment is independently
identified in the essay as Julie's held medium close-up.

The historical audit used three within-shot samples for Haar and five for YuNet.
This script reports that historical-protocol comparison *and* a fair five-sample
comparison for both detectors.  It does not turn face-height ratios into cinematic
shot-scale categories.
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
START, END = 5900.0, 6060.0
HISTORICAL_HAAR_SAMPLES = (0.25, 0.50, 0.75)
FIVE_SAMPLES = (0.15, 0.30, 0.50, 0.70, 0.85)


def verify_model(model: Path) -> None:
    if not model.is_file():
        raise FileNotFoundError(f"missing YuNet model: {model}")
    digest = hashlib.sha256(model.read_bytes()).hexdigest()
    if digest != MODEL_SHA256:
        raise RuntimeError(
            f"unexpected YuNet model SHA-256: {digest}; expected {MODEL_SHA256}"
        )


def scenes(video_path: Path) -> list[tuple[float, float]]:
    if not video_path.is_file():
        raise FileNotFoundError(f"missing analysis input: {video_path}")
    video = open_video(str(video_path))
    manager = SceneManager()
    manager.add_detector(ContentDetector(threshold=27.0))
    video.seek(START)
    manager.detect_scenes(video, end_time=END)
    return [
        (scene_start.seconds, scene_end.seconds)
        for scene_start, scene_end in manager.get_scene_list()
    ]


def run_haar(
    video_path: Path,
    shot_segments: list[tuple[float, float]],
    sample_positions: tuple[float, ...],
) -> list[dict]:
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError(f"OpenCV could not open video: {video_path}")
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    rows = []
    for number, (start, end) in enumerate(shot_segments, 1):
        values = []
        for position in sample_positions:
            cap.set(
                cv2.CAP_PROP_POS_MSEC,
                (start + (end - start) * position) * 1000,
            )
            ok, image = cap.read()
            if not ok:
                continue
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = cascade.detectMultiScale(
                gray,
                scaleFactor=1.08,
                minNeighbors=5,
                minSize=(18, 18),
            )
            if len(faces):
                values.append(
                    max(height for _, _, _, height in faces) / frame_height
                )
        rows.append(
            {
                "segment": number,
                "start_s": start,
                "duration_s": end - start,
                "hits": len(values),
                "samples": len(sample_positions),
                "median_largest_face_height_ratio": (
                    float(np.median(values)) if values else None
                ),
            }
        )
    cap.release()
    return rows


def run_yunet(
    video_path: Path,
    model: Path,
    shot_segments: list[tuple[float, float]],
    sample_positions: tuple[float, ...],
) -> list[dict]:
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError(f"OpenCV could not open video: {video_path}")
    detector = cv2.FaceDetectorYN.create(str(model), "", (0, 0), 0.5, 0.3, 5000)
    rows = []
    for number, (start, end) in enumerate(shot_segments, 1):
        values = []
        for position in sample_positions:
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
        rows.append(
            {
                "segment": number,
                "start_s": start,
                "duration_s": end - start,
                "hits": len(values),
                "samples": len(sample_positions),
                "median_largest_face_height_ratio": (
                    float(np.median(values)) if values else None
                ),
            }
        )
    cap.release()
    return rows


def summary(rows: list[dict]) -> dict:
    seen = [
        row
        for row in rows
        if row["median_largest_face_height_ratio"] is not None
    ]
    values = [row["median_largest_face_height_ratio"] for row in seen]
    target = min(rows, key=lambda row: abs(row["start_s"] - 5943.3))
    return {
        "segments_with_face": len(seen),
        "segments_total": len(rows),
        "median_face_height_ratio_across_seen_segments": (
            float(np.median(values)) if values else None
        ),
        "max_face_height_ratio": max(values) if values else None,
        "known_closeup_segment": target,
    }


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
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    verify_model(args.model)
    shot_segments = scenes(args.video)

    haar_3 = run_haar(args.video, shot_segments, HISTORICAL_HAAR_SAMPLES)
    haar_5 = run_haar(args.video, shot_segments, FIVE_SAMPLES)
    yunet_5 = run_yunet(args.video, args.model, shot_segments, FIVE_SAMPLES)

    result = {
        "analysis": "Haar/YuNet calibration on known Julie close-up",
        "video": args.video.name,
        "window_s": [START, END],
        "scene_detector_threshold": 27.0,
        "segments": len(shot_segments),
        "known_closeup": {
            "description": (
                "Detector-independent calibration target from the essay/frame pass: "
                "held medium close-up of Julie"
            ),
            "expected_start_s": 5943.3,
        },
        "historical_protocol": {
            "haar_sample_positions": list(HISTORICAL_HAAR_SAMPLES),
            "yunet_sample_positions": list(FIVE_SAMPLES),
            "haar": summary(haar_3),
            "yunet": summary(yunet_5),
        },
        "equal_five_sample_protocol": {
            "sample_positions": list(FIVE_SAMPLES),
            "haar": summary(haar_5),
            "yunet": summary(yunet_5),
        },
        "rows": {
            "haar_three_samples": haar_3,
            "haar_five_samples": haar_5,
            "yunet_five_samples": yunet_5,
        },
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

    hist = result["historical_protocol"]
    fair = result["equal_five_sample_protocol"]
    print(
        "historical protocols: "
        f"Haar {hist['haar']['segments_with_face']}/{len(shot_segments)}; "
        f"YuNet {hist['yunet']['segments_with_face']}/{len(shot_segments)}"
    )
    print(
        "equal five-sample protocol: "
        f"Haar {fair['haar']['segments_with_face']}/{len(shot_segments)}; "
        f"YuNet {fair['yunet']['segments_with_face']}/{len(shot_segments)}"
    )
    target = fair["yunet"]["known_closeup_segment"]
    print(
        "known Julie close-up, YuNet: "
        f"{target['hits']}/{target['samples']} hits, "
        f"median face-height ratio="
        f"{target['median_largest_face_height_ratio']:.6f}"
    )
    print(
        "known Julie close-up, Haar: "
        f"{fair['haar']['known_closeup_segment']['hits']}/"
        f"{fair['haar']['known_closeup_segment']['samples']} hits"
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
