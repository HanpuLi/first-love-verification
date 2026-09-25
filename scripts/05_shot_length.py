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

# NOTE (2026-08-27, audit): the figures the essay actually reports for this window are
# 62 shots, ASL 7.129 s (melee) and 10 shots, ASL 2.604 s (animation). Both were
# reproduced independently on 2026-08-27 and match. Earlier labels in this repository
# quoted 60 / 7.320139 and 12 / 2.190972 from a superseded run; they have been corrected.
#
# Two limits on this window that the essay's appendix should be read alongside:
#   (1) The window is given in seconds on the 92.9-minute copy. That is a copy-dependent
#       coordinate. Mapped to the release track it spans c. 4859-5542 s, i.e. about 683 s
#       of material, of which the 92.9-minute copy carries only 442 s: roughly 241 s is
#       missing from this window on that copy. Re-measured on the complete broadcast
#       recording the ASL comes out at 7.12 s, i.e. the reported value holds.
#   (2) Threshold 27.0 slightly under-detects even on this copy. Checked against cuts
#       from the complete recording at a calibrated threshold, 27.0 matches 36 of 39
#       (92.3%) while 22.0 matches 39 of 39. The essay already describes its count as
#       the conservative one, which is consistent with this.
