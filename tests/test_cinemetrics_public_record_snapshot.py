"""Offline tests for historic Cinemetrics public-shot snapshots."""
from __future__ import annotations

import copy
import csv
import json
import sys
from hashlib import sha256
from pathlib import Path
import tempfile
import unittest

DATA = Path(__file__).resolve().parents[1] / "data/cinemetrics"
SNAP = DATA / "public-record-audit"
sys.path.insert(0, str(SNAP))
import verify_snapshot as check


class PublicRecordSnapshotTests(unittest.TestCase):
    def test_original_and_amended_html_archives_are_aligned(self):
        report = check.verify()
        self.assertEqual(report["historical_count"], 18)
        self.assertEqual(report["amended_count"], 17)
        self.assertEqual(report["other_16_cut_changes"], 0)
        self.assertEqual(report["historical_rebased_cut_s"], "87.70")
        self.assertEqual(report["after_cut_s"], "88.00")
        self.assertEqual(report["independent_reference_cut_s"], "87.72")
        self.assertEqual(report["after_vs_source_s"], "0.28")

    def test_snapshot_embeds_provenance_of_original_http_html(self):
        for path in (check.BEFORE, check.AFTER):
            record = json.loads(path.read_text())
            self.assertEqual(record["summary_as_published"]["submitted_by"], "Hanpu Li")
            self.assertEqual(len(record["raw_http_response_html_sha256"]), 64)
            self.assertGreater(record["raw_http_response_bytes"], 100_000)
            self.assertEqual(
                record["shot_array_sha256"],
                sha256(json.dumps(record["raw_shots_from_server_payload"],
                                  separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
            )

    def test_rejects_a_tampered_snapshot(self):
        data = json.loads(check.AFTER.read_text())
        data["raw_shots_from_server_payload"][9]["timestamp"] = 87.7
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "after.json"
            f.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, "shot payload fingerprint mismatch"):
                check.read_snapshot(f, 17, "17", "02:27.9", "8.7", "5.0")

    def test_rejects_crosswalk_changed_without_data_change(self):
        with tempfile.TemporaryDirectory() as tmp:
            with check.CROSSWALK.open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            rows[9]["post_amendment_start_s"] = "87.70"
            f = Path(tmp) / "crosswalk.csv"
            with f.open("w", newline="") as h:
                writer = csv.DictWriter(h, fieldnames=list(rows[0].keys()))
                writer.writeheader()
                writer.writerows(rows)
            with self.assertRaisesRegex(ValueError, "public timestamp changed"):
                check.verify(crosswalk=f, check_manifest=False)

    def test_rejects_reference_frame_shifted_by_one(self):
        with tempfile.TemporaryDirectory() as tmp:
            with check.REFERENCE.open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            rows[9]["frame_start_at_25fps"] = "55955"
            f = Path(tmp) / "reference.csv"
            with f.open("w", newline="") as h:
                writer = csv.DictWriter(h, fieldnames=list(rows[0].keys()))
                writer.writeheader()
                writer.writerows(rows)
            with self.assertRaisesRegex(ValueError, "frame index changed"):
                check.verify(reference=f, check_manifest=False)


if __name__ == "__main__":
    unittest.main()
