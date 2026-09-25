"""
PySceneDetect + OpenCV YuNet: shot count, ASL and shot-scale across the betrayal sequence

Supports the shot-level footnote in the body and the timebase note in the appendix.
Media inputs are NOT included in this repository (see README).

Window: 2147.4-2301.0 s on the complete off-air FilmFour recording, which is the
betrayal sequence (release track 00:31:05-00:33:45) mapped through
    t_recording = 0.96 * t_release + 357.0
See 11_subtitle_timebase.py for how that mapping is established.

The face detector is YuNet, NOT the Haar cascade used in 06_face_scale_audit.py.
Haar fails to register the confirmed medium close-up of Julie at 5943.3 s on this
copy (720x576, low-key lighting); YuNet returns it on 5 of 5 sampled frames at
0.458 of frame height. A null result from Haar on this material establishes nothing.

Model: face_detection_yunet_2023mar.onnx from the OpenCV Zoo. It is stored with
Git LFS, so fetch it from the media endpoint --- raw.githubusercontent.com returns
a 131-byte pointer file, not the model.
"""

import cv2
import numpy as np
from scenedetect import open_video, SceneManager
from scenedetect.detectors import ContentDetector

VID = "first_love_FilmFour_2026-01-12.mp4"
MODEL = "face_detection_yunet_2023mar.onnx"
START, END = 2147.4, 2301.0

video = open_video(VID)
sm = SceneManager()
sm.add_detector(ContentDetector(threshold=27.0))
video.seek(START)
sm.detect_scenes(video, end_time=END)
scenes = [(s.seconds, e.seconds) for s, e in sm.get_scene_list()]
durations = [e - s for s, e in scenes]
print(f"Shots: {len(scenes)}")
print(f"ASL: {sum(durations) / len(durations):.3f} s")
print(f"Longest: {max(durations):.2f} s   Shortest: {min(durations):.2f} s")

cap = cv2.VideoCapture(VID)
H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
det = cv2.FaceDetectorYN.create(MODEL, "", (0, 0), 0.5, 0.3, 5000)

# Bands calibrated against the essay's own reading: the medium close-up of Julie
# at 5943.3 s measures 0.458 of frame height.
def band(x):
    if x is None:
        return "no face"
    return ("ECU" if x >= 0.70 else "CU" if x >= 0.45 else
            "MCU" if x >= 0.28 else "MS" if x >= 0.15 else "LS")

scales = []
for i, (s, e) in enumerate(scenes, 1):
    vals = []
    for p in (0.15, 0.30, 0.50, 0.70, 0.85):
        cap.set(cv2.CAP_PROP_POS_MSEC, (s + (e - s) * p) * 1000)
        ok, img = cap.read()
        if not ok:
            continue
        det.setInputSize((img.shape[1], img.shape[0]))
        _, faces = det.detect(img)
        if faces is not None and len(faces):
            vals.append(max(float(f[3]) for f in faces) / H)
    med = float(np.median(vals)) if vals else None
    scales.append(med)
    print(f"  shot {i:2d}  {s:8.1f}s  {e - s:6.2f}s  "
          f"{med if med is None else round(med, 4)!s:>7}  {len(vals)}/5  {band(med)}")
cap.release()

seen = [x for x in scales if x is not None]
print(f"\nShots with a detected face: {len(seen)}/{len(scales)}")
print(f"Median face height: {np.median(seen):.3f}   Max: {max(seen):.3f}")
print(f"ECU (>=0.70): {sum(1 for x in seen if x >= 0.70)}")
print(f"CU  (>=0.45): {sum(1 for x in seen if x >= 0.45)}")
