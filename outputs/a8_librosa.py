import librosa, numpy as np
np.set_printoptions(precision=15, suppress=True)

OFFSET=4730.0
CUT_IN=4742.0
CUT_OUT=4768.0
HOP=512

def run(path, sr_target, label):
    y, sr = librosa.load(path, sr=sr_target, offset=0.0, mono=True)
    # note seg already starts at OFFSET (4730). absolute time = OFFSET + local
    print(f"\n===== {label}  sr={sr} len={len(y)} dur={len(y)/sr:.4f}s hop={HOP} =====")
    # beat track
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr, hop_length=HOP)
    beat_times = librosa.frames_to_time(beats, sr=sr, hop_length=HOP) + OFFSET
    # nearest beat to cut-in
    i = int(np.argmin(np.abs(beat_times - CUT_IN)))
    nb = beat_times[i]; off = nb - CUT_IN
    print(f"tempo={np.atleast_1d(tempo)[0]:.6f}")
    print(f"nearest beat to cut-in {CUT_IN}: {nb:.10f}  offset {off:+.10f}  ({off*sr/HOP:.4f} hops)")
    # RMS
    rms = librosa.feature.rms(y=y)[0]
    rt = librosa.times_like(rms, sr=sr, hop_length=HOP) + OFFSET
    # frame index nearest cut-in and cut-out
    ci = int(np.argmin(np.abs(rt-CUT_IN)))
    co = int(np.argmin(np.abs(rt-CUT_OUT)))
    print(f"RMS frames around cut-in (idx {ci}, t={rt[ci]:.4f}):")
    for k in range(ci-3, ci+4):
        print(f"   t={rt[k]:.5f}  rms={rms[k]:.18f}")
    # search essay values in rms
    targets=[0.129644557833672,0.198803529143333,0.288493871688843,0.286753028631210]
    for tv in targets:
        d=np.abs(rms-tv); j=int(np.argmin(d))
        print(f"   closest to {tv}: idx{j} t={rt[j]:.4f} val={rms[j]:.18f} (|d|={d[j]:.2e})")
    # surge before->after cut-in (frame before vs at)
    before=rms[ci-1]; after=rms[ci]
    print(f"surge (frame {ci-1}->{ci}): {before:.18f} -> {after:.18f} = {(after/before-1)*100:.15f}%")
    # cut-out sustain
    b2=rms[co-1]; a2=rms[co]
    print(f"cutout (frame {co-1}->{co}): {b2:.18f} -> {a2:.18f} = {(a2/b2-1)*100:.15f}%")

run("seg_48k_mono.wav", 48000, "NATIVE 48k")
run("seg_22k_mono.wav", 22050, "RESAMPLED 22.05k")
run("seg_48k_mono.wav", None, "sr=None(file 48k)")
