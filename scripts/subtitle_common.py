"""Shared subtitle parsing and Monica surface-form classification helpers."""
from __future__ import annotations

import re
from pathlib import Path

MONICA = re.compile(r"\bMonica\b", re.I)


def parse_srt(path: str | Path) -> list[dict[str, object]]:
    raw = Path(path).read_text(encoding="utf-8-sig", errors="replace")
    blocks = re.split(r"\r?\n\r?\n", raw.strip())
    entries: list[dict[str, object]] = []
    for block in blocks:
        lines = [line.strip().rstrip("\r") for line in block.strip().splitlines()]
        timestamp = next(
            (line for line in lines if re.match(r"^\d{2}:\d{2}:\d{2}", line)),
            None,
        )
        text = [
            line
            for line in lines
            if line
            and not re.match(r"^\d+$", line)
            and not re.match(r"^\d{2}:\d{2}:\d{2}", line)
        ]
        if not timestamp or not text:
            continue
        hours, minutes, rest = timestamp.split("-->")[0].strip().split(":")
        seconds = int(hours) * 3600 + int(minutes) * 60 + float(rest.replace(",", "."))
        entries.append(
            {
                "time": timestamp.split("-->")[0].strip(),
                "sec": seconds,
                "text": " ".join(text),
            }
        )
    return entries


def classify_monica(entry: dict[str, object]) -> str:
    text = str(entry["text"])
    if text.isupper():
        return "ON_SCREEN_TEXT"
    if re.search(r",\s*Monica[!?.]*$", text, re.I):
        return "VOCATIVE"
    if text.strip().lower().startswith("monica"):
        return "SUBJECT_OR_ADDRESS"
    return "THIRD_PERSON_OBJECT"
