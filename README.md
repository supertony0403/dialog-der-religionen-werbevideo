# Dialog der Religionen – Trailer

Ein 72-sekündiger Trailer für den Discord-Server **Dialog der Religionen**
(<https://discord.gg/dialog-der-religionen>), komplett aus Code erzeugt:
Bild über numpy/Pillow, Musik über Synthese, Zusammenbau mit ffmpeg. Kein
Stock-Material, keine fremde Musik — nur drei Schriften unter SIL Open Font
License (Cinzel, EB Garamond, Inter).

## Ergebnis

| Datei | Format | Verwendung |
|---|---|---|
| `out/DDR_TikTok.mp4` | 1080×1920, 26 s | **TikTok / Reels / Shorts** – mit eigenem Beat |
| `out/DDR_TikTok_stumm.mp4` | 1080×1920, 26 s | dieselbe Fassung ohne Ton, für TikTok-Sounds aus der App |
| `out/DDR_TikTok_Cover.png` | Standbild | Cover fürs Profilraster |
| `out/DDR_Werbevideo_16x9.mp4` | 1920×1080, 30 fps | YouTube, Website, Discord mit Nitro |
| `out/DDR_Werbevideo_9x16.mp4` | 1080×1920, 30 fps | Stories, Reels, TikTok |
| `out/DDR_Werbevideo_16x9_discord.mp4` | 1024×576 | direkter Upload ohne Nitro (unter 10 MB) |
| `out/DDR_Werbevideo_9x16_discord.mp4` | 576×1024 | dito, hochkant |
| `out/DDR_Poster_*.png`, `out/DDR_Kreis_1x1.png` | Standbilder | Banner, Server-Icon, Vorschaubild |

## Die TikTok-Fassung (26 s)

Eigener Schnitt, nicht die gekürzte Langfassung: auf TikTok entscheiden die
ersten zwei Sekunden, deshalb steht der Haken am Anfang und nicht der Aufbau.

| Zeit | Teil | Inhalt |
|---|---|---|
| 0:00–0:04 | Haken | „Christen. Muslime. Atheisten." → **„Ein Chat."** → „Und keiner rastet aus." |
| 0:04–0:12 | Schlagabtausch | sechs Repliken als Chatverlauf, Pointe: „… gute Frage." |
| 0:12–0:16 | Fakten im Takt | 12 Weltanschauungen · 0 Bekehrungsdruck · 20 Uhr Voice · 24/7 |
| 0:16–0:18 | Zwölf Zeichen | die Symbole fliegen in den Kreis |
| 0:18–0:22 | Drop | Emblem und Name mit Aufschlag |
| 0:22–0:26 | Einladung | Link, „Komm rein. Stell deine Frage.", dann zurück zum Anfang (**Loop**) |

Alles Wichtige liegt zwischen TikToks Bedienelementen (oben Statusleiste, rechts
die Buttons, unten Caption und Menü). Der Schluss führt zurück zum ersten Bild,
damit die Wiederholung nahtlos wirkt.

**Musik:** Der Beat ist selbst synthetisiert – 120 BPM, Sub und Trommeln tragen
die Lautstärke, oberhalb von 12 kHz ist alles abgeschnitten. Gemessen: 30 % Bass,
24 % untere Mitten, 39 % Mitten, −13,6 dBFS RMS. Wer stattdessen einen
Trending-Sound aus der TikTok-App nutzen will, nimmt `DDR_TikTok_stumm.mp4` –
das ist auch der lizenzrechtlich saubere Weg für fremde Musik.

## Aufbau

| Zeit | Bewegung | Inhalt |
|---|---|---|
| 0:00–0:08 | Kaltstart | ein Lichtpunkt im Dunkeln, „Woran glaubst du?" |
| 0:08–0:19 | Fragensturm | acht Streitfragen schlagen im Takt ein, Sternenflug |
| 0:19–0:32 | Die Philosophen | Nietzsche, Dostojewski, Kant, Augustinus, Al-Ghazali, Camus |
| 0:32–0:45 | Die Debatte | acht Repliken als Chatverlauf, Gold gegen Blau |
| 0:45–0:56 | Zwölf Wege | zwölf Zeichen ordnen sich zum Kreis, Nachrichten wandern |
| 0:56–1:01 | Die Haltung | „Hier wird gestritten. Nicht gehetzt." |
| 1:01–1:07 | Emblem | Aufschlag, zwei sich durchdringende Kreise, der Name |
| 1:07–1:12 | Einladung | `discord.gg/dialog-der-religionen`, steht bis zum letzten Bild |

**Die zwölf Zeichen:** Christentum, Islam, Judentum, Buddhismus, Hinduismus,
Taoismus, Sikhismus, Bahai, Shinto, Zoroastrismus, Jainismus — und ein
Fragezeichen für alle, die suchen, zweifeln oder nichts glauben. Alle sind als
gleich feine Linien gezeichnet: keines wirkt größer oder wichtiger als ein
anderes. Das ist die Aussage des Films, in einer gestalterischen Entscheidung.

## Bauen

```bash
./build.sh                  # alles: Ton, beide Formate, Discord-Fassungen, Poster
WORKERS=6 ./build.sh        # auf schwächeren Maschinen
```

Einzelschritte:

```bash
python3 src/audio.py --out work/soundtrack.wav
python3 src/render.py --format 16x9 --out work/video_16x9.mp4 --workers 10
python3 src/render.py --stills 9.5,25,38,52,63 --scale 0.5   # Prüfbilder
```

Voraussetzungen: Python ≥ 3.12 mit `numpy` und `Pillow`, dazu `ffmpeg`.

## Code

| Datei | Aufgabe |
|---|---|
| `src/timing_tiktok.py` / `src/scenes_tiktok.py` / `src/audio_tiktok.py` | die TikTok-Fassung (26 s) |
| `src/timing.py` | **die Partitur** – Szenenzeiten, Texte, Schläge; Bild und Ton lesen dieselbe Datei |
| `src/core.py` | Render-Kern: Lichtmasken, gemeinsamer Glow-Buffer, Tonwertkurve, Schriften |
| `src/backdrops.py` | bewegte Ebenen: Sternenflug, Lichtschneisen, Glut, Nebel, Schockwellen, Kamera |
| `src/symbols.py` | die zwölf Zeichen als Linienzeichnung |
| `src/scenes.py` | Storyboard, Kamerafahrten, Layout für 16:9, 9:16 und 1:1 |
| `src/audio.py` | Trailer-Score: Chor, Taiko, Braams, Streicher, Riser, Hall |
| `src/render.py` | Frames parallel rendern und an ffmpeg streamen |

Die erste, ruhigere Fassung (40 s, Kammerton) liegt weiterhin als
`src/scenes_kammer.py` und `src/audio_kammer.py` bei.

### Wie das Bild entsteht

Additiv: Formen und Text landen in Graustufenmasken, die als farbiges Licht auf
den dunklen Grund addiert werden. Der Glow aller Ebenen sammelt sich in **einem**
Puffer bei einem Sechstel der Auflösung, der einmal am Ende hochskaliert wird —
das hält das Rendern schnell und den Look einheitlich. Partikel zeichnen ohne
Überabtastung, Symbole und Ringe mit; die Lichtschneisen laufen direkt in der
Glow-Auflösung. Zum Schluss zoomt und wackelt die Kamera auf den Schlägen.

### Wie der Ton entsteht

Alles Synthese: Chor aus Sägezahnstimmen durch einen Vokalfilter, Trommeln aus
Tonhöhenabfall plus gefiltertem Rauschen, Braams aus additiven Obertönen, die
langsam aufgehen, Hall als FFT-Faltung mit abklingendem Rauschen. Die Flächen
weichen jedem Schlag kurz aus (Ducking). Über allem eine EQ-Kurve und ein
Tiefpass bei 12,5 kHz: laut und wuchtig, aber nichts, was in den Ohren sticht.
Gemessen: Bass 25 %, untere Mitten 22 %, Mitten 31 %, Präsenz 5 %, −16,9 dBFS RMS.

## Texte ändern

Alles steht in `src/timing.py`: `QUESTIONS` (Fragensturm), `QUOTES`
(Philosophen), `DEBATE` (Schlagabtausch), dazu Claims, Titel und Link. Wer
Zeiten verschiebt, verschiebt Bild und Musik gemeinsam — beide lesen dieselben
Konstanten.
