"""
Locating the release track on the off-air recording via burned-in subtitle activity

Supports the timebase note in the appendix.
Media inputs are NOT included in this repository (see README).

The recording carries burned-in English subtitles. Their appearance and disappearance
are precise time events and share a source with the release subtitle file, so
correlating the two recovers the mapping far more accurately than audio does.

Measured accuracy over the betrayal sequence: correlation 0.673, and the resulting
model places `What's happening?' (release 00:34:02) at 2317.3 s against 2318.5 s
observed on a frame check --- 1.2 s.

For comparison, on the same material: correlating the subtitle file against an audio
RMS envelope scores 0.09-0.36 searching the whole film and 0.21-0.375 searching
locally, and single-point anchoring (reading one subtitle off one sampled frame) was
found to be off by 28.8 s without any internal sign that it was wrong.

NOTE: the offset only holds until the next retained ad break, and the search range
must be set from the expected offset at that point in the film. Searching a late
sequence with an early sequence's range returns a plausible-looking false peak
(0.495 in the case tested). Check that subtitles are actually present in the window
first: an action sequence with sparse dialogue gives nothing to correlate.
"""

import re
import cv2
import numpy as np

VID = "first_love_FilmFour_2026-01-12.mp4"
SRT = "first_love_en.srt"
START, END = 2100.0, 2400.0
PAL = 0.96                      # release -> recording, the 4.1667% PAL speed-up
SEARCH = np.arange(300.0, 470.0, 0.1)

cap = cv2.VideoCapture(VID)
fps = cap.get(cv2.CAP_PROP_FPS)
H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
cap.set(cv2.CAP_PROP_POS_MSEC, START * 1000)
step = max(1, int(round(fps / 10)))       # sample at 10 Hz
times, bright = [], []
n = 0
while True:
    ok, img = cap.read()
    if not ok:
        break
    t = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
    if t > END:
        break
    if n % step == 0:
        g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        roi = g[int(H * 0.78):int(H * 0.99), int(W * 0.10):int(W * 0.90)]
        times.append(t)
        bright.append((roi > 205).mean())
    n += 1
cap.release()
times, bright = np.array(times), np.array(bright)
present = (bright > max(0.006, np.percentile(bright, 55))).astype(float)

text = open(SRT, encoding="utf-8-sig", errors="ignore").read()
def to_sec(s):
    h, m, rest = s.split(":")
    sec, ms = rest.split(",")
    return int(h) * 3600 + int(m) * 60 + int(sec) + int(ms) / 1000
cues = [(to_sec(a), to_sec(b)) for a, b in
        re.findall(r"(\d\d:\d\d:\d\d,\d+) --> (\d\d:\d\d:\d\d,\d+)", text)]

best = (None, -9.0)
for off in SEARCH:
    t_rel = (times - off) / PAL
    ref = np.zeros(len(t_rel))
    for a, b in cues:
        ref[(t_rel >= a) & (t_rel <= b)] = 1.0
    if ref.std() < 1e-6:
        continue
    c = float(np.corrcoef(ref, present)[0, 1])
    if c > best[1]:
        best = (off, c)

print(f"Subtitle-present samples: {present.mean():.2f} of window")
print(f"Best offset: {best[0]:.1f} s   correlation: {best[1]:.3f}")
print(f"  t_recording = {PAL} * t_release + {best[0]:.1f}")
