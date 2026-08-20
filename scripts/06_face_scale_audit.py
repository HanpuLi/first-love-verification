"""
OpenCV: character presence and shot-scale proxy (candidate counts only)

Supports the analysis reported in the essay appendix.
Media inputs are NOT included in this repository (see README).
"""

import cv2
import numpy as np
def compare_faces(face1, face2_ref):
    f1 = cv2.resize(face1, (64, 64))
    f2 = cv2.resize(face2_ref, (64, 64))
    g1 = cv2.cvtColor(f1, cv2.COLOR_BGR2GRAY)
    g2 = cv2.cvtColor(f2, cv2.COLOR_BGR2GRAY)
    return cv2.matchTemplate(g1, g2, cv2.TM_CCOEFF_NORMED)[0][0]
cap = cv2.VideoCapture("first_love.mp4")
fps = cap.get(cv2.CAP_PROP_FPS)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
ref_face = cv2.imread("monica_ref_0.png")
monica_frames = 0
monica_cu = 0
total_sampled = 0
for f in range(int(4300 * fps), int(4742 * fps), int(fps)):
    cap.set(cv2.CAP_PROP_POS_FRAMES, f)
    ret, frame = cap.read()
    if not ret: break
    total_sampled += 1
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4)
    for (x, y, w, h) in faces:
        crop = frame[y:y+h, x:x+w]
        if compare_faces(crop, ref_face) > 0.38:
            monica_frames += 1
            if h >= 65: monica_cu += 1
            break
print(f"Presence: {monica_frames/total_sampled*100:.15f}%")
print(f"CU proportion: {monica_cu/monica_frames*100:.15f}%")
cap.release()
