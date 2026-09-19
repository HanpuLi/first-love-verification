# Reproducibility baseline

This repository separates two goals that are easy to conflate:

1. **claim verification** — the archived outputs and README record what was actually reported in the essay;
2. **software compatibility** — CI checks that the scripts still import and that media-free logic remains executable on a current Python runtime.

The original media is intentionally absent, so CI cannot recompute the film-dependent numerical results. A dependency update that changes a detector, decoder or signal-processing algorithm can therefore pass import checks while still changing the published numbers.

## Recorded analysis environment

The archived figure captions preserve two important major/minor versions:

- `outputs/fig_audio_alignment.png` identifies **librosa 0.11**;
- `outputs/fig_asl_comparison.png` identifies **PySceneDetect 0.7**.

Exact NumPy, OpenCV, Python and FFmpeg patch versions were not preserved with the archived run. Bit-for-bit reproduction of every historical number is therefore not claimed.

`requirements.txt` keeps the analysis libraries inside compatibility bands that match the recorded major versions where known. Major analysis-library upgrades are deliberately reviewed manually rather than accepted through routine Dependabot version bumps.

## What CI can prove without the film

CI verifies:

- all analysis modules compile and import;
- shell scripts parse;
- required archived artifacts remain present;
- no film, subtitle or audio source media is committed;
- SRT parsing and Monica surface-form classification are covered by media-free regression tests.

## Re-running the numerical analysis

A full re-run requires the user-supplied inputs listed in `README.md`, `ffmpeg`/`ffprobe`, and the Python dependencies in `requirements.txt`.

When regenerating an essay-facing output after a dependency upgrade:

1. record `python --version`, `ffmpeg -version`, and `python -m pip freeze`;
2. rerun the affected script against the same source input and time base;
3. compare the result with the archived output and the figure/text value;
4. document any numerical drift before updating the baseline.

Do not treat a successful import test as evidence that a new major version reproduces a historical numerical result.
