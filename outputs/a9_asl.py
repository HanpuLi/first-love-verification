from scenedetect import open_video, SceneManager
from scenedetect.detectors import ContentDetector
from fractions import Fraction
VID="/sessions/happy-gallant-knuth/mnt/学习/PhD_Applications_2026/02_Writing_Samples_README/FirstLove/first_love.mp4"

def detect(start_s, end_s, label):
    video=open_video(VID)
    fps=video.frame_rate
    sm=SceneManager()
    sm.add_detector(ContentDetector(threshold=27.0))
    video.seek(start_s)
    sm.detect_scenes(video, end_time=end_s)
    scenes=sm.get_scene_list()
    print(f"\n===== {label}: window {start_s}-{end_s}s  fps={fps}  detected {len(scenes)} shots =====")
    durs=[]
    for k,(s,e) in enumerate(scenes,1):
        d=e.get_seconds()-s.get_seconds(); durs.append(d)
    if durs:
        tot=sum(durs); asl=tot/len(durs)
        print(f"  total covered={tot:.5f}s  ASL={asl:.6f}s  ASL_frac~={asl*24:.3f}/24")
        # longest / specific shots
        order=sorted(range(len(durs)), key=lambda i:-durs[i])
        print(f"  longest shot #{order[0]+1}={durs[order[0]]:.5f}s ; 2nd #{order[1]+1}={durs[order[1]]:.5f}s")
        for idx in [10,11,12,13,14,15,16,17,29,54]:
            if idx<=len(durs): print(f"    Shot {idx}: {durs[idx-1]:.6f}s ({durs[idx-1]*24:.2f} frames)")
    return durs

# Melee window per essay
detect(4300.0,4742.0,"MELEE (essay: 62 shots, ASL 7.129s)")
# Animation window per essay (cut-in 4742 to cut-out ~4768.04)
detect(4742.0,4768.04,"ANIMATION (essay: 10 shots, ASL 2.604s)")
