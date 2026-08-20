#!/usr/bin/env bash
# ffprobe: container, frame rate and duration of each copy
#
# Supports the analysis reported in the essay appendix.
# Media inputs are NOT included in this repository (see README).

ffprobe -select_streams v:0 \
  -show_entries stream=width,height,r_frame_rate,nb_frames,duration \
  -show_entries format=duration \
  first_love_FilmFour_2026-01-12.mp4
# -> width=720 height=576 r_frame_rate=25/1 duration=8091.16
