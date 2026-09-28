from scenedetect import SceneManager, open_video
from scenedetect.detectors import ContentDetector

VID = "first_love.mp4"


def detect(start_s, end_s, label):
    video = open_video(VID)
    fps = video.frame_rate
    manager = SceneManager()
    manager.add_detector(ContentDetector(threshold=27.0))
    video.seek(start_s)
    manager.detect_scenes(video, end_time=end_s)
    scenes = manager.get_scene_list()
    print(
        f"\n===== {label}: window {start_s}-{end_s}s  fps={fps}  "
        f"detected {len(scenes)} shot segments ====="
    )
    durations = []
    for start, end in scenes:
        duration = end.get_seconds() - start.get_seconds()
        durations.append(duration)
    if durations:
        total = sum(durations)
        asl = total / len(durations)
        print(
            f"  total covered={total:.5f}s  ASL={asl:.6f}s  "
            f"ASL_frac~={asl * 24:.3f}/24"
        )
        order = sorted(range(len(durations)), key=lambda i: -durations[i])
        print(
            f"  longest segment #{order[0] + 1}={durations[order[0]]:.5f}s ; "
            f"2nd #{order[1] + 1}={durations[order[1]]:.5f}s"
        )
        for idx in [10, 11, 12, 13, 14, 15, 16, 17, 29, 54]:
            if idx <= len(durations):
                print(
                    f"    Segment {idx}: {durations[idx - 1]:.6f}s "
                    f"({durations[idx - 1] * 24:.2f} frames)"
                )
    return durations


# Windowed detection includes boundary-clipped shot segments by definition.
detect(4300.0, 4742.0, "MELEE (essay: 62 segments, ASL 7.129s)")
detect(4742.0, 4768.04, "ANIMATION (essay: 10 segments, ASL 2.604s)")
