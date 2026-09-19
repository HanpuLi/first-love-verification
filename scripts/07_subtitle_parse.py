"""
SRT parsing for both subtitle tracks

Supports the analysis reported in the essay appendix.
Media inputs are NOT included in this repository (see README).
"""

from subtitle_common import parse_srt

en = parse_srt("first_love_en.srt")  # 1073 entries
ja = parse_srt("first_love_ja.srt")  #   39 entries
