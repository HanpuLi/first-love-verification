import cv2, numpy as np
VID="/sessions/happy-gallant-knuth/mnt/学习/PhD_Applications_2026/02_Writing_Samples_README/FirstLove/first_love.mp4"
casc=cv2.CascadeClassifier(cv2.data.haarcascades+"haarcascade_frontalface_default.xml")
cap=cv2.VideoCapture(VID); fps=cap.get(cv2.CAP_PROP_FPS)
hits=0; tot=0; cu=0
for t in np.arange(4300,4768,4.0):  # sample every 4s across climax+anim
    cap.set(cv2.CAP_PROP_POS_MSEC,t*1000); ok,fr=cap.read()
    if not ok: continue
    tot+=1; H,W=fr.shape[:2]
    g=cv2.convertScaleAbs(cv2.cvtColor(fr,cv2.COLOR_BGR2GRAY),alpha=2.0,beta=40)
    f=casc.detectMultiScale(g,1.1,4,minSize=(50,50))
    if len(f):
        hits+=1
        a=max(w*h for x,y,w,h in f)/(W*H)
        if a>0.10: cu+=1
cap.release()
print(f"sampled frames={tot}  frames_with_any_frontal_face={hits} ({100*hits/tot:.1f}%)  of which CU(face>10% area)={cu}")
print("NOTE: Haar frontal-face detection on this low-key night footage; not Monica-specific (no recognition model). Informational only.")
