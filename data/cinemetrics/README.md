# Frame-accurate shot timings: *First Love* (2019), betrayal sequence

**Contributor:** Hanpu Li · **Director:** Takashi Miike · **Film:** *First Love* (*Hatsukoi*, 2019).

**Public record (13 October 2026):** The [Cinemetrics contribution](https://cinemetrics.uchicago.edu/movie/0d9aff11-65ef-4c3e-90e7-99cbde4649ca) originally displayed **18 intervals / 150.9 s / ASL 8.4 s**, including an unwanted opening fragment. After the curator's amendment, the headline displayed **17 shots / 147.9 s / ASL 8.7 s**. The public shot list still placed one internal cut at **88.0 s** instead of the frame-indexed **87.72 s**. The [before-and-after public shot-list snapshots](public-record-audit/README.md) document both states and the unique altered boundary.

The corrected sample consists of **17 complete consecutive shots**, bounded by two real edits, over **147.88 seconds**. Mean shot length: **8.698824 s**; median: **4.92 s**. It is a *sequence-level* statistic, **not** the full film's average shot length.

## Reproducible data

- [Shot timings CSV](first-love-betrayal-filmfour-17-shots.csv): 17 complete shots, start/end timestamps and frame indices in the source recording.
- [Cinemetrics FACT .cmsx](first-love-betrayal-corrected.cmsx): corrected official-tool export; the public headline now reflects its count and total, with one remaining internal timing discrepancy in the published shot list.
- [Standalone verifier](verify_dataset.py): checks CSV continuity and frame indices against the 17 shot-end markers in the FACT export.

The source is a privately held 2026-01-12 FilmFour off-air recording, 720×576 at 25 fps, including advertisements outside this excerpt. The source-recording window is **2150.44–2298.32 s**. It is not the release print's time base. These boundaries were obtained with PySceneDetect 0.7.1 ContentDetector threshold 22 and checked against adjacent frames; threshold 18 introduced motion-related false positives. Shot scales were not classified. No video, subtitles, audio or film stills are redistributed.

### Verification

Run from the repository root with Python 3 (standard library only):

    python3 data/cinemetrics/verify_dataset.py
    python3 -m unittest discover -s tests -v

The verifier checks all 17 shot durations, 25 fps frame indices, contiguous boundaries, summary statistics, and agreement with the FACT export. The final shot-end marker is at local time 147.88 seconds. FACT also stores a legacy markers string truncated to deciseconds; verification uses the higher-precision shotMarkers timestamps for the frame comparison. These tests check the published data's internal consistency. Identifying actual film edits requires the separate source-frame review.

### Attribution

Li, Hanpu (2026). *First Love (2019): betrayal-sequence shot-length measurements* [research dataset]. Accompanying the [First Love verification materials](../../README.md). Cinemetrics public record: [submission link](https://cinemetrics.uchicago.edu/movie/0d9aff11-65ef-4c3e-90e7-99cbde4649ca). Historical public-record snapshots: [13 October amendment audit](public-record-audit/README.md).

The published files allow the dataset's numerical and export consistency to be checked without distributing the source recording.
