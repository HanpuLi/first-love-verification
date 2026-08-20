"""
SRT parsing for both subtitle tracks

Supports the analysis reported in the essay appendix.
Media inputs are NOT included in this repository (see README).
"""

import re

def parse_srt(path):
    with open(path, 'r', encoding='utf-8-sig', errors='replace') as f:
        content = f.read()
    blocks = re.split(r'\n\n', content.strip())
    entries = []
    for block in blocks:
        lines = [l.strip().rstrip('\r') for l in block.strip().split('\n')]
        ts = next((l for l in lines
                   if re.match(r'^\d{2}:\d{2}:\d{2}', l)), None)
        txt = [l for l in lines
               if l
               and not re.match(r'^\d+$', l)
               and not re.match(r'^\d{2}:\d{2}:\d{2}', l)]
        if txt and ts:
            h, m, rest = ts.split('-->')[0].strip().split(':')
            sec = int(h)*3600 + int(m)*60 + float(rest.replace(',', '.'))
            entries.append({'time': ts.split('-->')[0].strip(),
                            'sec':  sec,
                            'text': ' '.join(txt)})
    return entries

en = parse_srt('first_love_en.srt')  # 1073 entries
ja = parse_srt('first_love_ja.srt')  #   39 entries
