# Changelog

## [Unreleased]

- Defines A.9 as windowed shot-segment analysis, matching the archived 62 / 7.129 s
  melee result and 10 / 2.604 s animation result.
- Recovers the 2026-08-26 post-essay verification experiments into reproducible scripts
  and archives fresh 2026-09-28 reruns for the relative playback rate, local subtitle
  timebase, PySceneDetect threshold sensitivity, Haar/YuNet calibration, and betrayal
  face-height analysis.
- Records the 25/24 relative-rate evidence (mean NCC 0.817 versus 0.575 unscaled and
  0.544 in the opposite direction) and the 88.4 s local cross-copy offset increase.
- Separates historical unequal-sampling Haar/YuNet figures (8/14 versus 12/14) from an
  equal five-sample rerun (9/14 versus 12/14), and preserves the known-close-up
  Haar 0/5 versus YuNet 5/5 result.
- Documents detector-threshold sensitivity rather than presenting the complete-copy
  7.12 s ASL result as detector-independent ground truth.
- Pins the external YuNet model by SHA-256 and keeps the model outside the repository.
- Adds media-free tests that lock the archived audit outputs against silent drift.

## [2026.09.19] - 2026-09-19

First citable reproducibility snapshot.

- Records the three incompatible time bases used by the essay verification work.
- Preserves archived numerical outputs without redistributing the film, subtitle tracks or extracted frames.
- Adds a shared SRT parser/classifier with media-free regression tests.
- Documents the known analysis-environment boundary and deliberately compatibility-bands scientific dependencies.
- Adds CI, CodeQL, gitleaks, branch protection, citation metadata and an explicit code/repository licensing boundary.
