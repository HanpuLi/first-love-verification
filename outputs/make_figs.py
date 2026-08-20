import librosa, numpy as np, json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OFF=4730.0; CUT_IN=4742.0; CUT_OUT=4768.0; HOP=512
# ---- audio (reproduced, native 48k) ----
y,sr=librosa.load("seg_48k_mono.wav",sr=48000)
rms=librosa.feature.rms(y=y)[0]; rt=librosa.times_like(rms,sr=sr,hop_length=HOP)+OFF
oenv=librosa.onset.onset_strength(y=y,sr=sr,hop_length=HOP); ot=librosa.times_like(oenv,sr=sr,hop_length=HOP)+OFF
tempo,beats=librosa.beat.beat_track(y=y,sr=sr,hop_length=HOP)
bt=librosa.frames_to_time(beats,sr=sr,hop_length=HOP)+OFF
i=int(np.argmin(np.abs(bt-CUT_IN))); nb=bt[i]

fig,(ax1,ax2)=plt.subplots(2,1,figsize=(10,6),sharex=True)
ax1.plot(rt,rms,color="#1f77b4",lw=1.1,label="RMS volume envelope")
ax1.axvline(CUT_IN,color="#d62728",ls="--",lw=1.2,label=f"visual cut-in {CUT_IN}s")
ax1.axvline(CUT_OUT,color="#2ca02c",ls="--",lw=1.2,label=f"visual cut-out {CUT_OUT}s")
ax1.set_ylabel("RMS amplitude"); ax1.set_xlim(4735,4775)
ax1.legend(fontsize=8,loc="upper right")
ax1.set_title("Soundtrack RMS envelope & onset-beat alignment around the animated climax (sandbox-reproduced, librosa 0.11, native 48 kHz)",fontsize=9)
ax2.plot(ot,oenv,color="#7f7f7f",lw=0.9,label="onset strength")
ax2.vlines(bt,0,oenv.max(),color="#9467bd",alpha=0.5,lw=0.8,label="detected beats")
ax2.axvline(nb,color="#d62728",lw=1.4,label=f"nearest beat {nb:.4f}s (offset {nb-CUT_IN:+.4f}s)")
ax2.axvline(CUT_IN,color="#d62728",ls="--",lw=1.0)
ax2.set_xlabel("time (s)"); ax2.set_ylabel("onset strength")
ax2.legend(fontsize=8,loc="upper right")
plt.tight_layout(); plt.savefig("fig_audio_alignment.png",dpi=150); plt.close()
print("wrote fig_audio_alignment.png; nearest beat",round(nb,7),"offset",round(nb-CUT_IN,7))

# ---- ASL (reproduced shots) ----
d=json.load(open("a9_shots.json"))
m=d["melee_main"]["durs"]; a=d["anim_main"]["durs"]
asl_m=sum(m)/len(m); asl_a=sum(a)/len(a)
fig,(axA,axB)=plt.subplots(1,2,figsize=(11,5),gridspec_kw={"width_ratios":[3,1]})
axA.bar(range(1,len(m)+1),m,color="#4c72b0")
axA.axhline(asl_m,color="#c44e52",ls="--",lw=1.4,label=f"reproduced ASL = {asl_m:.3f}s ({len(m)} shots)")
axA.axhline(7.320139,color="#dd8452",ls=":",lw=1.4,label="essay ASL = 7.320s (60 shots)")
axA.set_title("Live-action hardware-store melee (4300–4742 s)",fontsize=9)
axA.set_xlabel("shot #"); axA.set_ylabel("shot duration (s)"); axA.legend(fontsize=8)
axB.bar(range(1,len(a)+1),a,color="#55a868")
axB.axhline(asl_a,color="#c44e52",ls="--",lw=1.4,label=f"reproduced ASL={asl_a:.3f}s ({len(a)})")
axB.axhline(2.190972,color="#dd8452",ls=":",lw=1.4,label="essay ASL=2.191s (12)")
axB.set_title("Animated climax (4742–4768 s)",fontsize=9)
axB.set_xlabel("shot #"); axB.legend(fontsize=7)
fig.suptitle("Shot durations & ASL — sandbox-reproduced (PySceneDetect 0.7, ContentDetector thr=27.0); dotted = essay's in-text values",fontsize=9)
plt.tight_layout(); plt.savefig("fig_asl_comparison.png",dpi=150); plt.close()
print(f"wrote fig_asl_comparison.png; melee {len(m)} ASL {asl_m:.4f}; anim {len(a)} ASL {asl_a:.4f}")
