#!/usr/bin/env bash
# Baut das komplette Werbepaket: Soundtrack, beide Videoformate, Discord-Fassungen, Poster.
set -euo pipefail
cd "$(dirname "$0")"

PY=${PY:-python3}
WORKERS=${WORKERS:-10}
mkdir -p out work
trap 'rm -f ffmpeg2pass-*.log ffmpeg2pass-*.log.mbtree' EXIT

echo "== Soundtrack =="
$PY src/audio.py --out work/soundtrack.wav

for FMT in 16x9 9x16; do
  echo "== Video $FMT =="
  $PY src/render.py --format "$FMT" --out "work/video_$FMT.mp4" --workers "$WORKERS" --crf 19
  ffmpeg -y -loglevel error -i "work/video_$FMT.mp4" -i work/soundtrack.wav \
    -c:v copy -c:a aac -b:a 192k -shortest "out/DDR_Werbevideo_$FMT.mp4"
  echo "   -> out/DDR_Werbevideo_$FMT.mp4 ($(du -h "out/DDR_Werbevideo_$FMT.mp4" | cut -f1))"

  # kleine Fassung fuer den direkten Upload auf Discord (Ziel < 10 MB)
  if [ "$FMT" = "16x9" ]; then SCALE="1280:720"; else SCALE="720:1280"; fi
  ffmpeg -y -loglevel error -i "work/video_$FMT.mp4" -vf "scale=$SCALE:flags=lanczos" \
    -c:v libx264 -preset slower -b:v 1650k -pass 1 -an -f null /dev/null
  ffmpeg -y -loglevel error -i "work/video_$FMT.mp4" -i work/soundtrack.wav \
    -vf "scale=$SCALE:flags=lanczos" -c:v libx264 -preset slower -b:v 1650k -pass 2 \
    -c:a aac -b:a 128k -shortest -movflags +faststart "out/DDR_Werbevideo_${FMT}_discord.mp4"
  echo "   -> out/DDR_Werbevideo_${FMT}_discord.mp4 ($(du -h "out/DDR_Werbevideo_${FMT}_discord.mp4" | cut -f1))"
done

echo "== Poster =="
$PY src/render.py --format 16x9 --stills 39.5 --stills-dir work/poster
cp work/poster/still_16x9_39.50.png out/DDR_Poster_16x9.png
$PY src/render.py --format 9x16 --stills 39.5 --stills-dir work/poster
cp work/poster/still_9x16_39.50.png out/DDR_Poster_9x16.png
$PY src/render.py --format 1x1 --stills 20.7 --stills-dir work/poster
cp work/poster/still_1x1_20.70.png out/DDR_Kreis_1x1.png

ls -lh out/
