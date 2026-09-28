#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
tracked = subprocess.check_output(["git", "ls-files"], text=True).splitlines()
errors: list[str] = []

media_ext = {".mp4", ".mkv", ".avi", ".srt", ".vtt", ".wav", ".mp3"}
external_inputs = {"face_detection_yunet_2023mar.onnx"}
for rel in tracked:
    if Path(rel).suffix.lower() in media_ext:
        errors.append(f"third-party media/subtitle file must not be tracked: {rel}")
    if rel in external_inputs:
        errors.append(f"external analysis input must not be tracked: {rel}")

required = [
    "scripts/01_stream_inspect.sh",
    "scripts/02_scene_detect.sh",
    "scripts/03_extract_frames.sh",
    "scripts/04_audio_alignment.py",
    "scripts/05_shot_length.py",
    "scripts/06_face_scale_audit.py",
    "scripts/07_subtitle_parse.py",
    "scripts/08_monica_classify.py",
    "scripts/09_monica_subtitle_analysis.py",
    "scripts/10_shot_scale_betrayal.py",
    "scripts/11_subtitle_timebase.py",
    "scripts/subtitle_common.py",
    "tests/test_subtitle_logic.py",
    "REPRODUCIBILITY.md",
    "CITATION.cff",
    "LICENSE",
    "LICENSING.md",
    "CHANGELOG.md",
    "VERSION",
    "outputs/a9_shots.json",
]
for rel in required:
    if not (ROOT / rel).is_file():
        errors.append(f"missing verification artifact: {rel}")

try:
    a9 = json.loads((ROOT / "outputs/a9_shots.json").read_text())
except Exception as exc:
    errors.append(f"outputs/a9_shots.json is invalid: {exc}")
else:
    expected = {
        "melee_main": (62, 7.129032258064517, 442.0),
        "anim_main": (10, 2.6041667, 26.041667),
    }
    for key, (expected_n, expected_asl, expected_total) in expected.items():
        record = a9.get(key)
        if not isinstance(record, dict):
            errors.append(f"outputs/a9_shots.json missing record: {key}")
            continue
        durations = record.get("durs")
        if record.get("n") != expected_n:
            errors.append(
                f"{key} shot-segment count changed: "
                f"{record.get('n')!r} != {expected_n}"
            )
        if not math.isclose(
            float(record.get("asl", math.nan)),
            expected_asl,
            rel_tol=0,
            abs_tol=1e-9,
        ):
            errors.append(f"{key} ASL changed from archived baseline")
        if not isinstance(durations, list) or not math.isclose(
            sum(durations), expected_total, rel_tol=0, abs_tol=1e-6
        ):
            errors.append(f"{key} covered duration changed from archived baseline")

readme = (ROOT / "README.md").read_text()
for marker in (
    "No media is redistributed",
    "Time bases",
    "Limitations, stated once",
    "v2026.09.19",
    "LICENSING.md",
):
    if marker not in readme:
        errors.append(f"README lost required methodological boundary: {marker}")

version = (ROOT / "VERSION").read_text().strip() if (ROOT / "VERSION").exists() else None
citation = (ROOT / "CITATION.cff").read_text() if (ROOT / "CITATION.cff").exists() else ""
if version != "2026.09.19":
    errors.append(f"unexpected release snapshot version: {version!r}")
if (
    f'version: "{version}"' not in citation
    or 'date-released: "2026-09-19"' not in citation
):
    errors.append("CITATION.cff release metadata does not match VERSION/release date")

if errors:
    raise SystemExit("\n".join(errors))
print(
    f"repository check: {len(tracked)} tracked files; "
    "no prohibited media; required verification artifacts present"
)
