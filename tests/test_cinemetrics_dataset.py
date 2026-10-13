"""Regression tests for the independently reusable public Cinemetrics data."""
from __future__ import annotations

import copy
import csv
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "cinemetrics"
sys.path.insert(0, str(DATA))
import verify_dataset as subject


class CinemetricsDatasetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with subject.CSV.open(newline="", encoding="utf-8") as handle:
            cls.rows = list(csv.DictReader(handle))
        cls.export = json.loads(subject.CMSX.read_text(encoding="utf-8"))

    def test_public_data_matches_reported_shot_statistics(self):
        result = subject.audit()
        self.assertEqual(result["shots"], 17)
        self.assertEqual(result["duration_s"], "147.88")
        self.assertEqual(result["median_shot_length_s"], "4.92")
        self.assertEqual(result["fact_markers"], 17)
        self.assertEqual(result["result"], "arithmetic_and_export_consistent")

    def test_rejects_discontinuous_interval(self):
        rows = copy.deepcopy(self.rows)
        rows[3]["source_recording_start_s"] = "2202.32"
        rows[3]["duration_s"] = "3.80"
        rows[3]["frame_start_at_25fps"] = "55058"
        with self.assertRaisesRegex(ValueError, "gap or overlap"):
            subject.verify(rows, self.export)

    def test_rejects_incorrect_frame_index(self):
        rows = copy.deepcopy(self.rows)
        rows[0]["frame_end_at_25fps"] = "54705"
        with self.assertRaisesRegex(ValueError, "frame indices"):
            subject.verify(rows, self.export)

    def test_rejects_non_frame_aligned_timestamp(self):
        rows = copy.deepcopy(self.rows)
        rows[1]["source_recording_end_s"] = "2191.77"
        rows[1]["duration_s"] = "3.53"
        with self.assertRaisesRegex(ValueError, "does not fall"):
            subject.verify(rows, self.export)

    def test_rejects_extra_or_missing_shots(self):
        with self.assertRaisesRegex(ValueError, "17 complete shots"):
            subject.verify(self.rows[:-1], self.export)

    def test_rejects_wrong_fact_marker(self):
        export = copy.deepcopy(self.export)
        export["shotMarkers"][6]["ts"] += 0.04
        with self.assertRaisesRegex(ValueError, "FACT marker 7"):
            subject.verify(self.rows, export)

    def test_rejects_accidental_shot_scale_coding(self):
        export = copy.deepcopy(self.export)
        export["shotMarkers"][5]["typeIdx"] = 1
        with self.assertRaisesRegex(ValueError, "shot-scale category"):
            subject.verify(self.rows, export)

    def test_rejects_legacy_marker_divergence(self):
        export = copy.deepcopy(self.export)
        export["markers"] = "1000" + export["markers"][3:]
        with self.assertRaisesRegex(ValueError, "legacy marker"):
            subject.verify(self.rows, export)

    def test_public_dataset_contains_no_media(self):
        forbidden = {".mp4", ".mkv", ".mov", ".jpg", ".jpeg",
                     ".png", ".srt", ".ass", ".wav", ".mp3"}
        self.assertFalse([p.name for p in DATA.iterdir() if p.suffix.lower() in forbidden])


if __name__ == "__main__":
    unittest.main()
