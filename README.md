# Verification materials — *First Love* (Miike Takashi, 2019)

Scripts and archived outputs supporting the computational passages of the essay
**"False Secondary Contradictions: *Giri*, *Ninjō*, Patriarchal Capitalism, and Qualified
Brechtian Disruption in Miike Takashi's *First Love*"** (Hanpu Li).

**Project page:** [On Takashi Miike’s *First Love*](https://hanpuli.github.io/writing/first-love/) · **Author:** [Hanpu Li / 李函璞](https://hanpuli.github.io/)

Scripts 01–09 and the original archived outputs preserve the analysis used for the
2026.09.19 reproducibility snapshot. Scripts 10–14 are later audit additions. The
post-snapshot audit results below were regenerated from the source inputs on
2026-09-28 and archived as JSON rather than reconstructed from prose notes.

---

## What is not here

**No film, subtitle, frame-grab or extracted audio media is redistributed.** The
scripts expect user-supplied inputs:

| Input | What it is |
|---|---|
| `first_love.mp4` | 92.9-minute off-air copy used by the earlier A.8–A.10 passes |
| `first_love_FilmFour_2026-01-12.mp4` | Complete off-air FilmFour recording used by the later audits |
| `first_love_en.srt` | English subtitle track, 1,073 entries, release timecodes |
| `first_love_ja.srt` | Japanese subtitle track, 39 entries (sparse community upload) |
| `bob_transcript_cleaned.txt` | ASR transcript of the English audio, used as a consistency check |
| `face_detection_yunet_2023mar.onnx` | OpenCV Zoo YuNet model used by scripts 10 and 14; exact hash below |

Frames reproduced in the essay are low-resolution stills used for non-commercial
scholarly criticism. Copyright in *First Love* (2019) remains with its rights holders.

---

## Time bases

Three clocks are involved and they are not interchangeable.

| Clock | Used for | Runtime / properties |
|---|---|---|
| Release track | Body-text timecodes | c. 108 min |
| Complete off-air FilmFour recording | Figure-caption recording clock; scripts 10–14 where specified | 134.9 min, 25 fps, 720×576, retained ad breaks |
| 92.9-minute off-air copy | Earlier A.8–A.10 passes and one side of the cross-copy audits | 92.9 min, 24 fps, 1280×538, abridged |

Body timecodes were checked against `first_love_en.srt`: `Are you going to increase your
debt again?` at 00:11:29 (subtitle 00:11:29.64); `Yasu, Monica wants a hit` at 00:11:59
(00:11:59.59); the on-screen threat at 00:23:49 (00:23:49.72) and 00:32:06
(00:32:06.05); and `Yasu! No!` at 00:39:48 (00:39:48.51).

The two off-air copies also differ in playback rate. Script 12 independently tests
three rate hypotheses from their audio envelopes. The best of the tested hypotheses
is a **25/24 = 1.0416667** stretch of the FilmFour envelope, consistent with the
standard PAL speed-up relative to the 24-fps copy. This establishes only the relative
playback-rate relation between those two off-air copies. Scripts 10–11 use `0.96` as
a fixed release-to-FilmFour rate input from the earlier audit. Script 12 is consistent
with that value, but it does not independently establish it for the release track,
which is not one of script 12's inputs.

Retained ad breaks make the release-to-recording offset piecewise rather than global.
A local offset must be estimated for the relevant stretch; script 11 does this for the
betrayal sequence.

---

## Scripts

| Script | Appendix / role | What it establishes |
|---|---|---|
| `01_stream_inspect.sh` | A.2 | Container, frame rate and duration |
| `02_scene_detect.sh` | A.3 | Brightness-normalised scene-change detection |
| `03_extract_frames.sh` | A.4 | Frame / interval extraction at specified timestamps |
| `04_audio_alignment.py` | A.8 | RMS and onset-beat analysis at the animated cut-points |
| `05_shot_length.py` | A.9 | Windowed ASL on the 92.9-minute copy; boundary-clipped segments are included |
| `06_face_scale_audit.py` | A.10 | Haar-based candidate counts; not identity recognition |
| `07_subtitle_parse.py` | A.11.1 | SRT parsing |
| `08_monica_classify.py` | A.11.2 | Surface-form classification of entries naming Monica |
| `09_monica_subtitle_analysis.py` | A.11 | Full discourse pass |
| `10_shot_scale_betrayal.py` | post-snapshot audit | Betrayal shot segmentation plus continuous YuNet face-height proxy |
| `11_subtitle_timebase.py` | post-snapshot audit | Local burned-in-subtitle / release-SRT offset search at fixed rate 0.96 |
| `12_pal_rate_audit.py` | post-snapshot audit | Cross-copy audio-envelope rate hypotheses and dense local offset steps |
| `13_content_detector_calibration.py` | post-snapshot audit | Cross-copy PySceneDetect threshold sensitivity |
| `14_face_detector_calibration.py` | post-snapshot audit | Haar / YuNet behaviour on a known close-up calibration window |

Run `python3 -m pip install -r requirements.txt` first. Scripts 01–04 and 12 also
require `ffmpeg` / `ffprobe` as documented by the scripts. Source media are
intentionally absent from CI, so CI checks importability, media-free tests and the
integrity of the archived outputs; it cannot regenerate film-dependent measurements.

The citable repository snapshot remains **v2026.09.19**. Scripts 10–14 and the
2026-09-28 audit outputs are post-snapshot material until a later release is tagged.
See [CITATION.cff](CITATION.cff), [CHANGELOG.md](CHANGELOG.md),
[REPRODUCIBILITY.md](REPRODUCIBILITY.md) and [LICENSING.md](LICENSING.md).

---

## Archived outputs

The original A.9 baseline is `outputs/a9_shots.json`:

- melee window 4300–4742 s on the 92.9-minute copy: **62 windowed shot segments,
  ASL 7.129032 s**, covering 442.0 s;
- animation window: **10 segments, ASL 2.604167 s**.

“62” is a count of the shot segments returned when PySceneDetect is started at the
analysis-window boundary; the first and last may be clipped by that boundary. It is
not interchangeable with an alternative definition that counts only complete shots
strictly contained inside the window.

The post-snapshot audits were re-run from the media on 2026-09-28 and archived as:

- `outputs/pal_rate_audit_2026-09-28.json`
- `outputs/subtitle_timebase_betrayal_2026-09-28.json`
- `outputs/manual_timebase_checks_2026-09-28.json`
- `outputs/content_detector_calibration_2026-09-28.json`
- `outputs/face_detector_calibration_2026-09-28.json`
- `outputs/betrayal_shot_face_audit_2026-09-28.json`

The JSON files record the numerical baseline and, where applicable, the library
versions used in the rerun. The accompanying tests prevent these archived values from
being silently changed.

---

## Relative-rate audit: what the 4.1667% claim rests on

Script 12 extracts both off-air soundtracks as temporary 8 kHz mono PCM and converts
them to 100 Hz log-RMS envelopes. Across **46 anchors**, each using a 20-second window,
it tests three rate hypotheses:

| FilmFour-envelope treatment | Mean NCC | Median NCC | anchors with NCC > 0.85 |
|---|---:|---:|---:|
| no scaling, 1.000000 | **0.575** | 0.568 | 5/46 |
| stretch by 25/24, 1.041667 | **0.817** | **0.902** | **27/46** |
| opposite direction, 0.960000 | **0.544** | 0.512 | 4/46 |

The 25/24 hypothesis is therefore substantially better on this experiment. This
establishes the **relative playback-rate relation of these two source copies**; it does
not by itself identify every edit or ad boundary.

After applying that rate correction, a dense local alignment across the region
containing the betrayal sequence gives four high-confidence offset plateaus at about
**631.36, 652.87, 677.94 and 719.77 s**. Their three positive steps are approximately
**21.51 + 25.07 + 41.83 = 88.405 s**. This is evidence that the abridged 92.9-minute
copy loses a net 88.4 s relative to the complete recording across that local region.
The value is a cross-copy edit measurement, not a release-to-recording offset.

---

## Local subtitle timebase audit

Script 11 solves a narrower problem: where the betrayal sequence sits on the complete
FilmFour recording once the rate term is fixed at `0.96`.

In the FilmFour window 2100–2400 s it samples the lower subtitle region with an
integer frame stride chosen by rounding `fps / 10`. On the archived 25-fps input this
is a two-frame stride, so the effective sampling rate is **12.5 Hz**, not 10 Hz. It
then converts bright subtitle activity to a binary signal, maps the release SRT cue
activity through candidate offsets, and searches offsets 300.0–469.9 s in 0.1-second
steps. The 2026-09-28 rerun gives:

- best offset: **357.0 s**;
- correlation: **0.673228**;
- local mapping: `t_recording = 0.96 × t_release + 357.0`.

For example, release 00:34:02 (`What's happening?`, 2042 s) maps to **2317.32 s**.
A separate local frame check found the cue absent at 2317.3 s and visible at 2318.5 s,
so its observed onset is bracketed by those samples: **(2317.3, 2318.5] s**. That is a
spot check at roughly 1.2-second granularity, not a frame-exact onset measurement.

The audit also preserves a failed-method diagnostic. A 2026-08-26 single-frame
anchoring attempt produced offset **385.8 s**; the distributed method corrected it to
357.0 s, a difference of **28.8 s**. The 385.8 value is retained as historical evidence
of that failed anchoring method, not as a valid timebase result.

The local offset is not portable across retained ad breaks, and the configured search
range is itself a local prior. A plausible correlation peak outside the correct
offset range is not evidence of a valid mapping.

---

## PySceneDetect threshold sensitivity

Script 13 uses a stretch present in both off-air copies to measure how
`ContentDetector` behaves after the rate/offset mapping is applied. These are
**cross-copy operational reference sets**, not manually annotated ground truth.

Using the 92.9-minute copy at threshold 27.0 as a 36-cut reference:

- FilmFour threshold 27.0 matches **30/36**, misses 6, adds 0;
- FilmFour threshold 18.0 matches **36/36**, misses 0, adds 3.

Using FilmFour threshold 18.0 as a 39-cut reference:

- 92.9-minute copy threshold 27.0 matches **36/39 (92.3%)**, misses 3, adds 0;
- 92.9-minute copy threshold 22.0 matches **39/39**, with no misses or extras.

This matters for interpreting ASL as well as shot counts. On the fixed complete-
broadcast melee window 6048.0–6703.8 s:

| FilmFour threshold | Segments | ASL on recording clock | Rate-corrected ASL |
|---|---:|---:|---:|
| 18.0 | 130 | 5.045 s | **5.255 s** |
| 22.0 | 96 | 6.831 s | **7.116 s** |

Thus the often-quoted “about 7.12 s on the complete copy” is a real **threshold-22
sensitivity result**, not a detector-independent ground truth. Its proximity to the
92.9-copy A.9 value of 7.129 s is informative, but the large threshold effect must be
kept with that comparison.

---

## Haar / YuNet calibration

The known calibration target is the held Julie close-up whose detected shot begins at
**5943.32 s** on the FilmFour recording and lasts **10.72 s**.

The historical 2026-08-26 comparison used unequal sampling protocols: three within-shot
samples for Haar and five for YuNet. Re-running those exact protocols reproduces
**Haar 8/14** versus **YuNet 12/14** segments with at least one detected face.

For an apples-to-apples five-sample comparison, the 2026-09-28 rerun gives
**Haar 9/14** versus **YuNet 12/14**. More importantly, on the independently known
Julie close-up:

- Haar: **0/5** sampled frames detect a face;
- YuNet: **5/5** sampled frames detect a face;
- YuNet median largest-face-height / frame-height ratio: **0.457569**.

This demonstrates a detector failure mode relevant to the low-resolution, low-key
FilmFour material. It does **not** establish universal Haar/YuNet recall, and the
0.457569 measurement is not by itself a calibration of cinematic ECU/CU/MCU/MS/LS
category boundaries. For that reason scripts 10 and 14 report continuous face-height
ratios rather than categorical shot-scale labels.

---

## Betrayal-sequence audit

Script 10 uses the subtitle-derived FilmFour window **2147.4–2301.0 s**, YuNet, five
samples per detected segment and ContentDetector threshold **18.0**, the high-recall
FilmFour operating point identified by script 13.

The 2026-09-28 archived run reports:

- **24** windowed shot segments;
- **ASL 6.400 s**;
- longest segment **37.80 s**;
- shortest segment **0.84 s**;
- a YuNet face detection in **13/24** segments;
- median face-height ratio among those segments **0.231**;
- maximum face-height ratio **0.544**.

These values are detector- and threshold-dependent. The script does not identify
characters and does not infer cinematic shot-scale categories from the ratios.

---

## Which copy each analysis uses

| Script | Copy / inputs |
|---|---|
| 04 | 92.9-minute copy |
| 05 / A.9 archived run | 92.9-minute copy |
| 06 | 92.9-minute copy |
| 10 | complete FilmFour recording + YuNet |
| 11 | complete FilmFour recording + release SRT |
| 12 | both off-air copies |
| 13 | both off-air copies |
| 14 | complete FilmFour recording + YuNet |

---

## YuNet model boundary

The external model is OpenCV Zoo
`face_detection_yunet_2023mar.onnx`. The expected Git LFS object is:

`sha256:8f2383e4dd3cfbb4553ea8718107fc0423210dc964f9f4280604804ed2552fa4`

with size **232589 bytes**. Scripts 10 and 14 verify that SHA-256 before analysis.
Fetch the Git LFS object rather than the small pointer returned by a non-LFS raw-file
fetch. The model is intentionally ignored by Git and is not covered by this
repository's MIT licence.

---

## Limitations

- The relation of either off-air copy to a definitive commercial cut has not been independently established.
- The 92.9-minute copy is abridged; a coordinate on it is not automatically a coordinate on the release track or complete recording.
- Audio matching establishes a strong relative rate signal, but edit/ad boundaries still require local alignment.
- Subtitle-activity matching is local and search-range dependent.
- PySceneDetect counts and ASL are threshold-sensitive; a detector operating point is part of the measurement.
- Face detection is detector-, threshold-, sampling- and copy-dependent; a null face detection is not evidence that no face is present.
- The Japanese subtitle file is sparse (39 entries against 1,073 in the English release) and is corroborative rather than suitable for systematic coverage claims.
