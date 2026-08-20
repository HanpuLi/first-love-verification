"""
librosa: RMS envelope and onset-beat alignment at the animated cut-points

Supports the analysis reported in the essay appendix.
Media inputs are NOT included in this repository (see README).
"""

import librosa
import numpy as np
y, sr = librosa.load("first_love.mp4", sr=None, offset=4730.0, duration=50.0)
rms = librosa.feature.rms(y=y, hop_length=512)[0]
onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=512)
peaks = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr, hop_length=512, units='time')
times_peaks = 4730.0 + peaks
times_rms = 4730.0 + librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=512)
closest_beat = times_peaks[np.argmin(np.abs(times_peaks - 4742.0))]
idx = np.argmin(np.abs(times_rms - 4742.0))
vol_before = np.mean(rms[idx-10:idx])
vol_after = np.mean(rms[idx:idx+10])
print(f"Closest beat: {closest_beat:.10f}s (offset: {closest_beat - 4742.0:+.10f}s)")
print(f"Volume surge: {(vol_after - vol_before) / vol_before * 100:.15f}%")
