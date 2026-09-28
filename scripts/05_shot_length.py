"""
PySceneDetect: average shot length across the climax analysis window.

The reported A.9 statistic is defined on the 4300-4742 s window of the 92.9-minute
copy. Detection starts at the window boundary, so the first and last entries may be
partial shot segments clipped by that boundary. This is the same definition used by
outputs/a9_full.py and the archived outputs/a9_shots.json.
Media inputs are NOT included in this repository (see README).
"""

from pathlib import Path

from scenedetect import SceneManager, open_video
from scenedetect.detectors import ContentDetector

VID = Path("first_love.mp4")
START, END = 4300.0, 4742.0

if not VID.is_file():
    raise FileNotFoundError(f"missing analysis input: {VID}")

video = open_video(str(VID))
manager = SceneManager()
manager.add_detector(ContentDetector(threshold=27.0))
video.seek(START)
manager.detect_scenes(video, end_time=END)
scenes = manager.get_scene_list()
durations = [end.seconds - start.seconds for start, end in scenes]

if not durations:
    raise RuntimeError(f"no shot segments detected in {START}-{END} s")

asl = sum(durations) / len(durations)
order = sorted(range(len(durations)), key=lambda i: -durations[i])

print(f"Detected {len(scenes)} shot segments intersecting the analysis window.")
print(f"Covered duration: {sum(durations):.6f} seconds.")
print(f"ASL: {asl:.15f} seconds.")
print(f"Longest segment: {durations[order[0]]:.15f}s (segment {order[0] + 1})")
print(f"Second longest: {durations[order[1]]:.15f}s (segment {order[1] + 1})")
