"""
PySceneDetect + OpenCV YuNet: shot segmentation and detected-face-height proxy
across the betrayal sequence.

Media inputs are NOT included in this repository (see README).

Window: 2147.4-2301.0 s on the complete off-air FilmFour recording. The window is
mapped from release 00:31:05-00:33:45 using the local relation

    t_recording = 0.96 * t_release + 357.0

The 0.96 rate term is a fixed analysis assumption; 11_subtitle_timebase.py searches
the local offset conditional on that rate. This script does not assign categorical
ECU/CU/MCU/MS/LS labels. It reports a continuous proxy: for five samples in each
detected shot segment, the largest YuNet face height divided by frame height, then
the median of the successful samples.

Model: face_detection_yunet_2023mar.onnx from OpenCV Zoo. The expected Git LFS
object is SHA-256 8f2383e4dd3cfbb4553ea8718107fc0423210dc964f9f4280604804ed2552fa4
(232589 bytes). Fetch the LFS object, not the small pointer file.
"""

from hashlib import sha256
from pathlib import Path

import cv2
import numpy as np
from scenedetect import SceneManager, open_video
from scenedetect.detectors import ContentDetector

VID = Path("first_love_FilmFour_2026-01-12.mp4")
MODEL = Path("face_detection_yunet_2023mar.onnx")
MODEL_SHA256 = "8f2383e4dd3cfbb4553ea8718107fc0423210dc964f9f4280604804ed2552fa4"
START, END = 2147.4, 2301.0

if not VID.is_file():
    raise FileNotFoundError(f"missing analysis input: {VID}")
if not MODEL.is_file():
    raise FileNotFoundError(f"missing YuNet model: {MODEL}")

model_digest = sha256(MODEL.read_bytes()).hexdigest()
if model_digest != MODEL_SHA256:
    raise RuntimeError(
        f"unexpected YuNet model SHA-256: {model_digest}; expected {MODEL_SHA256}. "
        "Fetch the OpenCV Zoo Git LFS object rather than the pointer file."
    )

video = open_video(str(VID))
manager = SceneManager()
manager.add_detector(ContentDetector(threshold=27.0))
video.seek(START)
manager.detect_scenes(video, end_time=END)
scenes = [(start.seconds, end.seconds) for start, end in manager.get_scene_list()]
durations = [end - start for start, end in scenes]

if not durations:
    raise RuntimeError(f"no shot segments detected in {START}-{END} s")

print(f"Shot segments: {len(scenes)}")
print(f"ASL: {sum(durations) / len(durations):.3f} s")
print(f"Longest: {max(durations):.2f} s   Shortest: {min(durations):.2f} s")

cap = cv2.VideoCapture(str(VID))
if not cap.isOpened():
    raise RuntimeError(f"OpenCV could not open video: {VID}")

detector = cv2.FaceDetectorYN.create(str(MODEL), "", (0, 0), 0.5, 0.3, 5000)

face_height_ratios = []
for i, (start, end) in enumerate(scenes, 1):
    values = []
    for position in (0.15, 0.30, 0.50, 0.70, 0.85):
        cap.set(cv2.CAP_PROP_POS_MSEC, (start + (end - start) * position) * 1000)
        ok, image = cap.read()
        if not ok:
            continue
        detector.setInputSize((image.shape[1], image.shape[0]))
        _, faces = detector.detect(image)
        if faces is not None and len(faces):
            values.append(max(float(face[3]) for face in faces) / image.shape[0])

    median_ratio = float(np.median(values)) if values else None
    face_height_ratios.append(median_ratio)
    value_text = "none" if median_ratio is None else f"{median_ratio:.4f}"
    print(
        f"  segment {i:2d}  {start:8.1f}s  {end - start:6.2f}s  "
        f"largest-face-height={value_text:>6}  detections={len(values)}/5"
    )

cap.release()

seen = [value for value in face_height_ratios if value is not None]
print(f"\nSegments with a detected face: {len(seen)}/{len(face_height_ratios)}")
if seen:
    print(f"Median face-height ratio: {np.median(seen):.3f}   Max: {max(seen):.3f}")
else:
    print("No faces were detected in the sampled frames.")
