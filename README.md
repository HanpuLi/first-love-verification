# Verification materials — *First Love* (Miike Takashi, 2019)

Scripts and archived outputs supporting the computational passages of the essay
**"False Secondary Contradictions: *Giri*, *Ninjō*, Patriarchal Capitalism, and Qualified
Brechtian Disruption in Miike Takashi's *First Love*"** (Hanpu Li).

**Project page:** [On Takashi Miike’s *First Love*](https://hanpuli.github.io/writing/first-love/) · **Author:** [Hanpu Li / 李函璞](https://hanpuli.github.io/)

Scripts 01–09 and the archived outputs preserve the analysis used for the essay's
2026.09.19 reproducibility snapshot. Scripts 10–11 are later audit additions. They are
published so that the claims they actually compute can be checked rather than taken on
trust.

---

## What is not here

**No media is redistributed.** The film, its subtitle files, and the extracted frames are
not included, and cannot be: they are third-party copyright material held for private
study. The scripts expect the following inputs, which a reader must supply:

| Input | What it is |
|---|---|
| `first_love.mp4` | 92.9-minute off-air copy used by the earlier A.8–A.10 passes |
| `first_love_FilmFour_2026-01-12.mp4` | Complete off-air FilmFour recording used by scripts 10–11 |
| `first_love_en.srt` | Official English subtitle track (Norman England translation), 1,073 entries, release timecodes |
| `first_love_ja.srt` | Japanese subtitle track, 39 entries (sparse community upload) |
| `bob_transcript_cleaned.txt` | ASR transcript of the English audio, produced independently as a consistency check |
| `face_detection_yunet_2023mar.onnx` | OpenCV Zoo YuNet model used by script 10; exact content hash below |

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
| Complete off-air FilmFour recording | Figure-caption recording clock and scripts 10–11 | 134.9 min, 25 fps, 720×576, with retained ad breaks |
| 92.9-minute off-air copy | Earlier A.8–A.10 passes | 92.9 min, 24 fps, 1280×538, burned-in Simplified-Chinese subtitles |

Body timecodes were verified against `first_love_en.srt`: `Are you going to increase your
debt again?` at 00:11:29 (subtitle 00:11:29.64); `Yasu, Monica wants a hit` at 00:11:59
(00:11:59.59); the on-screen threat at 00:23:49 (00:23:49.72) and 00:32:06 (00:32:06.05);
`Yasu! No!` at 00:39:48 (00:39:48.51).

There is no single global release/recording offset across retained ad breaks. Script 11
therefore performs a **local** search. It fixes the rate term at 0.96 recording seconds
per release second and estimates only the offset inside one configured window. That
fixed rate is an input to the analysis, not a value independently estimated by script 11.

---

## Scripts

| Script | Appendix / role | What it establishes |
|---|---|---|
| `01_stream_inspect.sh` | A.2 | Container, frame rate and duration of each copy |
| `02_scene_detect.sh` | A.3 | Brightness-normalised scene-change detection for low-key sequences |
| `03_extract_frames.sh` | A.4 | Single-frame and interval extraction at exact timestamps |
| `04_audio_alignment.py` | A.8 | RMS envelope and onset-beat alignment at the animated cut-points. Reported result: nearest beat onset to the cut-in (4742.0 s) at 4741.925 s, offset −0.075 s; RMS 0.1296 → 0.1988 across the cut-in (+53.3%) |
| `05_shot_length.py` | A.9 | Windowed average shot length for 4300–4742 s. The statistic is 62 **shot segments intersecting the 442 s analysis window**, ASL 7.129 s; the first/last segments may be clipped by the window boundaries |
| `06_face_scale_audit.py` | A.10 | Character presence and a shot-scale proxy. **Candidate counts, not identifications**: Haar detection with greyscale correlation cannot reliably distinguish the film's dark-haired women. No figure from this script is used as an empirical claim in the essay |
| `07_subtitle_parse.py` | A.11.1 | SRT parsing for both tracks |
| `08_monica_classify.py` | A.11.2 | Surface-form classification of the 25 entries naming Monica |
| `09_monica_subtitle_analysis.py` | A.11 | The full discourse pass: scene windows, JA/EN alignment, speech-function counts |
| `10_shot_scale_betrayal.py` | post-snapshot audit | Shot segmentation plus a continuous YuNet face-height proxy across the betrayal window; it does **not** assign categorical ECU/CU/MCU/MS/LS labels |
| `11_subtitle_timebase.py` | post-snapshot audit | Local subtitle-activity offset search conditional on a fixed 0.96 rate term; it reports the best offset and correlation in the configured search window |

Run with `python3 -m pip install -r requirements.txt` first. The shell scripts need
`ffmpeg` and `ffprobe` on `PATH`. The repository keeps analysis libraries inside
compatibility bands rather than automatically accepting major upgrades, because the
copyrighted source media is intentionally absent from CI. See
[REPRODUCIBILITY.md](REPRODUCIBILITY.md) for the recorded environment boundary and the
procedure for validating numerical drift.

The citable repository snapshot remains **v2026.09.19**. Scripts 10–11 and the later
methodological corrections are post-snapshot changes until a later release is tagged.
See [CITATION.cff](CITATION.cff) for machine-readable citation metadata,
[CHANGELOG.md](CHANGELOG.md) for the snapshot boundary, and
[LICENSING.md](LICENSING.md) for the code/research-media rights boundary.

---

## Archived outputs

`outputs/` holds the run products the essay cites, so that a reader can compare a fresh
run against the run actually reported. `outputs/a9_shots.json` fixes the A.9 baseline:
62 shot segments / 7.129032 s for the 4300–4742 s melee window and 10 segments /
2.604167 s for the animation window.

Scripts 10–11 do not yet have archived numerical run products in this repository.
Their numerical results must therefore be regenerated from the user-supplied inputs;
the README does not treat exploratory measurements from unarchived runs as repository
evidence.

---

## Limitations, stated once

- The relation of either off-air copy to a definitive cut has not been independently established.
- Audio was analysed from the recording's own soundtrack; confirmation of perceived acoustic sync is subject to the limitation of off-air encoding quality.
- Brightness and contrast lifts applied to dark scenes are reading aids, disclosed in each affected caption. They alter exposure and saturation, not framing, scale or staging, which are what the figures are cited for.
- The Japanese subtitle file is a sparse community upload (39 entries against 1,073 in the English release). Its evidential role is corroborative only; it cannot support systematic speech-function analysis.
- Face-detection results are detector-, threshold-, sampling- and copy-dependent. A detector null result is not evidence that no face is present.

---

## Local subtitle timebase audit

Script `11_subtitle_timebase.py` searches one defined problem only. In the
2100–2400 s window of the complete recording it:

1. fixes the rate term at `0.96`;
2. converts the burned-in subtitle region to a binary activity series;
3. converts `first_love_en.srt` cues to a binary reference series; and
4. searches offsets from 300.0 to 469.9 s for the highest correlation.

On the original audit input this procedure reported an offset of **357.0 s** at
correlation **0.673**, giving the local relation

`t_recording = 0.96 × t_release + 357.0 s`.

That statement is deliberately narrow. The script does **not** estimate the 0.96 rate
term, establish whole-film linearity, bridge ad breaks, or claim exact frame-level sync.
The configured search range is a local prior, and a window with little subtitle activity
may be uninformative; the script prints the subtitle-present fraction and fails explicitly
when the sampled activity is degenerate.

---

## Which copy each script runs on

| Script | Copy | Note |
|---|---|---|
| `04_audio_alignment.py` | **92.9-min copy** | offset 4730 s is on that clock |
| `05_shot_length.py`, `outputs/a9_asl.py` | **92.9-min copy** | windowed shot-segment definition; melee window 4300–4742 s |
| `06_face_scale_audit.py` | **92.9-min copy** | Haar-based candidate counts only |
| `10_shot_scale_betrayal.py` | **complete broadcast recording** | 2147.4–2301.0 s; YuNet face-height proxy |
| `11_subtitle_timebase.py` | **complete broadcast recording** | needs burned-in English subtitle activity plus `first_love_en.srt` |

## Face detector boundary and YuNet model

`06_face_scale_audit.py` and `10_shot_scale_betrayal.py` use different detectors on
different copies for different purposes. This repository does not archive a controlled
Haar-versus-YuNet benchmark, so no cross-detector performance numbers are claimed here.
Script 10 reports only the continuous detected-face-height ratio described above.

The YuNet model is the OpenCV Zoo file
`face_detection_yunet_2023mar.onnx`. Its expected Git LFS object is:

`sha256:8f2383e4dd3cfbb4553ea8718107fc0423210dc964f9f4280604804ed2552fa4`
(232589 bytes).

Script 10 verifies that SHA-256 before analysis. Fetch the Git LFS object rather than the
small pointer returned by a non-LFS raw-file fetch.
