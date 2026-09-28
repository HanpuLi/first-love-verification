#!/usr/bin/env python3
"""Audit the relative playback rate of the two off-air copies.

This reproduces the 2026-08-26 audio-envelope experiment which compared three
rate hypotheses before any local timebase offsets were interpreted:

    1.00000000   no rate correction
    1.04166667   stretch the FilmFour envelope by 25/24
    0.96000000   stretch in the opposite direction

Audio is extracted temporarily with ffmpeg as 8 kHz mono signed 16-bit PCM.
No source media or extracted audio is written to the repository.

The same run also performs a dense local alignment over the 92.9-minute copy
around 1580-1720 s.  The dense result is useful for measuring rate-corrected
offset steps in the abridged copy; it is not a release-track time conversion.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import scipy
from scipy.ndimage import uniform_filter1d
from scipy.signal import correlate

SAMPLE_RATE = 8000
HOP = 80
ENVELOPE_FPS = SAMPLE_RATE / HOP
RATES = (1.0, 1.04166667, 0.96)


def extract_audio(video: Path, raw_path: Path) -> None:
    if not video.is_file():
        raise FileNotFoundError(f"missing analysis input: {video}")
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg is required on PATH")
    subprocess.run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-i",
            str(video),
            "-vn",
            "-ac",
            "1",
            "-ar",
            str(SAMPLE_RATE),
            "-f",
            "s16le",
            "-y",
            str(raw_path),
        ],
        check=True,
    )


def envelope(raw_path: Path) -> np.ndarray:
    samples = np.fromfile(raw_path, dtype=np.int16).astype(np.float32) / 32768.0
    n = len(samples) // HOP * HOP
    frames = samples[:n].reshape(-1, HOP)
    rms = np.sqrt((frames * frames).mean(axis=1) + 1e-12)
    return np.log(rms + 1e-6)


def stretch(values: np.ndarray, ratio: float) -> np.ndarray:
    if ratio == 1.0:
        return values
    n = int(len(values) * ratio)
    positions = np.arange(n) / ratio
    return np.interp(positions, np.arange(len(values)), values)


def ncc_best(window: np.ndarray, reference: np.ndarray) -> tuple[int | None, float]:
    centred = window - window.mean()
    std = centred.std()
    if std < 1e-6:
        return None, 0.0
    centred = centred / std
    length = len(centred)
    if len(reference) < length + 2:
        return None, 0.0

    numerator = correlate(reference, centred, mode="valid", method="fft")
    mean = uniform_filter1d(reference, length, origin=-(length // 2))[: len(numerator)]
    mean_sq = uniform_filter1d(
        reference * reference, length, origin=-(length // 2)
    )[: len(numerator)]
    ref_std = np.sqrt(np.maximum(mean_sq - mean * mean, 1e-12))
    ncc = numerator / (length * ref_std)
    index = int(np.argmax(ncc))
    return index, float(ncc[index])


def rate_hypotheses(copy_a: np.ndarray, copy_b: np.ndarray) -> list[dict]:
    window_s = 20.0
    step_s = 120.0
    anchors = np.arange(60.0, len(copy_a) / ENVELOPE_FPS - window_s - 5, step_s)
    results = []

    for ratio in RATES:
        ref = stretch(copy_b, ratio)
        rows = []
        scores = []
        for t_a in anchors:
            window = copy_a[
                int(t_a * ENVELOPE_FPS) : int((t_a + window_s) * ENVELOPE_FPS)
            ]
            index, score = ncc_best(window, ref)
            if index is None:
                continue
            t_b_stretched = index / ENVELOPE_FPS
            rows.append(
                {
                    "copy_a_s": round(float(t_a), 6),
                    "copy_b_rate_corrected_s": round(float(t_b_stretched), 6),
                    "ncc": round(score, 9),
                }
            )
            scores.append(score)

        score_array = np.asarray(scores)
        results.append(
            {
                "ratio": ratio,
                "window_s": window_s,
                "step_s": step_s,
                "anchors": len(rows),
                "mean_ncc": float(score_array.mean()),
                "median_ncc": float(np.median(score_array)),
                "count_gt_0_70": int((score_array > 0.70).sum()),
                "count_gt_0_85": int((score_array > 0.85).sum()),
                "rows": rows,
            }
        )
    return results


def dense_local_steps(
    copy_a: np.ndarray, copy_b: np.ndarray, best_result: dict
) -> dict:
    ratio = float(best_result["ratio"])
    rate_corrected_b = stretch(copy_b, ratio)
    known = [row for row in best_result["rows"] if row["ncc"] > 0.80]
    if not known:
        raise RuntimeError("no high-confidence coarse anchors for dense alignment")

    known_a = np.asarray([row["copy_a_s"] for row in known])
    known_offset = np.asarray(
        [
            row["copy_b_rate_corrected_s"] - row["copy_a_s"]
            for row in known
        ]
    )

    window_s = 12.0
    step_s = 4.0
    search_s = 220.0
    rows = []
    for t_a in np.arange(20.0, len(copy_a) / ENVELOPE_FPS - window_s - 2, step_s):
        prior_offset = known_offset[np.argmin(np.abs(known_a - t_a))]
        lower = max(
            0, int((t_a + prior_offset - search_s) * ENVELOPE_FPS)
        )
        upper = min(
            len(rate_corrected_b),
            int((t_a + prior_offset + search_s + window_s) * ENVELOPE_FPS),
        )
        window = copy_a[
            int(t_a * ENVELOPE_FPS) : int((t_a + window_s) * ENVELOPE_FPS)
        ]
        index, score = ncc_best(window, rate_corrected_b[lower:upper])
        if index is None:
            continue
        t_b = (lower + index) / ENVELOPE_FPS
        rows.append(
            {
                "copy_a_s": float(t_a),
                "copy_b_rate_corrected_s": float(t_b),
                "rate_corrected_offset_s": float(t_b - t_a),
                "ncc": float(score),
            }
        )

    local = [
        row
        for row in rows
        if 1580.0 < row["copy_a_s"] < 1720.0 and row["ncc"] > 0.85
    ]
    if not local:
        raise RuntimeError("no high-confidence dense anchors in local audit window")

    plateaus: list[list[dict]] = []
    for row in local:
        if not plateaus:
            plateaus.append([row])
            continue
        current_median = float(
            np.median([x["rate_corrected_offset_s"] for x in plateaus[-1]])
        )
        if abs(row["rate_corrected_offset_s"] - current_median) <= 2.0:
            plateaus[-1].append(row)
        else:
            plateaus.append([row])

    plateau_summary = []
    for group in plateaus:
        plateau_summary.append(
            {
                "copy_a_start_s": group[0]["copy_a_s"],
                "copy_a_end_s": group[-1]["copy_a_s"],
                "median_rate_corrected_offset_s": float(
                    np.median([x["rate_corrected_offset_s"] for x in group])
                ),
                "median_ncc": float(np.median([x["ncc"] for x in group])),
                "anchors": len(group),
            }
        )

    steps = []
    for before, after in zip(plateau_summary, plateau_summary[1:]):
        delta = (
            after["median_rate_corrected_offset_s"]
            - before["median_rate_corrected_offset_s"]
        )
        steps.append(float(delta))

    return {
        "window_s": window_s,
        "step_s": step_s,
        "search_s": search_s,
        "selection": "1580 < copy_a_s < 1720 and ncc > 0.85",
        "plateaus": plateau_summary,
        "positive_offset_steps_s": [x for x in steps if x > 0],
        "positive_offset_step_sum_s": float(sum(x for x in steps if x > 0)),
        "rows": local,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--copy-a", type=Path, default=Path("first_love.mp4"))
    parser.add_argument(
        "--copy-b",
        type=Path,
        default=Path("first_love_FilmFour_2026-01-12.mp4"),
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    with tempfile.TemporaryDirectory(prefix="first-love-pal-") as tmp:
        tmp_path = Path(tmp)
        raw_a = tmp_path / "copy_a.raw"
        raw_b = tmp_path / "copy_b.raw"
        extract_audio(args.copy_a, raw_a)
        extract_audio(args.copy_b, raw_b)
        env_a = envelope(raw_a)
        env_b = envelope(raw_b)

        hypotheses = rate_hypotheses(env_a, env_b)
        best = max(hypotheses, key=lambda item: item["mean_ncc"])
        dense = dense_local_steps(env_a, env_b, best)

    ffmpeg_version = subprocess.run(
        ["ffmpeg", "-version"], check=True, capture_output=True, text=True
    ).stdout.splitlines()[0]

    result = {
        "analysis": "PAL/audio-envelope rate audit",
        "copy_a": args.copy_a.name,
        "copy_b": args.copy_b.name,
        "audio": {
            "sample_rate_hz": SAMPLE_RATE,
            "hop_samples": HOP,
            "envelope_rate_hz": ENVELOPE_FPS,
            "transform": "log RMS",
        },
        "rate_hypotheses": hypotheses,
        "best_ratio": best["ratio"],
        "dense_local_alignment": dense,
        "environment": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "ffmpeg": ffmpeg_version,
        },
    }

    print(
        "rate hypotheses: "
        + ", ".join(
            f"{item['ratio']:.6f} mean={item['mean_ncc']:.3f} "
            f"median={item['median_ncc']:.3f}"
            for item in hypotheses
        )
    )
    print(f"best ratio: {best['ratio']:.8f}")
    print(
        "local rate-corrected offset steps: "
        + " + ".join(
            f"{x:.1f}" for x in dense["positive_offset_steps_s"]
        )
        + f" = {dense['positive_offset_step_sum_s']:.1f} s"
    )

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(result, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"saved {args.output}")


if __name__ == "__main__":
    main()
