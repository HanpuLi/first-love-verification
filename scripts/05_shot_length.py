"""
PySceneDetect: average shot length across the climax window

Supports the analysis reported in the essay appendix.
Media inputs are NOT included in this repository (see README).
"""

from scenedetect import detect, ContentDetector
scene_list = detect("first_love.mp4", ContentDetector(threshold=27.0))
climax_scenes = [s for s in scene_list if s[0].get_seconds() >= 4300.0 and s[1].get_seconds() <= 4742.0]
durations = [s[1].get_seconds() - s[0].get_seconds() for s in climax_scenes]
asl = sum(durations) / len(durations)
order = sorted(range(len(durations)), key=lambda i: -durations[i])
print(f"Detected {len(climax_scenes)} shots.")
print(f"ASL: {asl:.15f} seconds.")
print(f"Longest shot: {durations[order[0]]:.15f}s (Shot {order[0]+1})")
print(f"Second longest: {durations[order[1]]:.15f}s (Shot {order[1]+1})")
