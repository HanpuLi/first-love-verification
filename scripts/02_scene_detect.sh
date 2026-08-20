#!/usr/bin/env bash
# ffmpeg: brightness-normalised scene-change detection for dark sequences
#
# Supports the analysis reported in the essay appendix.
# Media inputs are NOT included in this repository (see README).

# scene-change detection (brightness-normalised for dark scenes)
ffmpeg -ss 6700 -to 6740 -i first_love_FilmFour_2026-01-12.mp4 \
  -vf "eq=brightness=0.12:contrast=1.3,select='gt(scene,0.12)',showinfo"
