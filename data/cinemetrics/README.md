# Frame-accurate shot timings: *First Love* (2019), betrayal sequence

**Contributor:** Hanpu Li · **Director:** Takashi Miike · **Film:** *First Love* (*Hatsukoi*, 2019).

**Dataset status:** Locally verified correction. The [public Cinemetrics record](https://cinemetrics.uchicago.edu/movie/0d9aff11-65ef-4c3e-90e7-99cbde4649ca) currently reports **18 shots / 150.9 s / ASL 8.4 s** because it includes an unwanted initial 3.04-second partial shot. A correction request has been sent to the database curator. **Do not cite the public record's summary as the corrected result until the curator updates it.**

The corrected sample consists of **17 complete consecutive shots**, bounded by two real edits, over **147.88 seconds**. Mean shot length: **8.698824 s**; median: **4.92 s**. It is a *sequence-level* statistic, **not** the full film's average shot length.

## Reproducible data

- [Shot timings CSV](first-love-betrayal-filmfour-17-shots.csv): 17 complete shots, start/end timestamps and frame indices in the source recording.
- [Cinemetrics FACT .cmsx](first-love-betrayal-corrected.cmsx): corrected official-tool export; **not yet reflected in the public Cinemetrics record**.

The source is a privately held 2026-01-12 FilmFour off-air recording, 720×576 at 25 fps, including advertisements outside this excerpt. The source-recording window is **2150.44–2298.32 s**. It is not the release print's time base. These boundaries were obtained with PySceneDetect 0.7.1 ContentDetector threshold 22 and checked against adjacent frames; threshold 18 introduced motion-related false positives. Shot scales were not classified. No video, subtitles, audio or film stills are redistributed.

### Verification

The CSV is contiguous, with 17 rows; the first start and last end delimit 147.88 seconds. The FACT export has 17 markers whose timestamps match the CSV end times minus 2150.44 seconds to within 0.005 seconds. The last marker is at 147.88 seconds. Both datasets were validated locally on 13 October 2026.

### Attribution

Li, Hanpu (2026). *First Love (2019): betrayal-sequence shot-length measurements* [research dataset]. Accompanying the [First Love verification materials](../../README.md). Cinemetrics public record: [submission link](https://cinemetrics.uchicago.edu/movie/0d9aff11-65ef-4c3e-90e7-99cbde4649ca) (correction pending).

This dataset documents one limited sample. It does not claim independent peer review, a full-film census, or curator approval of the correction.
