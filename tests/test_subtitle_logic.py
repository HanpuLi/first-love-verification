from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from subtitle_common import classify_monica, parse_srt  # noqa: E402


class SubtitleLogicTests(unittest.TestCase):
    def test_parse_srt_handles_bom_crlf_and_multiline_text(self) -> None:
        fixture = (
            "\ufeff1\r\n"
            "00:00:01,500 --> 00:00:03,000\r\n"
            "Hello,\r\n"
            "Monica!\r\n\r\n"
            "2\r\n"
            "00:01:02,250 --> 00:01:03,000\r\n"
            "MONICA\r\n"
        )
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "fixture.srt"
            path.write_text(fixture, encoding="utf-8")
            entries = parse_srt(path)

        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0]["text"], "Hello, Monica!")
        self.assertAlmostEqual(float(entries[0]["sec"]), 1.5)
        self.assertAlmostEqual(float(entries[1]["sec"]), 62.25)

    def test_monica_surface_categories_remain_stable(self) -> None:
        cases = {
            "MONICA OWES US": "ON_SCREEN_TEXT",
            "Come here, Monica!": "VOCATIVE",
            "Monica is here": "SUBJECT_OR_ADDRESS",
            "We saw Monica yesterday": "THIRD_PERSON_OBJECT",
        }
        for text, expected in cases.items():
            with self.subTest(text=text):
                self.assertEqual(classify_monica({"text": text}), expected)


if __name__ == "__main__":
    unittest.main()
