#!/usr/bin/env bash
# ffmpeg: single-frame and interval frame extraction at exact timestamps
#
# Supports the analysis reported in the essay appendix.
# Media inputs are NOT included in this repository (see README).

# (i) Extract single frame at an exact timestamp
ffmpeg -ss 6708.0 -i first_love_FilmFour_2026-01-12.mp4 \
  -frames:v 1 fig_crash_typography.png

# (ii) Generate contact sheet across a window (here 2 fps), tiled 4x6
ffmpeg -ss 5944 -to 5992 -i first_love_FilmFour_2026-01-12.mp4 \
  -vf "fps=2,scale=480:-1,tile=4x6" climax_julie_contact.png

# (iii) Extract with brightness adjustment filter for low-key scenes
ffmpeg -ss 6376.0 -i first_love_FilmFour_2026-01-12.mp4 \
  -vf "eq=brightness=0.16:contrast=1.35" -frames:v 1 otomo_read.png

# (iv) Tile individual frames into multi-panel plates
montage a1_pre.png a2_crash.png a3_2d.png a4_resume.png \
  -tile 2x2 fig01_animation_transition.png
