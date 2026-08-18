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


# Om wird als Schriftzeichen gesetzt (Devanagari), der Rest ist gezeichnet.
DRAWN = {
    "kreuz": cross,
    "halbmond": crescent,
    "davidstern": star_of_david,
    "rad": dharma_wheel,
    "yinyang": yin_yang,
    "frage": question,
}

ORDER = ["kreuz", "halbmond", "davidstern", "rad", "om", "yinyang", "frage"]
LABELS = {
    "kreuz": "Christentum", "halbmond": "Islam", "davidstern": "Judentum",
    "rad": "Buddhismus", "om": "Hinduismus", "yinyang": "Taoismus",
    "frage": "Suchende",
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
