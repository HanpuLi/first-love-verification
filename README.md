# Verification materials — *First Love* (Miike Takashi, 2019)

Scripts and archived outputs supporting the computational passages of the essay
**"False Secondary Contradictions: *Giri*, *Ninjō*, Patriarchal Capitalism, and Qualified
Brechtian Disruption in Miike Takashi's *First Love*"** (Hanpu Li).

**Project page:** [On Takashi Miike’s *First Love*](https://hanpuli.github.io/writing/first-love/) · **Author:** [Hanpu Li / 李函璞](https://hanpuli.github.io/)

Everything reported in the essay's appendix was produced by the scripts below. They are
published so that the claims can be checked rather than taken on trust.

---

## What is not here

**No media is redistributed.** The film, its subtitle files, and the extracted frames are
not included, and cannot be: they are third-party copyright material held for private
study. The scripts expect the following inputs, which a reader must supply:

| Input | What it is |
|---|---|
| `first_love.mp4` | An off-air recording (92.9 min) or the complete broadcast recording |
| `first_love_en.srt` | Official English subtitle track (Norman England translation), 1,073 entries, release timecodes |
| `first_love_ja.srt` | Japanese subtitle track, 39 entries (sparse community upload) |
| `bob_transcript_cleaned.txt` | ASR transcript of the English audio, produced independently as a consistency check |

Frames reproduced in the essay are low-resolution stills used for non-commercial
scholarly criticism (UK: CDPA 1988 s.30; US: 17 U.S.C. §107). Copyright in *First Love*
(2019) remains with its rights holders.

---

## Time bases

Three copies are involved and **they do not share a clock**. This matters when running
anything below against a timestamp taken from the essay.

| Clock | Used for | Runtime |
|---|---|---|
| Release track | All timecodes in the essay's **body text** | c. 108 min |
| Complete off-air FilmFour recording | All timecodes in the essay's **figure captions** ("recording time base") | 134.9 min, 25 fps, 720×576. **PAL-speeded: it runs 4.1667% fast**, and it retains its ad breaks |
| 92.9-minute off-air copy | Some earlier frame passes | 92.9 min, 24 fps, 1280×538, burned-in Simplified-Chinese subtitles. Cut: the betrayal sequence alone loses 88.4 s, and the ending is shortened |

Body timecodes were verified against `first_love_en.srt`: `Are you going to increase your
debt again?` at 00:11:29 (subtitle 00:11:29.64); `Yasu, Monica wants a hit` at 00:11:59
(00:11:59.59); the on-screen threat at 00:23:49 (00:23:49.72) and 00:32:06 (00:32:06.05);
`Yasu! No!` at 00:39:48 (00:39:48.51).

The release/recording offset is established at **one** point only and has not been checked
for linearity across the running time. Do not assume it is constant.

---

## Scripts

| Script | Appendix | What it establishes |
|---|---|---|
| `01_stream_inspect.sh` | A.2 | Container, frame rate and duration of each copy |
| `02_scene_detect.sh` | A.3 | Brightness-normalised scene-change detection for low-key sequences |
| `03_extract_frames.sh` | A.4 | Single-frame and interval extraction at exact timestamps |
| `04_audio_alignment.py` | A.8 | RMS envelope and onset-beat alignment at the animated cut-points. Reported result: nearest beat onset to the cut-in (4742.0 s) at 4741.925 s, offset −0.075 s; RMS 0.1296 → 0.1988 across the cut-in (+53.3%) |
| `05_shot_length.py` | A.9 | Average shot length across the climax window (4300–4742 s). Reported result: ASL 7.129 s across 62 detected cuts |
| `06_face_scale_audit.py` | A.10 | Character presence and a shot-scale proxy. **Candidate counts, not identifications**: Haar detection with greyscale correlation cannot reliably distinguish the film's dark-haired women. No figure from this script is used as an empirical claim in the essay |
| `07_subtitle_parse.py` | A.11.1 | SRT parsing for both tracks |
| `08_monica_classify.py` | A.11.2 | Surface-form classification of the 25 entries naming Monica |
| `09_monica_subtitle_analysis.py` | A.11 | The full discourse pass: scene windows, JA/EN alignment, speech-function counts |

Run with `python3 -m pip install -r requirements.txt` first. The shell scripts need
`ffmpeg` and `ffprobe` on `PATH`. The repository keeps analysis libraries inside
compatibility bands rather than automatically accepting major upgrades, because the
copyrighted source media is intentionally absent from CI. See
[REPRODUCIBILITY.md](REPRODUCIBILITY.md) for the recorded environment boundary and the
procedure for validating numerical drift.

The citable repository snapshot is **v2026.09.19**. See [CITATION.cff](CITATION.cff)
for machine-readable citation metadata, [CHANGELOG.md](CHANGELOG.md) for the snapshot
boundary, and [LICENSING.md](LICENSING.md) for the code/research-media rights boundary.

---

## Archived outputs

`outputs/` holds the run products the essay cites, so that a reader can compare a fresh run
against the run actually reported. Where an output is missing, the essay's claim rests on
the figures reproduced in the text.

---

## Limitations, stated once

- The relation of either off-air copy to a definitive cut has not been independently established.
- Audio was analysed from the recording's own soundtrack; confirmation of perceived acoustic sync is subject to the limitation of off-air encoding quality.
- Brightness and contrast lifts applied to dark scenes are reading aids, disclosed in each affected caption. They alter exposure and saturation, not framing, scale or staging, which are what the figures are cited for.
- The Japanese subtitle file is a sparse community upload (39 entries against 1,073 in the English release). Its evidential role is corroborative only; it cannot support systematic speech-function analysis.

---

## How the clocks actually relate (measured, 2026-08)

The gap between the recording and the release track is **not a constant, and not one
mechanism**. Two effects run against each other:

- **PAL speed-up.** The recording runs **4.1667% fast**. Established by cross-correlating
  log-RMS audio envelopes: mean normalised correlation **0.817** with the recording
  stretched by that factor, against **0.575** unstretched and **0.544** stretched the
  other way. This alone makes the gap *shrink* as the film runs.
- **Retained ad breaks.** These step the gap *up*, by several minutes at a time.

Within a single stretch between breaks the correspondence is strictly linear: successive
anchors hold to within **0.1 s**. Across the whole running time it is neither linear nor
recoverable from any single constant.

**To fix an exact correspondence at a given point**, use `11_subtitle_timebase.py`, which
correlates the recording's burned-in subtitle activity against `first_love_en.srt`. Over
the betrayal sequence this gives `t_recording = 0.96 × t_release + 357.0 s` at
correlation 0.673, confirmed by an independent frame check to within 1.2 s.

What does *not* work, on this material: correlating the subtitle file against an audio
envelope (0.09–0.36 over the whole film, 0.21–0.375 locally), and single-point anchoring
from one sampled frame, which was found to be **off by 28.8 s with no internal sign that
it was wrong**. Two further cautions are in the header of `11_subtitle_timebase.py`.

---

## Which copy each script runs on

| Script | Copy | Note |
|---|---|---|
| `04_audio_alignment.py` | **92.9-min copy** | offset 4730 s is on that clock |
| `05_shot_length.py`, `outputs/a9_asl.py` | **92.9-min copy** | melee window 4300–4742 s; 4742 s is the animation cut-in |
| `06_face_scale_audit.py` | **92.9-min copy** | see the warning below |
| `10_shot_scale_betrayal.py` | **complete broadcast recording** | 2147.4–2301.0 s |
| `11_subtitle_timebase.py` | **complete broadcast recording** | needs the burned-in subtitles |
| The `librosa` figures for the Figure 5 close-up (5940–5960 s) | **complete broadcast recording** | spectral centroids sit 4.1667% above their release-track values; RMS is unaffected |

## ⚠️ On the Haar cascade in `06_face_scale_audit.py`

`haarcascade_frontalface_default` **fails on the complete broadcast recording**. Tested
against a target the essay independently confirms — the held medium close-up of Julie at
5943.3 s, 10.72 s long — Haar returns no face at all, while YuNet returns it on 5 of 5
sampled frames at 0.458 of frame height. Over the same 160-second window Haar found faces
in 8 of 14 shots, YuNet in 12 of 14.

The material is 720×576 and lit low-key. **A null result from Haar on this copy is not
evidence that no face is present**, and no "there is no close-up here" claim should rest
on it. `10_shot_scale_betrayal.py` uses YuNet for exactly this reason. How Haar performs
on the higher-resolution 92.9-minute copy, which is what A.10 actually used, has not been
tested.

The YuNet model (`face_detection_yunet_2023mar.onnx`, OpenCV Zoo) is **not included** —
it is a third-party file, and it is stored with Git LFS, so fetch it from the media
endpoint rather than `raw.githubusercontent.com`, which returns a 131-byte pointer.
