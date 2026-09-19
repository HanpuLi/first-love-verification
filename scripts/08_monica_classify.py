"""
Surface-form classifier for the 25 Monica references

Supports the analysis reported in the essay appendix.
Media inputs are NOT included in this repository (see README).
"""

from collections import Counter

from subtitle_common import MONICA, classify_monica, parse_srt

en = parse_srt("first_love_en.srt")
all_monica = [entry for entry in en if MONICA.search(str(entry["text"]))]
for entry in all_monica:
    entry["monica_cat"] = classify_monica(entry)

counts = Counter(str(entry["monica_cat"]) for entry in all_monica)
for category in [
    "THIRD_PERSON_OBJECT",
    "VOCATIVE",
    "ON_SCREEN_TEXT",
    "SUBJECT_OR_ADDRESS",
]:
    print(f"{category}: {counts[category]}")

# Archived result:
# THIRD_PERSON_OBJECT : 16  (object/topic/addressee of another speaker:
#                            13 strictly third-person, 2 identification
#                            lines, 1 direct question to her)
# VOCATIVE            :  1  (addressed by name; speaker not Monica)
# ON_SCREEN_TEXT      :  1  (visual insert)
# SUBJECT_OR_ADDRESS  :  7  (requires contextual inference)
# => object/topic/addressee rather than speaker: 16 + 1 = 17 entries
