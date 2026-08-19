"""Storyboard des Werbevideos - 40 Sekunden in sechs Szenen.

    S1  0.00 - 5.33   Die eine Frage
    S2  5.33 - 13.33  Der Fragensturm
    S3 13.33 - 21.33  Der Kreis: sieben Zeichen, ein Netz aus Gespraechen
    S4 21.33 - 29.33  Die Haltung des Servers
    S5 29.33 - 34.67  Emblem und Name
    S6 34.67 - 40.00  Einladung

Alle Positionen sind formatunabhaengig: horizontal ueber die Bildmitte,
vertikal ueber Anteile der Bildhoehe, Groessen ueber die Layout-Einheit u.
"""
from __future__ import annotations

import math

import symbols
from core import (BLUE, DIM, GOLD, GOLD_PALE, TEAL, VIOLET, WARM, ease_in,
                  ease_out, fade, font, seg, smooth, sys_font)

T1, T2, T3, T4, T5, T6, TEND = 0.0, 5.3333, 13.3333, 21.3333, 29.3333, 34.6667, 40.0
RING_R = 330.0          # Radius des grossen Kreises in Layout-Einheiten
EMBLEM_Y = 0.335        # Ankerhoehe des Emblems (Anteil der Bildhoehe)


class Layout:
    def __init__(self, frame):
        self.f = frame
        self.w, self.h, self.u = frame.w, frame.h, frame.u
        self.cx, self.cy = frame.cx, frame.cy
        self.tall = frame.h > frame.w
        self.text_w = self.w * 0.86

    def y(self, frac: float) -> float:
        """Anteil der Bildhoehe; im Hochformat um die Mitte gestaucht."""
        if self.tall:
            frac = 0.5 + (frac - 0.5) * 0.78
        return self.h * frac

    def x(self, dx: float, width: float = 0.0) -> float:
        """Horizontaler Versatz; haelt den Textblock immer im sicheren Bereich."""
        x = self.cx + dx * self.u
        margin = self.w * 0.055 + width / 2
        return max(margin, min(self.w - margin, x))

    def fit(self, name: str, size: float, weight: int, text: str,
            max_frac: float = 0.88, tracking: float = 0.0):
        """Schrift so weit verkleinern, bis die Zeile ins Bild passt."""
        limit = self.w * max_frac
        for _ in range(14):
            f = font(name, size * self.u, weight)
            w = sum(f.getlength(ch) for ch in text) + tracking * max(0, len(text) - 1)
            if w <= limit or size < 12:
                return f
            size *= 0.94
        return font(name, size * self.u, weight)


def _lines(frame, L, text, f, y, color, alpha, tracking=0.0, lead=1.34, anchor="mm"):
    rows = []
    for para in text.split("\n"):
        rows += [""] if not para else _wrap(f, para, L.text_w, tracking)
    step = f.size * lead
    top = y - step * (len(rows) - 1) / 2
    for i, row in enumerate(rows):
        frame.text(row, f, (L.cx, top + i * step), color, alpha,
                   anchor=anchor, tracking=tracking)
    return len(rows)


def _wrap(f, s, max_w, tracking=0.0):
    from core import wrap
    return wrap(f, s, max_w, tracking)


# ------------------------------------------------------------------ S1 ------
def scene_one(fr, L, t):
    if t > T2 + 0.7:
        return
    u = L.u
    # ein einzelner Lichtpunkt, der zu atmen beginnt
    grow = ease_out(seg(t, 0.0, 2.6), 2.0)
    breathe = 1.0 + 0.12 * math.sin(t * 1.9)
    a = fade(t, 0.15, 1.1, T2 - 0.9, T2 + 0.35)
    r = (3.0 + 7.0 * grow) * u * breathe
    pen = fr.pen(GOLD_PALE, glow=1.5)
    pen.disc((L.cx, L.y(0.46)), r, a)
    pen.ring((L.cx, L.y(0.46)), r * 4.6 + 26 * u * grow, 1.1 * u, a * 0.30)

    q = fade(t, 1.0, 2.3, T2 - 1.0, T2 + 0.25)
    if q > 0:
        f = font("EBGaramond-Italic", 96 * u, 430)
        drift = (1 - ease_out(seg(t, 1.0, 3.0))) * 16 * u
        _lines(fr, L, "Woran glaubst du?", f, L.y(0.60) + drift, WARM, q)


# ------------------------------------------------------------------ S2 ------
QUESTIONS = [
    # Text, Startzeit, dx, y-Anteil, Groesse, Farbe
    ("Gibt es Gott – oder nur uns?",      5.50, -230, 0.24, 60, WARM),
    ("Was kommt danach?",                 6.28,  265, 0.41, 56, DIM),
    ("Warum lässt Gott das Leid zu?",     7.06, -205, 0.59, 62, GOLD_PALE),
    ("Braucht Moral Religion?",           7.84,  245, 0.77, 56, BLUE),
    ("Ist Glaube Privatsache?",           8.62,  185, 0.28, 54, DIM),
    ("Hat Wissenschaft Gott ersetzt?",    9.40, -255, 0.48, 58, VIOLET),
    ("Wer entscheidet, was wahr ist?",   10.18, -190, 0.87, 58, WARM),
    ("Und wenn wir uns alle irren?",     10.96,  225, 0.68, 60, GOLD_PALE),
]


def scene_two(fr, L, t):
    if not (T2 - 0.8 <= t <= T3 + 0.6):
        return
    u = L.u
    for i, (text, t0, dx, yf, size, color) in enumerate(QUESTIONS):
        a = fade(t, t0, t0 + 0.8, t0 + 3.4, t0 + 4.6)
        a *= 1.0 - smooth(seg(t, 12.05, 12.75))
        if a <= 0.004:
            continue
        # nach dem Kreisbeginn verstummen alle Stimmen
        a *= 1.0 - smooth(seg(t, T3 - 0.5, T3 + 0.55))
        rise = (1 - ease_out(seg(t, t0, t0 + 3.4))) * 26 * u
        f = L.fit("EBGaramond-Italic", size, 430, text, 0.86)
        x, y = L.x(dx, f.getlength(text)), L.y(yf) + rise
        fr.text(text, f, (x, y), color, a, anchor="mm")

    lead = fade(t, 12.45, 13.05, T3 + 0.05, T3 + 0.55)
    if lead > 0:
        txt = "FRAGEN, DIE MAN NICHT ALLEIN BEANTWORTET"
        f = L.fit("Cinzel", 46, 600, txt, 0.90, tracking=9 * u)
        _lines(fr, L, txt, f, L.y(0.50), GOLD_PALE, lead, tracking=9 * u)


def _tw(f, s):
    return f.getlength(s)


# ------------------------------------------------------------------ S3 ------
LINKS = [(0, 3), (1, 5), (2, 6), (4, 0), (6, 3), (1, 2), (5, 4), (0, 6), (2, 4)]


def ring_geometry(L, t):
    """Position, Radius und Deckkraft des grossen Kreises ueber die Zeit."""
    spin = math.radians(-90 + 2.2 * math.sin(t * 0.18))
    pull = smooth(seg(t, T5, T5 + 0.95))         # Einzug zum Emblem in S5
    r = RING_R * L.u * (1 - 0.72 * pull)
    cy = L.y(0.50) + (L.y(EMBLEM_Y) - L.y(0.50)) * pull
    return (L.cx, cy), r, spin, pull


def sym_positions(L, t):
    c, r, spin, pull = ring_geometry(L, t)
    pts = []
    for i in range(7):
        ang = spin + i * math.tau / 7
        pts.append((c[0] + r * math.cos(ang), c[1] + r * math.sin(ang)))
    return pts, c, r, pull


def scene_three(fr, L, t):
    if t < T3 - 0.7:
        return
    u = L.u
    pts, c, r, pull = sym_positions(L, t)

    # Der Kreis zeichnet sich
    draw = ease_in(seg(t, T3 + 0.32, T3 + 1.62), 1.4)
    presence = 1.0 if t < T4 else (1.0 - 0.88 * smooth(seg(t, T4, T4 + 0.9)))
    if pull > 0:
        presence = max(presence, 0.20 + 0.55 * pull)
    if draw > 0:
        pen = fr.pen(GOLD, glow=1.0)
        pen.arc(c, r, -90, -90 + 360 * draw, 2.0 * u, 0.95 * presence)
        if draw < 1:
            ang = math.radians(-90 + 360 * draw)
            fr.pen(GOLD_PALE, glow=1.6).disc(
                (c[0] + r * math.cos(ang), c[1] + r * math.sin(ang)), 4.2 * u, 0.95)

    # Sieben Zeichen erscheinen nacheinander
    sym_r = 62 * u * (1 - 0.55 * pull)
    for i, name in enumerate(symbols.ORDER):
        t0 = T3 + 1.62 + i * 0.50
        app = ease_out(seg(t, t0, t0 + 0.75), 2.2)
        if app <= 0.004:
            continue
        sym_fade = 1.0 - smooth(seg(t, T4 - 0.15, T4 + 0.75))
        a = app * presence * max(0.0, 1 - 2.2 * pull) * (sym_fade if t < T5 else 0.0)
        scale = 0.72 + 0.28 * app
        symbols.draw(fr, name, pts[i], sym_r * scale, 2.6 * u, a, GOLD_PALE)
        if app < 1:
            fr.pen(WARM, glow=1.8).disc(pts[i], sym_r * 0.22 * (1 - app) + 2 * u, (1 - app) * 0.9)

    # Das Netz der Gespraeche: Linien und wandernde Nachrichten
    for k, (a_i, b_i) in enumerate(LINKS):
        t0 = T3 + 3.7 + k * 0.30
        grow = ease_out(seg(t, t0, t0 + 0.85), 2.0)
        if grow <= 0.004:
            continue
        p0, p1 = pts[a_i], pts[b_i]
        tip = (p0[0] + (p1[0] - p0[0]) * grow, p0[1] + (p1[1] - p0[1]) * grow)
        alpha = 0.46 * presence * (1 - 0.5 * pull)
        fr.pen(BLUE, glow=0.7).line(p0, tip, 1.1 * u, alpha)
        if grow >= 1 and pull < 0.35:
            phase = ((t - t0 - 0.85) * 0.42 + k * 0.13) % 1.0
            mp = (p0[0] + (p1[0] - p0[0]) * phase, p0[1] + (p1[1] - p0[1]) * phase)
            fr.pen(TEAL, glow=1.7).disc(mp, 3.0 * u, 0.85 * presence * (1 - pull))

    cap = fade(t, T3 + 5.6, T3 + 6.3, T4 - 0.30, T4 + 0.25)
    if cap > 0:
        f = L.fit("Cinzel", 46, 620, "SIEBEN WEGE · EIN TISCH", 0.86, tracking=12 * u)
        _lines(fr, L, "SIEBEN WEGE · EIN TISCH", f, L.y(0.895), GOLD_PALE, cap,
               tracking=12 * u)


# ------------------------------------------------------------------ S4 ------
FEATURES = [
    "Tägliche Debatten – von Theodizee bis Kopftuchstreit",
    "Moderiert. Ohne Bekehrungsdruck.",
    "Voice-Runden am Abend",
    "Für Gläubige, Zweifler und Atheisten",
]


def scene_four(fr, L, t):
    if not (T4 - 0.5 <= t <= T5 + 0.4):
        return
    u = L.u
    claim = fade(t, T4 + 0.35, T4 + 1.15, T4 + 3.2, T4 + 3.9)
    if claim > 0:
        big = L.fit("Cinzel", 80, 700, "HIER WIRD", 0.62, tracking=7 * u)
        rise = (1 - ease_out(seg(t, T4 + 0.35, T4 + 1.6))) * 20 * u
        rows_a = _wrap(big, "HIER WIRD GESTRITTEN.", L.text_w, 7 * u)
        step = big.size * 1.22
        top = L.y(0.455) - (len(rows_a) * step + step * 1.35) / 2 + rise
        for i, row in enumerate(rows_a):
            fr.text(row, big, (L.cx, top + i * step), WARM, claim,
                    anchor="mm", tracking=7 * u)
        c2 = fade(t, T4 + 1.25, T4 + 2.0, T4 + 3.2, T4 + 3.9)
        y2 = top + len(rows_a) * step + step * 0.22
        fr.text("NICHT GEHETZT.", big, (L.cx, y2), GOLD, c2, anchor="mm",
                tracking=7 * u)
        sub = fade(t, T4 + 2.15, T4 + 2.85, T4 + 3.3, T4 + 3.9)
        if sub > 0:
            fs = font("Inter", 38 * u, 380)
            _lines(fr, L, "Argumente statt Parolen. Neugier statt Feindbilder.",
                   fs, y2 + step * 1.15, DIM, sub)

    # Vier Zeilen ueber den Server - linksbuendiger Block, Punkt davor
    base = T4 + 3.75
    f = font("Inter", 40 * u, 430)
    blocks = [_wrap(f, line, L.text_w * 0.74) for line in FEATURES]
    width = max(max(f.getlength(r) for r in rows) for rows in blocks)
    x0 = L.cx - width / 2 + 18 * u
    lead = f.size * 1.28
    heights = [len(rows) * lead for rows in blocks]
    gap = 34 * u
    total = sum(heights) + gap * (len(blocks) - 1)
    y = L.y(0.50) - total / 2
    for i, rows in enumerate(blocks):
        t0 = base + i * 0.40
        a = fade(t, t0, t0 + 0.65, T5 - 1.05, T5 - 0.35)
        if a > 0.004:
            slide = (1 - ease_out(seg(t, t0, t0 + 0.9), 2.5)) * 26 * u
            for j, row in enumerate(rows):
                fr.text(row, f, (x0 + slide, y + j * lead + lead / 2), WARM, a,
                        anchor="lm")
            fr.pen(GOLD, glow=1.3).disc((x0 - 26 * u + slide, y + lead / 2), 4.0 * u, a)
        y += heights[i] + gap


# ------------------------------------------------------------------ S5 ------
def emblem(fr, L, t, alpha):
    """Zwei Kreise, die einander durchdringen - das Zeichen des Dialogs."""
    if alpha <= 0.004:
        return
    u = L.u
    cx, cy = L.cx, L.y(EMBLEM_Y)
    R = 84 * u
    close = ease_out(seg(t, T5 + 0.25, T5 + 1.35), 2.2)
    off = (1 - close) * 90 * u + R * 0.42
    pen = fr.pen(GOLD, glow=1.2)
    pen.ring((cx - off, cy), R, 1.9 * u, alpha * 0.9)
    pen.ring((cx + off, cy), R, 1.9 * u, alpha * 0.9)
    pen.ring((cx, cy), R * 1.62, 1.0 * u, alpha * 0.35)
    core_a = alpha * close
    fr.pen(GOLD_PALE, glow=1.9).disc((cx, cy), 5.0 * u * (0.6 + 0.4 * close), core_a)
    for i in range(7):
        ang = -math.pi / 2 + i * math.tau / 7
        rr = R * 1.62
        fr.pen(GOLD, glow=1.0).disc((cx + rr * math.cos(ang), cy + rr * math.sin(ang)),
                                    2.2 * u, alpha * 0.55 * close)


def scene_five(fr, L, t):
    if t < T5 - 0.3:
        return
    u = L.u
    # Lichtstoss im Moment des Emblems
    flash = math.exp(-((t - T5 - 0.05) / 0.26) ** 2)
    if flash > 0.01:
        fr.pen(WARM, glow=1.8).disc((L.cx, L.y(EMBLEM_Y)), 34 * u * (0.5 + 0.8 * flash),
                                    0.42 * flash)
        grow = seg(t, T5, T5 + 0.85)
        fr.pen(GOLD_PALE, glow=1.4).ring((L.cx, L.y(EMBLEM_Y)),
                                         (60 + 520 * ease_out(grow, 2.4)) * u,
                                         2.4 * u * (1 - grow), 0.7 * (1 - grow))
    emb = fade(t, T5 + 0.15, T5 + 1.0, TEND + 5, TEND + 6)
    emblem(fr, L, t, emb)

    # Der Name zieht sich aus der Weite zusammen
    ta = fade(t, T5 + 0.95, T5 + 1.9, TEND + 5, TEND + 6)
    if ta > 0:
        prog = ease_out(seg(t, T5 + 0.95, T5 + 2.5), 2.4)
        tr = (52 - 38 * prog) * u
        f = L.fit("Cinzel", 72, 640, "DIALOG DER", 0.66, tracking=tr)
        _lines(fr, L, "DIALOG DER RELIGIONEN", f, L.y(0.505), WARM, ta,
               tracking=tr, lead=1.24)

    ln = ease_out(seg(t, T5 + 2.0, T5 + 2.9), 2.0) * fade(t, T5 + 2.0, T5 + 2.2,
                                                          TEND + 5, TEND + 6)
    if ln > 0:
        half = L.w * 0.16 * ln
        y = L.y(0.565)
        fr.pen(GOLD, glow=1.0).line((L.cx - half, y), (L.cx + half, y), 1.2 * u, 0.75)

    sa = fade(t, T5 + 2.4, T5 + 3.2, TEND + 5, TEND + 6)
    if sa > 0:
        f = font("Inter", 35 * u, 380)
        _lines(fr, L, "Der Discord für ehrliche Gespräche über Gott und die Welt.",
               f, L.y(0.625), DIM, sa)


# ------------------------------------------------------------------ S6 ------
def scene_six(fr, L, t):
    if t < T6 - 0.5:
        return
    u = L.u
    a = fade(t, T6 - 0.1, T6 + 0.75, TEND + 5, TEND + 6)
    if a > 0:
        label = "discord.gg/dialog-der-religionen"
        f = L.fit("Inter", 44, 600, label + "aaaa", 0.86)
        tw = f.getlength(label) + 6 * u * (len(label) - 1) * 0.0
        pad_x, pad_y = 54 * u, 30 * u
        y = L.y(0.735) + (1 - ease_out(seg(t, T6 - 0.1, T6 + 0.9), 2.4)) * 24 * u
        box = (L.cx - tw / 2 - pad_x, y - pad_y - 6 * u,
               L.cx + tw / 2 + pad_x, y + pad_y + 6 * u)
        breath = 0.72 + 0.28 * (0.5 + 0.5 * math.sin((t - T6) * 2.4))
        fr.pen(GOLD, glow=1.6).rounded_rect(box, 40 * u, 2.0 * u, a * breath)
        fr.text(label, f, (L.cx, y), GOLD_PALE, a, anchor="mm")

    b = fade(t, T6 + 0.9, T6 + 1.7, TEND + 5, TEND + 6)
    if b > 0:
        f = font("EBGaramond-Italic", 54 * u, 440)
        _lines(fr, L, "Komm rein. Stell deine Frage.", f, L.y(0.855), WARM, b)

    # Zum Schluss bleibt der eine Lichtpunkt vom Anfang
    # Das Licht vom Anfang pulsiert leise im Emblem weiter
    glowpt = fade(t, T6 + 1.6, T6 + 2.4, TEND, TEND)
    if glowpt > 0:
        beat = 0.55 + 0.45 * math.sin((t - T6) * 1.9)
        fr.pen(GOLD_PALE, glow=2.0).disc((L.cx, L.y(EMBLEM_Y)), 6.0 * u, glowpt * beat)


# ------------------------------------------------------------- Steuerung ----
def exposure(t: float) -> float:
    """Globale Belichtung: Aufblende, Lichtstoss beim Emblem, Abblende."""
    e = 1.34
    e *= smooth(seg(t, 0.0, 0.9))
    e += 0.85 * math.exp(-((t - T5 - 0.08) / 0.20) ** 2)
    e += 0.16 * math.exp(-((t - T3 - 0.32) / 0.30) ** 2)
    e *= 1.0 - 0.22 * smooth(seg(t, TEND - 0.45, TEND))
    return e


def mist_gain(t: float) -> float:
    return 0.42 + 0.34 * smooth(seg(t, 2.0, 14.0)) - 0.18 * smooth(seg(t, T5, T5 + 2.0))


def render(fr, L, t):
    scene_one(fr, L, t)
    scene_two(fr, L, t)
    scene_three(fr, L, t)
    scene_four(fr, L, t)
    scene_five(fr, L, t)
    scene_six(fr, L, t)
