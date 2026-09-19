"""
monica_subtitle_analysis.py
Run: python3 monica_subtitle_analysis.py
Inputs:  first_love_en.srt, first_love_ja.srt (same directory)
Outputs: printed report
"""

from subtitle_common import MONICA, classify_monica, parse_srt

en = parse_srt("first_love_en.srt")
ja = parse_srt("first_love_ja.srt")
print(f'EN entries: {len(en)}  duration: {float(en[-1]["sec"])/60:.1f} min')
print(f"JA entries: {len(ja)}")

# --- Monica reference classification ---
all_monica = [entry for entry in en if MONICA.search(str(entry["text"]))]
for entry in all_monica:
    entry["monica_cat"] = classify_monica(entry)

for cat in ["THIRD_PERSON_OBJECT", "VOCATIVE", "ON_SCREEN_TEXT", "SUBJECT_OR_ADDRESS"]:
    grp = [entry for entry in all_monica if entry["monica_cat"] == cat]
    print(f"\n--- {cat} (N={len(grp)}) ---")
    for entry in grp:
        print(f'  [{entry["time"]}]  {entry["text"]}')

# --- Scene windows (data-derived) ---
MARGIN = 180
all_secs = sorted(float(entry["sec"]) for entry in all_monica)
clusters = []
for sec in all_secs:
    if clusters and sec - clusters[-1][1] <= MARGIN:
        clusters[-1][1] = int(max(clusters[-1][1], sec + MARGIN))
    else:
        clusters.append([int(max(0, sec - MARGIN)), int(sec + MARGIN)])

print(f"\n--- {len(clusters)} scene windows (+/-{MARGIN}s margin) ---")
for i, (ws, we) in enumerate(clusters, 1):
    n = sum(1 for entry in en if ws <= float(entry["sec"]) <= we)
    print(f"  W{i}  {ws//60:02d}:{ws%60:02d}-{we//60:02d}:{we%60:02d}  {n} entries")

total = sum(
    1
    for ws, we in clusters
    for entry in en
    if ws <= float(entry["sec"]) <= we
)
print(f"Total entries across windows: {total}")

# --- W1 hallucination scene (window 1) ---
ws, we = clusters[0]
print(f"\n--- W1 dialogue ({ws//60:02d}:{ws%60:02d}-{we//60:02d}:{we%60:02d}) ---")
for entry in en:
    if ws <= float(entry["sec"]) <= we:
        print(f'  [{entry["time"]}]  {entry["text"]}')

# --- JA/EN alignment ---
en_by_sec = {}
for entry in en:
    en_by_sec.setdefault(round(float(entry["sec"])), []).append(entry)

print("\n--- JA/EN alignment (all JA entries, +/-3s) ---")
for je in ja:
    matches = []
    for delta in range(-3, 4):
        matches.extend(en_by_sec.get(round(float(je["sec"])) + delta, []))
    en_txt = " | ".join(str(match["text"]) for match in matches[:2]) or "[no match]"
    print(f'  JA [{je["time"]}]  {je["text"]}')
    print(f"  EN  {en_txt}")
