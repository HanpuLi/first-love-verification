# Cinemetrics public record: before-and-after snapshots (13 October 2026)

**Film:** *First Love* (*Hatsukoi*, 2019), Takashi Miike. **Contributor and auditor:** Hanpu Li.

**Canonical record:** https://cinemetrics.uchicago.edu/movie/0d9aff11-65ef-4c3e-90e7-99cbde4649ca

This directory preserves **two distinct public HTML responses actually saved on 13 October 2026**, one before the curator's amendment and one after it. The shot arrays were extracted from the server-rendered React payload. The complete HTML responses are retained privately. This public repository contains the observed public shot fields, headline statistics, HTML fingerprints and a crosswalk to the [25-fps reference CSV](../first-love-betrayal-filmfour-17-shots.csv). It contains no movie frames, audio, subtitles or private correspondence.

## Published states

| Saved public page | Local save time (UTC) | NoS | LEN | ASL | MSL |
|---|---|---:|---:|---:|---:|
| [Before amendment](capture_before_curator_amendment_2026-10-13.json) | 13 Oct 13:00:56.767 | 18 | 02:30.9 | 8.4 s | 4.7 s |
| [After amendment](capture_after_curator_amendment_2026-10-13.json) | 13 Oct 15:25:48.494 | 17 | 02:27.9 | 8.7 s | 5.0 s |

Times are **filesystem modification timestamps of the locally saved HTTP responses**, not timestamps certified by Cinemetrics. Each JSON document contains the original HTML response's byte count and SHA-256 checksum, the public shot-list array, and its own checksum. The public array includes the site's number, timestamp, shotLength, type, trendlineShotLength and movingAverage fields. The published shot timestamps use tenths of a second; the server's *internal storage precision* remains unknown.

The original 18-interval page displayed a **3.0-second initial fragment** (3.04 seconds in the contributor's original frame-level export). The amended page removed that interval. To align the pages at their *displayed* precision, subtract the original webpage's 3.0-second fragment from the starts of historical shots 2–18. This is not a frame-accurate time conversion.

The [crosswalk](before_after_shot_boundary_crosswalk.csv) aligns those starts with the amended page and the [source-frame reference](../first-love-betrayal-filmfour-17-shots.csv). Its result is specific:

- **16 of 17** rebased historical starts are identical to the amended page at the site's displayed precision.
- The exception is **start of complete shot 10**. It was historical shot 11 at 90.7 seconds; after subtracting the historical page's 3.0-second initial fragment, this is **87.7 seconds**. The amended page showed **88.0 seconds**, a **+0.3-second change between the two published states**.
- The frame-indexed reference places the cut at **87.72 seconds** within the complete-shot excerpt (source frame **55,954**, recording rate **25 fps**). The amended website's **88.0 seconds** differs from that reference by **+0.28 seconds**, equivalent to seven frame intervals.
- The amended lengths of shots 9 and 10 were **2.0 and 8.3 seconds**, versus reference lengths of **1.76 and 8.56 seconds**. The published headline remained **NoS 17 / LEN 2:27.9 / ASL 8.7**.

The historical HTML narrows the timing of the change to the *public-record amendment*. It does not identify whether a manual correction, an interface, data conversion or rendering caused it. These records and the original cut annotation were produced and checked by the same contributor. They are not an independent second-annotator verification or evidence of a database-wide error rate.

## Offline checks

Run from the repository root using Python 3's standard library:

    python3 data/cinemetrics/public-record-audit/verify_snapshot.py
    python3 -m unittest discover -s tests -p 'test_*.py' -v
    python3 data/cinemetrics/verify_dataset.py

The snapshot checker validates the stored public statistics, ordered shot arrays, fixture SHA-256 hashes, interval continuity, 17-row crosswalk, and the single changed boundary against the existing source-frame CSV. All checks can run offline, even if the curator subsequently changes the live website.

Someone with the **privately preserved** HTTP responses can also check the extracted arrays and source HTML checksums:

    python3 data/cinemetrics/public-record-audit/verify_snapshot.py \
        --before-html /path/to/saved-before.html \
        --after-html /path/to/saved-after.html

Without those raw responses, public consumers can verify the consistency of the released snapshot files, but cannot independently establish what the server returned at the stated times. The Git commit records when the snapshot files were published, not when the historical HTTP requests occurred.

**SHA256SUMS** records content-integrity digests of the three public data files. It is not a digital signature from Cinemetrics. The full HTML files and the source movie remain outside the repository.

## Attribution

Li, Hanpu (2026). *First Love (2019), Cinemetrics public-record amendment: before-and-after shot-length snapshots* [research dataset]. GitHub, HanpuLi/first-love-verification, data/cinemetrics/public-record-audit. Original public data: [Cinemetrics contribution](https://cinemetrics.uchicago.edu/movie/0d9aff11-65ef-4c3e-90e7-99cbde4649ca).

Attribute the public shot-list observations to Cinemetrics. The frame-indexed reference and crosswalk are the contributor's analysis. The present record does not establish film-edit validity without source frames or a population-level claim about the site.
