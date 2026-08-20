"""
monica_subtitle_analysis.py
Run: python3 monica_subtitle_analysis.py
Inputs:  first_love_en.srt, first_love_ja.srt (same directory)
Outputs: printed report
"""
import re
from pathlib import Path

def parse_srt(path):
    with open(path, encoding='utf-8-sig', errors='replace') as f:
        raw = f.read()
    blocks = re.split(r'\r?\n\r?\n', raw.strip())
    entries = []
    for block in blocks:
        lines = [l.strip().rstrip('\r') for l in block.strip().splitlines()]
        ts = next((l for l in lines
                   if re.match(r'^\d{2}:\d{2}:\d{2}', l)), None)
        txt = [l for l in lines if l
               and not re.match(r'^\d+$', l)
               and not re.match(r'^\d{2}:\d{2}:\d{2}', l)]
        if ts and txt:
            h, m, rest = ts.split('-->')[0].strip().split(':')
            sec = int(h)*3600 + int(m)*60 + float(rest.replace(',', '.'))
            entries.append(dict(time=ts.split('-->')[0].strip(),
                                sec=sec, text=' '.join(txt)))
    return entries

en = parse_srt('first_love_en.srt')
ja = parse_srt('first_love_ja.srt')
print(f'EN entries: {len(en)}  duration: {en[-1]["sec"]/60:.1f} min')
print(f'JA entries: {len(ja)}')

# --- Monica reference classification ---
MONICA = re.compile(r'\bMonica\b', re.I)

def classify_monica(e):
    t = e['text']
    if t.isupper(): return 'ON_SCREEN_TEXT'
    if re.search(r',\s*Monica[!?.]*$', t, re.I): return 'VOCATIVE'
    if t.strip().lower().startswith('monica'): return 'SUBJECT_OR_ADDRESS'
    return 'THIRD_PERSON_OBJECT'

all_monica = [e for e in en if MONICA.search(e['text'])]
for e in all_monica:
    e['monica_cat'] = classify_monica(e)

for cat in ['THIRD_PERSON_OBJECT','VOCATIVE','ON_SCREEN_TEXT','SUBJECT_OR_ADDRESS']:
    grp = [e for e in all_monica if e['monica_cat'] == cat]
    print(f'\n--- {cat} (N={len(grp)}) ---')
    for e in grp:
        print(f'  [{e["time"]}]  {e["text"]}')

# --- Scene windows (data-derived) ---
MARGIN = 180
all_secs = sorted(e['sec'] for e in all_monica)
clusters = []
for s in all_secs:
    if clusters and s - clusters[-1][1] <= MARGIN:
        clusters[-1][1] = int(max(clusters[-1][1], s + MARGIN))
    else:
        clusters.append([int(max(0, s - MARGIN)), int(s + MARGIN)])

print(f'\n--- {len(clusters)} scene windows (+/-{MARGIN}s margin) ---')
for i, (ws, we) in enumerate(clusters, 1):
    n = sum(1 for e in en if ws <= e['sec'] <= we)
    print(f'  W{i}  {ws//60:02d}:{ws%60:02d}-{we//60:02d}:{we%60:02d}  {n} entries')

total = sum(1 for ws, we in clusters for e in en if ws <= e['sec'] <= we)
print(f'Total entries across windows: {total}')

# --- W1 hallucination scene (window 1) ---
ws, we = clusters[0]
print(f'\n--- W1 dialogue ({ws//60:02d}:{ws%60:02d}-{we//60:02d}:{we%60:02d}) ---')
for e in en:
    if ws <= e['sec'] <= we:
        print(f'  [{e["time"]}]  {e["text"]}')

# --- JA/EN alignment ---
en_by_sec = {}
for e in en:
    en_by_sec.setdefault(round(e['sec']), []).append(e)

print('\n--- JA/EN alignment (all JA entries, +/-3s) ---')
for je in ja:
    matches = []
    for d in range(-3, 4):
        matches.extend(en_by_sec.get(round(je['sec']) + d, []))
    en_txt = ' | '.join(m['text'] for m in matches[:2]) or '[no match]'
    print(f'  JA [{je["time"]}]  {je["text"]}')
    print(f'  EN  {en_txt}')
