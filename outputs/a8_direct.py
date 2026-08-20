import librosa, numpy as np
VID="/sessions/happy-gallant-knuth/mnt/学习/PhD_Applications_2026/02_Writing_Samples_README/FirstLove/first_love.mp4"
CUT_IN=4742.0; CUT_OUT=4768.0; HOP=512
tgt=[0.129644557833672,0.198803529143333,0.288493871688843,0.286753028631210]

for srt,lab in [(None,"mp4 sr=None"),(22050,"mp4 sr=22050")]:
    # load directly from mp4, offset+duration
    y,sr=librosa.load(VID, sr=srt, offset=4730.0, duration=50.0, mono=True)
    print(f"\n##### {lab}: sr={sr} n={len(y)}")
    tempo,beats=librosa.beat.beat_track(y=y,sr=sr,hop_length=HOP)
    bt=librosa.frames_to_time(beats,sr=sr,hop_length=HOP)+4730.0
    i=int(np.argmin(np.abs(bt-CUT_IN)))
    print(f"  nearest beat {bt[i]:.10f} off {bt[i]-CUT_IN:+.10f}")
    rms=librosa.feature.rms(y=y)[0]
    rt=librosa.times_like(rms,sr=sr,hop_length=HOP)+4730.0
    for tv in tgt:
        d=np.abs(rms-tv);j=int(np.argmin(d))
        print(f"  ~{tv}: idx{j} t={rt[j]:.4f} val={rms[j]:.18f} |d|={d[j]:.2e}")

# Hypothesis: RMS averaged in window before/after cut. Test with 48k wav.
print("\n##### window-mean hypotheses (48k wav)")
y,sr=librosa.load("seg_48k_mono.wav",sr=48000)
rms=librosa.feature.rms(y=y)[0]
rt=librosa.times_like(rms,sr=sr,hop_length=HOP)+4730.0
def win(a,b):
    m=(rt>=a)&(rt<b); return rms[m].mean()
# try various windows around cut-in 4742
for (a1,b1,a2,b2) in [(4741,4742,4742,4743),(4740,4742,4742,4744),(4741.5,4742,4742,4742.5)]:
    bef=win(a1,b1); aft=win(a2,b2)
    print(f"  pre[{a1},{b1})={bef:.15f} post[{a2},{b2})={aft:.15f} surge={(aft/bef-1)*100:.6f}%")
