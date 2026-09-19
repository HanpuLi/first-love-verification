#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
tracked = subprocess.check_output(["git", "ls-files"], text=True).splitlines()
errors: list[str] = []

media_ext = {".mp4", ".mkv", ".avi", ".srt", ".vtt", ".wav", ".mp3"}
for rel in tracked:
    if Path(rel).suffix.lower() in media_ext:
        errors.append(f"third-party media/subtitle file must not be tracked: {rel}")

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
    "outputs/a9_shots.json",
]
for rel in required:
    if not (ROOT / rel).is_file():
        errors.append(f"missing verification artifact: {rel}")

try:
    json.loads((ROOT / "outputs/a9_shots.json").read_text())
except Exception as exc:
    errors.append(f"outputs/a9_shots.json is invalid: {exc}")

readme = (ROOT / "README.md").read_text()
for marker in ("No media is redistributed", "Time bases", "Limitations, stated once"):
    if marker not in readme:
        errors.append(f"README lost required methodological boundary: {marker}")

if errors:
    raise SystemExit("\n".join(errors))
print(f"repository check: {len(tracked)} tracked files; no prohibited media; required verification artifacts present")
