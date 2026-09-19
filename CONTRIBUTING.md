# Contributing

This repository is a verification companion to an academic essay. Contributions should improve reproducibility, error detection or methodological clarity without redistributing third-party film, subtitle or audio material.

Before opening a pull request:

```sh
python3 -m compileall -q scripts outputs tools
for f in scripts/*.sh; do bash -n "$f"; done
python3 tools/check_repository.py
```

A full environment check also installs `requirements.txt` and imports the analysis libraries; CI performs that check on every pull request.

Do not commit film copies, subtitle files, extracted frames, audio segments or other copyrighted source media. Synthetic fixtures are preferred for future automated tests.
