"""
Surface-form classifier for the 25 Monica references

Supports the analysis reported in the essay appendix.
Media inputs are NOT included in this repository (see README).
"""

MONICA = re.compile(r'\bMonica\b', re.I)

def classify_monica(e):
    t = e['text']
    if t.isupper():
        return 'ON_SCREEN_TEXT'       # visual insert, not oral dialogue
    if re.search(r',\s*Monica[!?.]*$', t, re.I):
        return 'VOCATIVE'             # Monica addressed by name; speaker != Monica
    if t.strip().lower().startswith('monica'):
        return 'SUBJECT_OR_ADDRESS'   # requires contextual inference
    return 'THIRD_PERSON_OBJECT'      # Monica is grammatical object/topic;
                                      # speaker cannot be Monica

all_monica = [e for e in en if MONICA.search(e['text'])]
for e in all_monica:
    e['monica_cat'] = classify_monica(e)

# Results:
# THIRD_PERSON_OBJECT : 16  (object/topic/addressee of another speaker:
#                            13 strictly third-person, 2 identification
#                            lines, 1 direct question to her)
# VOCATIVE            :  1  (addressed by name; speaker not Monica)
# ON_SCREEN_TEXT      :  1  (visual insert)
# SUBJECT_OR_ADDRESS  :  7  (requires contextual inference)
# => object/topic/addressee rather than speaker: 16 + 1 = 17 entries
