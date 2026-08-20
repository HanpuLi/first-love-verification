import librosa, numpy as np
CUT_IN=4742.0; CUT_OUT=4768.0; HOP=512
y,sr=librosa.load("seg_48k_mono.wav",sr=48000); OFF=4730.0
tempo,beats=librosa.beat.beat_track(y=y,sr=sr,hop_length=HOP)
bt=librosa.frames_to_time(beats,sr=sr,hop_length=HOP)+OFF
rms=librosa.feature.rms(y=y)[0]
# RMS sampled AT beat frames
rms_at_beats=rms[beats]
# essay values
E=[0.129644557833672,0.198803529143333,0.288493871688843,0.286753028631210]
print("RMS at each beat near cut-in:")
i=int(np.argmin(np.abs(bt-CUT_IN)))
for k in range(i-3,i+4):
    print(f"  beat#{k} t={bt[k]:.4f} rms_at_beat={rms_at_beats[k]:.15f}")
print("RMS at each beat near cut-out:")
j=int(np.argmin(np.abs(bt-CUT_OUT)))
for k in range(j-3,j+4):
    print(f"  beat#{k} t={bt[k]:.4f} rms_at_beat={rms_at_beats[k]:.15f}")
# does any consecutive-beat pair reproduce the essay surge 53.345% ?
for k in range(len(bt)-1):
    s=(rms_at_beats[k+1]/rms_at_beats[k]-1)*100
    if abs(s-53.345062)<0.5:
        print(f"  >> consecutive-beat surge {s:.6f}% at beats {k}->{k+1} t={bt[k]:.3f}->{bt[k+1]:.3f} vals {rms_at_beats[k]:.12f}->{rms_at_beats[k+1]:.12f}")
# search exact essay values among rms_at_beats
for tv in E:
    d=np.abs(rms_at_beats-tv); m=int(np.argmin(d))
    print(f"  essay {tv}: nearest beat-RMS idx{m} t={bt[m]:.3f} val={rms_at_beats[m]:.15f} |d|={d[m]:.2e}")
