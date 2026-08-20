from scenedetect import open_video, SceneManager
from scenedetect.detectors import ContentDetector
import json
VID="/sessions/happy-gallant-knuth/mnt/学习/PhD_Applications_2026/02_Writing_Samples_README/FirstLove/first_love.mp4"

def detect(start_s,end_s,thr=27.0,dsf=None):
    v=open_video(VID); sm=SceneManager()
    sm.add_detector(ContentDetector(threshold=thr))
    if dsf is not None: sm.downscale=dsf
    v.seek(start_s); sm.detect_scenes(v,end_time=end_s)
    return [round(e.get_seconds()-s.get_seconds(),6) for s,e in sm.get_scene_list()]

res={}
# main per-essay windows
m=detect(4300.0,4742.0); a=detect(4742.0,4768.0417)
res['melee_main']={'n':len(m),'asl':sum(m)/len(m),'durs':m}
res['anim_main']={'n':len(a),'asl':sum(a)/len(a),'durs':a}
print(f"MELEE 4300-4742: n={len(m)} ASL={sum(m)/len(m):.6f}")
print(f"ANIM 4742-4768.04: n={len(a)} ASL={sum(a)/len(a):.6f}")
# sensitivity: alt boundaries + downscale=1
for (s0,e0,lab) in [(4300.0,4741.75,'melee_altb'),(4741.75,4768.0417,'anim_altb')]:
    d=detect(s0,e0); print(f"  {lab} {s0}-{e0}: n={len(d)} ASL={sum(d)/len(d):.4f}")
md1=detect(4300.0,4742.0,dsf=1); print(f"  melee downscale=1: n={len(md1)} ASL={sum(md1)/len(md1):.4f}")
ad1=detect(4742.0,4768.0417,dsf=1); print(f"  anim downscale=1: n={len(ad1)} ASL={sum(ad1)/len(ad1):.4f}")
json.dump(res,open("a9_shots.json","w"),indent=1)
print("saved a9_shots.json")
