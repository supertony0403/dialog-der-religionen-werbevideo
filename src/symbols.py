"""Die sieben Zeichen am Tisch - als feine Lichtlinien gezeichnet.

Sechs Weltanschauungen plus das Fragezeichen fuer alle, die (noch) suchen.
Bewusst als Linienzeichnung: kein Symbol wirkt massiver als das andere.
"""
from __future__ import annotations

import math

from core import Pen, font

DEVANAGARI = "/usr/share/fonts/noto/NotoSansDevanagari-Light.ttf"


def _star(pen: Pen, c, r, w, a, points=5, rot=-90.0):
    cx, cy = c
    pts = []
    for i in range(points * 2):
        rad = r if i % 2 == 0 else r * 0.42
        ang = math.radians(rot + i * 180.0 / points)
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    pen.polyline(pts, w, a, closed=True)


def cross(pen: Pen, c, r, w, a):
    """Christentum."""
    cx, cy = c
    pen.line((cx, cy - r), (cx, cy + r), w, a)
    pen.line((cx - r * 0.62, cy - r * 0.30), (cx + r * 0.62, cy - r * 0.30), w, a)


def crescent(pen: Pen, c, r, w, a):
    """Islam - Sichel mit Stern."""
    cx, cy = c
    pen.arc((cx - r * 0.10, cy), r * 0.92, 38, 322, w * 1.35, a)
    _star(pen, (cx + r * 0.60, cy), r * 0.34, w, a)


def star_of_david(pen: Pen, c, r, w, a):
    """Judentum."""
    cx, cy = c
    for rot in (-90, 90):
        pts = [(cx + r * math.cos(math.radians(rot + i * 120)),
                cy + r * math.sin(math.radians(rot + i * 120))) for i in range(3)]
        pen.polyline(pts, w, a, closed=True)


def dharma_wheel(pen: Pen, c, r, w, a):
    """Buddhismus - Rad der Lehre."""
    cx, cy = c
    pen.ring(c, r, w, a)
    pen.ring(c, r * 0.22, w, a)
    for i in range(8):
        ang = math.radians(i * 45)
        dx, dy = math.cos(ang), math.sin(ang)
        pen.line((cx + dx * r * 0.22, cy + dy * r * 0.22),
                 (cx + dx * r * 0.97, cy + dy * r * 0.97), w * 0.85, a)


def yin_yang(pen: Pen, c, r, w, a):
    """Taoismus / oestliche Weisheit."""
    cx, cy = c
    pen.ring(c, r, w, a)
    pen.arc((cx, cy - r / 2), r / 2, -90, 90, w, a)
    pen.arc((cx, cy + r / 2), r / 2, 90, 270, w, a)
    pen.disc((cx, cy - r / 2), r * 0.13, a)
    pen.disc((cx, cy + r / 2), r * 0.13, a * 0.35)


def question(pen: Pen, c, r, w, a):
    """Fuer die Suchenden, Zweifelnden, Konfessionslosen."""
    cx, cy = c
    pen.ring(c, r, w * 0.8, a * 0.75)
    pen.arc((cx, cy - r * 0.34), r * 0.36, 170, 20, w * 1.15, a)
    pen.line((cx + r * 0.32, cy - r * 0.22), (cx, cy + r * 0.18), w * 1.15, a)
    pen.disc((cx, cy + r * 0.46), w * 0.85, a)


def khanda(pen: Pen, c, r, w, a):
    """Sikhismus - Doppelschwert im Chakra, flankiert von zwei Saebeln."""
    cx, cy = c
    pen.ring((cx, cy + r * 0.10), r * 0.52, w, a)                   # Chakra
    pen.line((cx, cy - r * 0.72), (cx, cy + r * 0.86), w * 1.2, a)  # Khanda
    pen.polyline([(cx - r * 0.15, cy - r * 0.60), (cx, cy - r * 1.00),
                  (cx + r * 0.15, cy - r * 0.60)], w, a)
    pen.line((cx - r * 0.16, cy + r * 0.62), (cx + r * 0.16, cy + r * 0.62), w, a)
    for sgn in (-1, 1):
        # gekruemmter Saebel: Bogenmittelpunkt liegt auf der Gegenseite
        a0, a1 = (120, 240) if sgn < 0 else (-60, 60)
        pen.arc((cx - sgn * r * 0.55, cy + r * 0.05), r * 1.28, a0, a1, w, a)
        pen.line((cx + sgn * r * 0.73, cy + r * 0.62),
                 (cx + sgn * r * 0.52, cy + r * 0.92), w * 1.1, a)


def nine_star(pen: Pen, c, r, w, a):
    """Bahai - neunzackiger Stern."""
    _star(pen, c, r, w, a, points=9, rot=-90)


def torii(pen: Pen, c, r, w, a):
    """Shinto - das Tor zum Heiligen."""
    cx, cy = c
    pen.line((cx - r * 1.02, cy - r * 0.62), (cx + r * 1.02, cy - r * 0.62), w * 1.2, a)
    pen.line((cx - r * 0.84, cy - r * 0.26), (cx + r * 0.84, cy - r * 0.26), w, a)
    pen.line((cx - r * 0.60, cy - r * 0.62), (cx - r * 0.72, cy + r * 0.92), w, a)
    pen.line((cx + r * 0.60, cy - r * 0.62), (cx + r * 0.72, cy + r * 0.92), w, a)
    pen.line((cx - r * 0.10, cy - r * 0.62), (cx + r * 0.10, cy - r * 0.62), w, a)


def fire_bowl(pen: Pen, c, r, w, a):
    """Zoroastrismus - das ewige Feuer."""
    cx, cy = c
    pen.arc((cx, cy + r * 0.32), r * 0.62, 0, 180, w, a)          # Schale
    pen.line((cx - r * 0.62, cy + r * 0.32), (cx + r * 0.62, cy + r * 0.32), w, a)
    pen.line((cx, cy + r * 0.94), (cx, cy + r * 0.70), w, a)
    pen.line((cx - r * 0.40, cy + r * 0.98), (cx + r * 0.40, cy + r * 0.98), w, a)
    import math as _m
    for sx, h, bend in ((-0.30, 0.34, 0.18), (0.0, 0.62, -0.10), (0.30, 0.30, -0.20)):
        pts = []
        for i in range(9):
            u_ = i / 8
            pts.append((cx + r * (sx + bend * _m.sin(_m.pi * u_) - 0.20 * (1 - u_) ** 2 * sx),
                        cy + r * (0.24 - (0.42 + h) * u_ ** 1.15)))
        pen.polyline(pts, w * 0.95, a)


def ahimsa(pen: Pen, c, r, w, a):
    """Jainismus - die erhobene Hand der Gewaltlosigkeit."""
    cx, cy = c
    # Handflaeche mit Daumen links
    pen.polyline([(cx + r * 0.50, cy + r * 0.98), (cx + r * 0.50, cy - r * 0.30),
                  (cx + r * 0.42, cy - r * 0.52)], w, a)
    pen.polyline([(cx - r * 0.50, cy + r * 0.98), (cx - r * 0.50, cy - r * 0.02),
                  (cx - r * 0.66, cy - r * 0.30), (cx - r * 0.50, cy - r * 0.44)], w, a)
    # vier Fingerkuppen
    for k, x in enumerate((-0.36, -0.12, 0.12, 0.34)):
        top = r * (0.92 if k in (1, 2) else 0.74)
        pen.arc((cx + r * x, cy - top), r * 0.13, 180, 360, w, a)
        pen.line((cx + r * x - r * 0.13, cy - top), (cx + r * x - r * 0.13, cy - r * 0.30), w, a)
        pen.line((cx + r * x + r * 0.13, cy - top), (cx + r * x + r * 0.13, cy - r * 0.30), w, a)
    pen.line((cx - r * 0.50, cy + r * 0.98), (cx + r * 0.50, cy + r * 0.98), w, a)
    pen.ring((cx, cy + r * 0.30), r * 0.26, w * 0.9, a)


# Om wird als Schriftzeichen gesetzt (Devanagari), der Rest ist gezeichnet.
DRAWN = {
    "kreuz": cross,
    "halbmond": crescent,
    "davidstern": star_of_david,
    "rad": dharma_wheel,
    "yinyang": yin_yang,
    "frage": question,
    "khanda": khanda,
    "neunstern": nine_star,
    "torii": torii,
    "feuer": fire_bowl,
    "ahimsa": ahimsa,
}

# Reihenfolge im Kreis - zwoelf Positionen wie auf einem Zifferblatt
ORDER = ["kreuz", "halbmond", "davidstern", "rad", "om", "yinyang",
         "khanda", "neunstern", "torii", "feuer", "ahimsa", "frage"]
LABELS = {
    "kreuz": "Christentum", "halbmond": "Islam", "davidstern": "Judentum",
    "rad": "Buddhismus", "om": "Hinduismus", "yinyang": "Taoismus",
    "khanda": "Sikhismus", "neunstern": "Bahai", "torii": "Shinto",
    "feuer": "Zoroastrismus", "ahimsa": "Jainismus", "frage": "Suchende",
}


def draw(frame, name: str, c, r, w, a, color):
    """Zeichnet ein Symbol in den Lichtlayer der gewuenschten Farbe."""
    if a <= 0.004:
        return
    if name == "om":
        f = font.__self__ if False else None  # noqa: F841  (Om nutzt Systemschrift)
        from core import sys_font
        frame.text("ॐ", sys_font(DEVANAGARI, r * 2.05), c, color, a, anchor="mm")
        return
    DRAWN[name](frame.pen(color), c, r, w, a)
