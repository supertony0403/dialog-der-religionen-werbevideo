# Dialog der Religionen – Werbevideo

Ein 40-sekündiger Spot für den Discord-Server **Dialog der Religionen**
(<https://discord.gg/dialog-der-religionen>), komplett aus Code erzeugt:
Bild über numpy/Pillow, Musik über additive Synthese, Zusammenbau mit ffmpeg.
Es sind keine fremden Video-, Bild- oder Musikdateien beteiligt, nur die drei
Schriften unter SIL Open Font License (Cinzel, EB Garamond, Inter).

## Ergebnis

| Datei | Format | Verwendung |
|---|---|---|
| `out/DDR_Werbevideo_16x9.mp4` | 1920×1080, 30 fps | Discord, YouTube, Website |
| `out/DDR_Werbevideo_9x16.mp4` | 1080×1920, 30 fps | Stories, Reels, TikTok |
| `out/DDR_Poster_16x9.png` | Standbild | Server-Banner, Vorschaubild |
| `out/DDR_Poster_9x16.png` | Standbild | Story-Grafik |

## Aufbau des Spots

| Zeit | Szene | Inhalt |
|---|---|---|
| 0:00–0:05 | Die Frage | ein Lichtpunkt, „Woran glaubst du?“ |
| 0:05–0:13 | Der Fragensturm | acht echte Streitfragen erscheinen und verklingen |
| 0:13–0:21 | Der Kreis | sieben Zeichen ordnen sich, ein Netz aus Gesprächen entsteht |
| 0:21–0:29 | Die Haltung | „Hier wird gestritten. Nicht gehetzt.“ plus vier Fakten |
| 0:29–0:35 | Das Emblem | zwei sich durchdringende Kreise, der Servername |
| 0:35–0:40 | Die Einladung | `discord.gg/dialog-der-religionen` |

Die sieben Zeichen sind Christentum, Islam, Judentum, Buddhismus, Hinduismus,
Taoismus – und ein Fragezeichen für alle, die suchen, zweifeln oder nichts
glauben. Alle sind als gleich feine Linien gezeichnet: keines wirkt größer
oder wichtiger als ein anderes.

## Bauen

```bash
./build.sh                  # alles: Ton, beide Formate, Poster
WORKERS=6 ./build.sh        # auf schwächeren Maschinen
```

Einzelschritte:

```bash
python3 src/audio.py --out work/soundtrack.wav
python3 src/render.py --format 16x9 --out work/video_16x9.mp4 --workers 10
python3 src/render.py --stills 2.2,14,26,33 --scale 0.5   # Prüfbilder
```

Voraussetzungen: Python ≥ 3.12 mit `numpy` und `Pillow`, dazu `ffmpeg`.

## Code

| Datei | Aufgabe |
|---|---|
| `src/core.py` | Render-Kern: Lichtmasken, Glow, Hintergrund, Tonwertkurve, Schriften |
| `src/symbols.py` | die sieben Zeichen als Linienzeichnung |
| `src/scenes.py` | Storyboard, Timing, Layout für Quer- und Hochformat |
| `src/render.py` | Frames rendern (parallel) und an ffmpeg streamen |
| `src/audio.py` | Soundtrack: Orgelpunkt, Pad-Akkorde, Puls, Glocken, Hall |

Gerendert wird additiv: Formen und Text landen in Graustufenmasken, die als
farbiges Licht auf den dunklen Grund addiert werden. Der Glow entsteht in
einem gemeinsamen Buffer bei einem Sechstel der Auflösung – das hält das
Rendern schnell und den Look über alle Elemente hinweg einheitlich.

## Texte ändern

Alle Formulierungen stehen in `src/scenes.py`: `QUESTIONS` (Fragensturm),
`FEATURES` (die vier Zeilen über den Server) und die Claims in den Funktionen
`scene_four` bis `scene_six`. Zeiten stehen als `T1`–`TEND` am Dateikopf und
sind auf die Taktgrenzen der Musik (90 BPM) gelegt – wer sie verschiebt,
sollte `CHORDS` in `src/audio.py` mitziehen.
