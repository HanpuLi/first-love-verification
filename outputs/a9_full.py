import json
from pathlib import Path

from scenedetect import SceneManager, open_video
from scenedetect.detectors import ContentDetector

VID = "first_love.mp4"
OUTPUT = Path(__file__).with_name("a9_shots.json")


def detect(start_s, end_s, threshold=27.0, downscale=None):
    video = open_video(VID)
    manager = SceneManager()
    manager.add_detector(ContentDetector(threshold=threshold))
    if downscale is not None:
        manager.downscale = downscale
    video.seek(start_s)
    manager.detect_scenes(video, end_time=end_s)
    return [
        round(end.get_seconds() - start.get_seconds(), 6)
        for start, end in manager.get_scene_list()
    ]


result = {}

# Main per-essay windows. Windowed detection intentionally includes boundary-clipped
# shot segments so the statistic covers the complete analysis interval.
melee = detect(4300.0, 4742.0)
animation = detect(4742.0, 4768.0417)
result["melee_main"] = {
    "n": len(melee),
    "asl": sum(melee) / len(melee),
    "durs": melee,
}
result["anim_main"] = {
    "n": len(animation),
    "asl": sum(animation) / len(animation),
    "durs": animation,
}
print(f"MELEE 4300-4742: n={len(melee)} ASL={sum(melee) / len(melee):.6f}")
print(
    f"ANIM 4742-4768.04: n={len(animation)} "
    f"ASL={sum(animation) / len(animation):.6f}"
)

# Sensitivity: alternate boundaries + downscale=1.
for start, end, label in [
    (4300.0, 4741.75, "melee_altb"),
    (4741.75, 4768.0417, "anim_altb"),
]:
    durations = detect(start, end)
    print(
        f"  {label} {start}-{end}: n={len(durations)} "
        f"ASL={sum(durations) / len(durations):.4f}"
    )

melee_d1 = detect(4300.0, 4742.0, downscale=1)
print(f"  melee downscale=1: n={len(melee_d1)} ASL={sum(melee_d1) / len(melee_d1):.4f}")
anim_d1 = detect(4742.0, 4768.0417, downscale=1)
print(f"  anim downscale=1: n={len(anim_d1)} ASL={sum(anim_d1) / len(anim_d1):.4f}")

OUTPUT.write_text(json.dumps(result, indent=1) + "\n")
print(f"saved {OUTPUT}")
