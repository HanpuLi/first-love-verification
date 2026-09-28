"""
Locate a release-track window on the complete off-air recording using burned-in
subtitle activity.

Media inputs are NOT included in this repository (see README).

This script estimates only a local offset. It fixes the rate term at 0.96
(recording seconds per release second), then searches offsets from 300.0 to 469.9 s
for the best correlation between burned-in subtitle activity and release-SRT cue
activity in the 2100-2400 s recording window.

The resulting mapping is therefore conditional on:
  * the fixed 0.96 rate term;
  * this recording and subtitle file;
  * the ROI/brightness threshold below; and
  * a locally plausible offset search range.

It does not estimate the rate term, establish whole-film linearity, bridge retained
ad breaks, or by itself provide an "exact" global time conversion.
"""

import re
from pathlib import Path

import cv2
import numpy as np

VID = Path("first_love_FilmFour_2026-01-12.mp4")
SRT = Path("first_love_en.srt")
START, END = 2100.0, 2400.0
RATE = 0.96
SEARCH = np.arange(300.0, 470.0, 0.1)

if not VID.is_file():
    raise FileNotFoundError(f"missing analysis input: {VID}")
if not SRT.is_file():
    raise FileNotFoundError(f"missing subtitle input: {SRT}")

cap = cv2.VideoCapture(str(VID))
if not cap.isOpened():
    raise RuntimeError(f"OpenCV could not open video: {VID}")

fps = cap.get(cv2.CAP_PROP_FPS)
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
if fps <= 0 or height <= 0 or width <= 0:
    cap.release()
    raise RuntimeError(
        f"invalid video metadata: fps={fps}, width={width}, height={height}"
    )

cap.set(cv2.CAP_PROP_POS_MSEC, START * 1000)
step = max(1, int(round(fps / 10)))  # approximately 10 Hz
times, bright = [], []
frame_index = 0

while True:
    ok, image = cap.read()
    if not ok:
        break
    t = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
    if t > END:
        break
    if frame_index % step == 0:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        roi = gray[
            int(height * 0.78):int(height * 0.99),
            int(width * 0.10):int(width * 0.90),
        ]
        times.append(t)
        bright.append((roi > 205).mean())
    frame_index += 1

cap.release()

if not bright:
    raise RuntimeError(f"no decodable frames sampled in {START}-{END} s")

times = np.asarray(times)
bright = np.asarray(bright)
present = (bright > max(0.006, np.percentile(bright, 55))).astype(float)
if present.std() < 1e-6:
    raise RuntimeError("subtitle-activity mask is constant; local correlation is undefined")

text = SRT.read_text(encoding="utf-8-sig", errors="ignore")


def to_sec(value):
    hours, minutes, rest = value.split(":")
    seconds, millis = rest.split(",")
    return (
        int(hours) * 3600
        + int(minutes) * 60
        + int(seconds)
        + int(millis) / 1000
    )


cues = [
    (to_sec(start), to_sec(end))
    for start, end in re.findall(
        r"(\d\d:\d\d:\d\d,\d+) --> (\d\d:\d\d:\d\d,\d+)", text
    )
]
if not cues:
    raise RuntimeError(f"no SRT cues parsed from {SRT}")

best_offset = None
best_correlation = -np.inf

for offset in SEARCH:
    release_times = (times - offset) / RATE
    reference = np.zeros(len(release_times))
    for cue_start, cue_end in cues:
        reference[
            (release_times >= cue_start) & (release_times <= cue_end)
        ] = 1.0
    if reference.std() < 1e-6:
        continue

    correlation = float(np.corrcoef(reference, present)[0, 1])
    if np.isfinite(correlation) and correlation > best_correlation:
        best_offset = float(offset)
        best_correlation = correlation

if best_offset is None:
    raise RuntimeError("no valid subtitle correlation found in the configured search range")

print(f"Subtitle-present samples: {present.mean():.2f} of window")
print(f"Fixed rate: {RATE:.2f} recording seconds per release second")
print(f"Best offset: {best_offset:.1f} s   correlation: {best_correlation:.3f}")
print(f"  t_recording = {RATE} * t_release + {best_offset:.1f}")
