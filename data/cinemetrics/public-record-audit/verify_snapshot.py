#!/usr/bin/env python3
"""Offline audit of two archived PUBLIC Cinemetrics server-rendered shot lists.

By design this does not verify the optical correctness of individual cuts:
the historical HTML was saved by the contributor, and all annotations derive
from the same contributor's source-frame review. The public repository does
not contain the audiovisual recording or complete HTML responses.
"""
from __future__ import annotations

import argparse
import csv
from decimal import Decimal as D, ROUND_HALF_UP
from hashlib import sha256
import json
from pathlib import Path
import re
from statistics import median
from typing import Any

HERE = Path(__file__).resolve().parent
DATA_ROOT = HERE.parent
BEFORE = HERE / "capture_before_curator_amendment_2026-10-13.json"
AFTER = HERE / "capture_after_curator_amendment_2026-10-13.json"
CROSSWALK = HERE / "before_after_shot_boundary_crosswalk.csv"
REFERENCE = DATA_ROOT / "first-love-betrayal-filmfour-17-shots.csv"

def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)

def d(value: Any) -> D:
    n = D(str(value))
    require(n.is_finite(), "nonfinite number")
    return n

def one_decimal(value: D) -> D:
    return value.quantize(D("0.1"), rounding=ROUND_HALF_UP)

def read_snapshot(path: Path, count: int, no_s: str, length: str, asl: str, msl: str) -> dict:
    obj = json.loads(path.read_text(encoding="utf-8"))
    require(obj["schema"] == "cinemetrics-public-shot-snapshot-v1", "schema mismatch")
    shots = obj["raw_shots_from_server_payload"]
    require(len(shots) == count, "shot count changed")
    require([s["number"] for s in shots] == list(range(1, count + 1)), "shot order changed")
    require(all(s.get("type") == "" for s in shots), "shot-scale labels appeared")
    require(obj["summary_as_published"]["NoS"] == no_s, "published NoS mismatch")
    require(obj["summary_as_published"]["LEN"] == length, "published length mismatch")
    require(obj["summary_as_published"]["ASL"] == asl, "published ASL mismatch")
    require(obj["summary_as_published"]["MSL"] == msl, "published MSL mismatch")
    require(obj["summary_as_published"]["submitted_by"] == "Hanpu Li", "attribution mismatch")
    require(obj["public_url"].startswith("https://cinemetrics.uchicago.edu/movie/"), "provenance URL mismatch")
    require(re.fullmatch(r"[0-9a-f]{64}", obj["raw_http_response_html_sha256"]) is not None, "raw HTML fingerprint invalid")
    shot_hash = sha256(json.dumps(shots, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
    require(shot_hash == obj["shot_array_sha256"], "shot payload fingerprint mismatch")
    for item in shots:
        require(d(item["shotLength"]) > 0, "nonpositive shot duration")
        require(d(item["timestamp"]) >= 0, "negative shot timestamp")
    total = sum((d(s["shotLength"]) for s in shots), D(0))
    require(one_decimal(total) == d(length.split(":")[0])*60 + d(length.split(":")[1]), "total/length mismatch")
    require(one_decimal(total / count) == d(asl), "ASL mismatch")
    require(one_decimal(median(d(x["shotLength"]) for x in shots)) == d(msl), "MSL mismatch")
    require(d(shots[0]["timestamp"]) == 0, "first shot does not begin at zero")
    for prev, next_item in zip(shots, shots[1:]):
        require(d(prev["timestamp"]) + d(prev["shotLength"]) == d(next_item["timestamp"]),
                f"public intervals discontinuous: {prev['number']}->{next_item['number']}")
    return obj

def verify(
    before: Path = BEFORE,
    after: Path = AFTER,
    crosswalk: Path = CROSSWALK,
    reference: Path = REFERENCE,
    check_manifest: bool = True,
) -> dict:
    if check_manifest:
        manifest = (HERE / "SHA256SUMS").read_text(encoding="utf-8").splitlines()
        tracked = {line.split("  ", 1)[1]: line.split("  ", 1)[0] for line in manifest if "  " in line}
        names = {BEFORE.name, AFTER.name, CROSSWALK.name}
        require(set(tracked) == names, "snapshot manifest missing or extra entries")
        for filename, expected in tracked.items():
            got = sha256((HERE / filename).read_bytes()).hexdigest()
            require(got == expected, f"snapshot SHA-256 mismatch: {filename}")
    first = read_snapshot(before, 18, "18", "02:30.9", "8.4", "4.7")
    second = read_snapshot(after, 17, "17", "02:27.9", "8.7", "5.0")
    initial = first["raw_shots_from_server_payload"]
    current = second["raw_shots_from_server_payload"]
    require(d(initial[0]["shotLength"]) == D("3.0"), "displayed initial partial interval changed")
    with reference.open(newline="", encoding="utf-8") as f:
        ref = list(csv.DictReader(f))
    require(len(ref) == 17, "reference row count changed")
    with crosswalk.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    require(len(rows) == 17, "crosswalk row count changed")
    source_origin = D("2150.44")
    adjustments = []
    for i, (original, revised, local, row) in enumerate(zip(initial[1:], current, ref, rows), 1):
        reorigin = d(original["timestamp"]) - d(initial[0]["shotLength"])
        public = d(revised["timestamp"])
        actual = d(local["source_recording_start_s"]) - source_origin
        require(d(row["complete_shot"]) == i, f"crosswalk row {i} not aligned")
        require(d(row["historical_record_row"]) == i + 1, "original row alignment changed")
        require(d(row["historical_rebased_start_s"]) == reorigin, f"historical timestamp changed in row {i}")
        require(d(row["post_amendment_start_s"]) == public, f"public timestamp changed in row {i}")
        require(d(row["frame_indexed_reference_start_s"]) == actual, f"source reference changed in row {i}")
        require(d(row["amendment_difference_s"]) == public - reorigin, f"amendment difference changed in row {i}")
        require(d(row["public_minus_reference_s"]) == public - actual, f"reference difference changed in row {i}")
        require(d(row["reference_duration_s"]) == d(local["duration_s"]), "reference duration changed")
        require(d(row["post_amendment_display_duration_s"]) == d(revised["shotLength"]), "website duration changed")
        require(d(row["duration_difference_s"]) == d(revised["shotLength"]) - d(local["duration_s"]), "duration delta changed")
        source_frame = int(local["frame_start_at_25fps"])
        require(source_frame == int(row["source_frame_start"]), "frame index changed")
        require(d(source_frame) / D(25) == d(local["source_recording_start_s"]),
                "reference position not on 25fps frame")
        if public != reorigin:
            adjustments.append((i, public-reorigin))
        if i != 10:
            require(abs(public-actual) <= D("0.05"),
                    f"unexplained extra public-reference discrepancy: shot {i}")
    require(adjustments == [(10, D("0.30"))], "expected exactly one edited public boundary at shot 10")
    require(d(rows[9]["frame_indexed_reference_start_s"]) == D("87.72"), "source cut shifted")
    require(d(rows[9]["post_amendment_start_s"]) == D("88.00"), "public cut shifted")
    require(d(rows[9]["public_minus_reference_s"]) == D("0.28"), "7-frame discrepancy changed")
    require(d(rows[8]["reference_duration_s"]) == D("1.76"), "reference shot 9 changed")
    require(d(rows[9]["reference_duration_s"]) == D("8.56"), "reference shot 10 changed")
    require(d(current[8]["shotLength"]) == D("2.0"), "published shot 9 length changed")
    require(d(current[9]["shotLength"]) == D("8.3"), "published shot 10 length changed")
    return {
        "status": "offline_archival_crosswalk_validated",
        "historical_count": len(initial),
        "amended_count": len(current),
        "aligned_complete_shots": len(ref),
        "historical_displayed_initial_fragment_s": str(d(initial[0]["shotLength"])),
        "historical_rebased_cut_s": str(d(rows[9]["historical_rebased_start_s"])),
        "after_cut_s": str(d(rows[9]["post_amendment_start_s"])),
        "independent_reference_cut_s": str(d(rows[9]["frame_indexed_reference_start_s"])),
        "change_during_amendment_s": str(adjustments[0][1]),
        "after_vs_source_s": str(d(rows[9]["public_minus_reference_s"])),
        "other_16_cut_changes": 0,
        "proof_scope": "These are archived public HTML shot arrays plus one contributor's saved reference, not independent annotation or a verified record of database internals.",
    }

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--before-html", type=Path, help="optional original local HTML for SHA + raw shot-array verification")
    p.add_argument("--after-html", type=Path, help="optional corrected local HTML for SHA + raw shot-array verification")
    args = p.parse_args()
    for label, path, snap in (
        ("before", args.before_html, BEFORE),
        ("after", args.after_html, AFTER)
    ):
        if path is None:
            continue
        from html.parser import HTMLParser
        raw = path.read_bytes()
        obj = json.loads(snap.read_text())
        require(sha256(raw).hexdigest() == obj["raw_http_response_html_sha256"],
                f"{label} original HTML fingerprint mismatch")
        # The snapshots can be checked against a retained HTML file without
        # sharing copyrighted video frames or requiring live site access.
        source_text = raw.decode(errors="replace").replace('\\"', '"')
        candidates = []
        for match in re.finditer('"shots":', source_text):
            try:
                array, _ = json.JSONDecoder().raw_decode(source_text[match.end():])
            except ValueError:
                continue
            if isinstance(array, list) and len(array) == len(obj["raw_shots_from_server_payload"]):
                if array and isinstance(array[0], dict) and "shotLength" in array[0]:
                    candidates.append(array)
        require(len(candidates) == 1 and candidates[0] == obj["raw_shots_from_server_payload"],
                f"{label} saved HTML payload mismatch")
    print(json.dumps(verify(), indent=2))

if __name__ == "__main__":
    main()
