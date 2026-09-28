# Reproducibility baseline

This repository separates two goals that are easy to conflate:

1. **claim verification** — archived outputs record the numerical baselines used by the essay or by later methodological audits;
2. **software compatibility** — CI checks that the scripts still compile/import and that media-free logic and archived-output invariants remain executable on a current Python runtime.

The copyrighted source media is intentionally absent, so CI cannot recompute the
film-dependent measurements. A dependency update can therefore pass CI while changing
a fresh media-dependent run.

## Recorded analysis environments

The original 2026.09.19 snapshot did not preserve every patch version. Its figure
captions preserve two important major/minor versions:

- `outputs/fig_audio_alignment.png` identifies **librosa 0.11**;
- `outputs/fig_asl_comparison.png` identifies **PySceneDetect 0.7**.

Exact NumPy, OpenCV, Python and FFmpeg patch versions were not preserved with every
historical run, so bit-for-bit reproduction of all pre-snapshot numbers is not claimed.

The **2026-09-28 post-snapshot audit reruns do record their environments inside the
JSON outputs**. They were generated with Python 3.14.7 and, depending on the script:

- NumPy 2.5.2;
- SciPy 1.18.1;
- OpenCV 4.14.0;
- PySceneDetect 0.7.1;
- FFmpeg 9.0.2.

The external YuNet object is pinned by SHA-256 in the README and in scripts 10/14.

`requirements.txt` keeps the analysis libraries inside compatibility bands matching
the recorded major versions where known. Major analysis-library upgrades are reviewed
manually rather than treated as automatically equivalent numerical environments.

## What CI can prove without the film

CI verifies:

- all analysis modules compile and the installed analysis libraries import;
- shell scripts parse;
- required archived artifacts remain present;
- no film, subtitle, extracted audio, or external YuNet model is committed;
- SRT parsing and Monica surface-form classification remain stable;
- the archived A.9 and 2026-09-28 audit JSON baselines retain their recorded numerical
  invariants.

Those tests prove the integrity of the checked-in baseline. They do **not** prove that
a fresh run on the absent media would reproduce it under a changed decoder, detector,
model, or dependency version.

## Re-running the numerical analysis

A full re-run requires the user-supplied inputs listed in `README.md`,
`ffmpeg`/`ffprobe`, and the Python dependencies in `requirements.txt`.

The later audits can be regenerated individually:

- script 10 → betrayal shot / face-height output;
- script 11 → local subtitle-timebase output;
- script 12 → relative-rate / dense-offset output;
- script 13 → ContentDetector calibration / sensitivity output;
- script 14 → Haar/YuNet calibration output.

When regenerating an archived or essay-facing output:

1. record `python --version`, `ffmpeg -version`, and `python -m pip freeze`;
2. use the same source copy, local time base, model object and script parameters;
3. compare the fresh result with the archived JSON / figure / text value;
4. investigate numerical drift before replacing the baseline;
5. if the difference is methodological rather than numerical noise, preserve the old
   result and document the changed operational definition.

Do not treat a successful import test as evidence that a dependency upgrade reproduces
a historical numerical result.
