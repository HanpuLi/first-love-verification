import cv2, os
KF="/sessions/happy-gallant-knuth/mnt/学习/PhD_Applications_2026/02_Writing_Samples_README/FirstLove/keyframes"
src=os.path.join(KF,"climax_03_sustained_faceCU_t4509s.png")  # the 4506-4513s sustained Monica CU named in essay
img=cv2.imread(src)
print("src shape",None if img is None else img.shape)
casc=cv2.CascadeClassifier(cv2.data.haarcascades+"haarcascade_frontalface_default.xml")
g=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
# brighten (low-key scene)
g2=cv2.convertScaleAbs(g,alpha=1.8,beta=30)
faces=casc.detectMultiScale(g2,1.1,4,minSize=(60,60))
print("faces detected:",faces)
if len(faces):
    x,y,w,h=sorted(faces,key=lambda f:-f[2]*f[3])[0]
    pad=int(0.25*h)
    y0=max(0,y-pad);x0=max(0,x-pad)
    crop=img[y0:y+h+pad, x0:x+w+pad]
    cv2.imwrite("monica_ref_0.png",crop)
    print("WROTE monica_ref_0.png size",crop.shape,"from face bbox",(x,y,w,h))
else:
    # fallback: center crop
    H,W=img.shape[:2]; crop=img[int(H*0.1):int(H*0.85),int(W*0.3):int(W*0.7)]
    cv2.imwrite("monica_ref_0.png",crop); print("fallback center crop",crop.shape)
