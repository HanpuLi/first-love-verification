from __future__ import annotations

import json
import math
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = ROOT / "outputs"


def load(name: str):
    return json.loads((OUTPUTS / name).read_text())


class ArchivedAuditOutputTests(unittest.TestCase):
    def test_pal_rate_audit_baseline(self):
        data = load("pal_rate_audit_2026-09-28.json")
        rows = {round(float(row["ratio"]), 8): row for row in data["rate_hypotheses"]}

        self.assertEqual(data["best_ratio"], 1.04166667)
        self.assertTrue(math.isclose(rows[1.0]["mean_ncc"], 0.5751781227, abs_tol=1e-9))
        self.assertTrue(math.isclose(rows[1.04166667]["mean_ncc"], 0.8169552705, abs_tol=1e-9))
        self.assertTrue(math.isclose(rows[0.96]["mean_ncc"], 0.5440051058, abs_tol=1e-9))
        self.assertEqual(rows[1.04166667]["count_gt_0_85"], 27)

        dense = data["dense_local_alignment"]
        self.assertEqual(len(dense["plateaus"]), 4)
        self.assertTrue(
            math.isclose(
                dense["positive_offset_step_sum_s"],
                88.405,
                abs_tol=1e-6,
            )
        )

    def test_subtitle_timebase_baseline(self):
        data = load("subtitle_timebase_betrayal_2026-09-28.json")
        self.assertEqual(data["fixed_rate"], 0.96)
        self.assertTrue(math.isclose(data["best_offset_s"], 357.0, abs_tol=1e-6))
        self.assertTrue(
            math.isclose(data["best_correlation"], 0.6732276789563851, abs_tol=1e-12)
        )
        self.assertTrue(
            math.isclose(
                data["predicted_recording_times_s"]["What's happening?"],
                2317.32,
                abs_tol=1e-6,
            )
        )

    def test_manual_timebase_check_baseline(self):
        data = load("manual_timebase_checks_2026-09-28.json")
        distributed = data["distributed_alignment"]
        self.assertEqual(distributed["best_offset_s"], 357.0)
        checks = distributed["manual_frame_checks"]
        self.assertEqual(checks[0]["recording_time_s"], 2317.3)
        self.assertIn("not yet visible", checks[0]["observation"])
        self.assertEqual(checks[1]["recording_time_s"], 2318.5)
        self.assertIn("visible", checks[1]["observation"])
        failed = data["historical_failed_single_point_anchor"]
        self.assertEqual(failed["inferred_offset_s"], 385.8)
        self.assertEqual(failed["corrected_distributed_offset_s"], 357.0)
        self.assertTrue(math.isclose(failed["offset_difference_s"], 28.8, abs_tol=1e-12))

    def test_face_detector_calibration_baseline(self):
        data = load("face_detector_calibration_2026-09-28.json")
        historical = data["historical_protocol"]
        fair = data["equal_five_sample_protocol"]

        self.assertEqual(historical["haar"]["segments_with_face"], 8)
        self.assertEqual(historical["yunet"]["segments_with_face"], 12)
        self.assertEqual(fair["haar"]["segments_with_face"], 9)
        self.assertEqual(fair["yunet"]["segments_with_face"], 12)

        haar_target = fair["haar"]["known_closeup_segment"]
        yunet_target = fair["yunet"]["known_closeup_segment"]
        self.assertEqual((haar_target["hits"], haar_target["samples"]), (0, 5))
        self.assertEqual((yunet_target["hits"], yunet_target["samples"]), (5, 5))
        self.assertTrue(
            math.isclose(
                yunet_target["median_largest_face_height_ratio"],
                0.4575691752963596,
                abs_tol=1e-12,
            )
        )

    def test_content_detector_calibration_baseline(self):
        data = load("content_detector_calibration_2026-09-28.json")

        broadcast = data["broadcast_against_copy_a_threshold_27_reference"]["thresholds"]
        self.assertEqual(
            {key: broadcast["27.0"][key] for key in ("matched", "missed", "extra")},
            {"matched": 30, "missed": 6, "extra": 0},
        )
        self.assertEqual(
            {key: broadcast["18.0"][key] for key in ("matched", "missed", "extra")},
            {"matched": 36, "missed": 0, "extra": 3},
        )

        copy_a = data["copy_a_against_broadcast_threshold_18_reference"]["thresholds"]
        self.assertEqual(
            {key: copy_a["27.0"][key] for key in ("matched", "missed", "extra")},
            {"matched": 36, "missed": 3, "extra": 0},
        )
        self.assertEqual(
            {key: copy_a["22.0"][key] for key in ("matched", "missed", "extra")},
            {"matched": 39, "missed": 0, "extra": 0},
        )

        sensitivity = {
            row["threshold"]: row
            for row in data["complete_broadcast_melee_sensitivity"]["results"]
        }
        self.assertEqual(sensitivity[18.0]["segments"], 130)
        self.assertEqual(sensitivity[22.0]["segments"], 96)
        self.assertTrue(
            math.isclose(
                sensitivity[22.0]["asl_rate_corrected_s"],
                7.1159,
                abs_tol=1e-4,
            )
        )

    def test_betrayal_audit_baseline(self):
        data = load("betrayal_shot_face_audit_2026-09-28.json")
        self.assertEqual(data["scene_detector_threshold"], 18.0)
        self.assertEqual(data["shot_segments"], 24)
        self.assertTrue(math.isclose(data["asl_s"], 6.4, abs_tol=1e-12))
        self.assertTrue(
            math.isclose(data["longest_segment_s"], 37.8, abs_tol=1e-9)
        )
        self.assertEqual(data["segments_with_detected_face"], 13)
        self.assertTrue(
            math.isclose(
                data["max_face_height_ratio"],
                0.5440290239122179,
                abs_tol=1e-12,
            )
        )


if __name__ == "__main__":
    unittest.main()
