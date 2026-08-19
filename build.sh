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
  if [ "$FMT" = "16x9" ]; then SCALE="1024:576"; else SCALE="576:1024"; fi
  ffmpeg -y -loglevel error -i "work/video_$FMT.mp4" -vf "scale=$SCALE:flags=lanczos" \
    -c:v libx264 -preset slower -b:v 940k -pass 1 -an -f null /dev/null
  ffmpeg -y -loglevel error -i "work/video_$FMT.mp4" -i work/soundtrack.wav \
    -vf "scale=$SCALE:flags=lanczos" -c:v libx264 -preset slower -b:v 940k -pass 2 \
    -c:a aac -b:a 96k -shortest -movflags +faststart "out/DDR_Werbevideo_${FMT}_discord.mp4"
  echo "   -> out/DDR_Werbevideo_${FMT}_discord.mp4 ($(du -h "out/DDR_Werbevideo_${FMT}_discord.mp4" | cut -f1))"
done

echo "== TikTok-Fassung =="
$PY src/audio_tiktok.py --out work/soundtrack_tiktok.wav
$PY src/render.py --edition tiktok --format 9x16 --out work/tiktok_9x16.mp4 \
  --workers "$WORKERS" --crf 19
ffmpeg -y -loglevel error -i work/tiktok_9x16.mp4 -i work/soundtrack_tiktok.wav \
  -c:v copy -c:a aac -b:a 192k -ar 48000 -shortest -movflags +faststart \
  out/DDR_TikTok.mp4
ffmpeg -y -loglevel error -i work/tiktok_9x16.mp4 -c:v copy -an \
  -movflags +faststart out/DDR_TikTok_stumm.mp4
$PY src/render.py --edition tiktok --format 9x16 --stills 3.4 --stills-dir work/cover
cp work/cover/still_9x16_03.40.png out/DDR_TikTok_Cover.png
echo "   -> out/DDR_TikTok.mp4 (+ stumme Fassung, + Cover)"

echo "== Poster =="
$PY src/render.py --format 16x9 --stills 71.0 --stills-dir work/poster
cp work/poster/still_16x9_71.00.png out/DDR_Poster_16x9.png
$PY src/render.py --format 9x16 --stills 71.0 --stills-dir work/poster
cp work/poster/still_9x16_71.00.png out/DDR_Poster_9x16.png
$PY src/render.py --format 1x1 --stills 54.5 --stills-dir work/poster
cp work/poster/still_1x1_54.50.png out/DDR_Kreis_1x1.png

ls -lh out/
