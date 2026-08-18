"""Render-Kern des DDR-Werbevideos.

Alles wird als Licht auf schwarzem Grund gedacht: Formen und Text landen in
Graustufen-Masken, die additiv mit einer Farbe ins Bild geblendet werden.
Dadurch entsteht der Kerzenschein-/Glasfenster-Look ohne teure Compositing-Tricks.
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "fonts"
FPS = 30

# ---------------------------------------------------------------- Farbwelt ---
GOLD = (1.00, 0.74, 0.36)
GOLD_PALE = (1.00, 0.89, 0.70)
BLUE = (0.66, 0.82, 1.00)
VIOLET = (0.82, 0.74, 1.00)
TEAL = (0.36, 0.86, 0.84)
WARM = (1.00, 0.95, 0.88)
DIM = (0.76, 0.80, 0.92)

# --------------------------------------------------------------- Easing -----
def clamp01(x: float) -> float:
    return 0.0 if x < 0 else (1.0 if x > 1 else x)


def seg(t: float, start: float, end: float) -> float:
    """Normierte Position von t innerhalb des Fensters [start, end]."""
    if end <= start:
        return 1.0
    return clamp01((t - start) / (end - start))


def smooth(x: float) -> float:
    x = clamp01(x)
    return x * x * (3 - 2 * x)


def ease_out(x: float, p: float = 3.0) -> float:
    return 1 - (1 - clamp01(x)) ** p


def ease_in(x: float, p: float = 3.0) -> float:
    return clamp01(x) ** p


def ease_in_out(x: float) -> float:
    x = clamp01(x)
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def pulse(t: float, period: float, sharp: float = 6.0) -> float:
    """Weicher Puls zwischen 0 und 1 mit einstellbarer Spitzigkeit."""
    phase = (t % period) / period
    return math.exp(-sharp * phase) if phase < 1 else 0.0


def fade(t: float, a: float, b: float, c: float, d: float) -> float:
    """Trapezblende: rein a->b, halten b->c, raus c->d."""
    if t < a or t > d:
        return 0.0
    if t < b:
        return smooth(seg(t, a, b))
    if t <= c:
        return 1.0
    return 1.0 - smooth(seg(t, c, d))


# ---------------------------------------------------------------- Fonts -----
_FONT_CACHE: dict = {}


def font(name: str, size: float, weight: int | None = None, opsz: float | None = None):
    key = (name, round(size, 1), weight, opsz)
    if key in _FONT_CACHE:
        return _FONT_CACHE[key]
    f = ImageFont.truetype(str(FONTS / f"{name}.ttf"), max(6, int(round(size))))
    axes = []
    try:
        available = [a["name"].decode() if isinstance(a["name"], bytes) else a["name"]
                     for a in f.get_variation_axes()]
    except OSError:
        available = []
    for ax in available:
        if ax == "Optical size":
            axes.append(opsz if opsz is not None else min(32, max(14, size / 3)))
        elif ax == "Weight":
            axes.append(weight if weight is not None else 400)
    if axes:
        f.set_variation_by_axes(axes)
    _FONT_CACHE[key] = f
    return f


def sys_font(path: str, size: float):
    key = (path, round(size, 1))
    if key not in _FONT_CACHE:
        _FONT_CACHE[key] = ImageFont.truetype(path, max(6, int(round(size))))
    return _FONT_CACHE[key]


def text_size(f, s: str, tracking: float = 0.0) -> tuple[float, float]:
    if not s:
        return 0.0, 0.0
    if tracking:
        w = sum(f.getlength(ch) for ch in s) + tracking * (len(s) - 1)
    else:
        w = f.getlength(s)
    box = f.getbbox(s)
    return w, box[3] - box[1]


def wrap(f, s: str, max_w: float, tracking: float = 0.0) -> list[str]:
    words, lines, cur = s.split(), [], ""
    for w in words:
        probe = f"{cur} {w}".strip()
        if text_size(f, probe, tracking)[0] <= max_w or not cur:
            cur = probe
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


# ------------------------------------------------------------ Zeichenhilfe --
class Pen:
    """Zeichnet in eine überabgetastete Maske; Koordinaten in Bildpixeln."""

    def __init__(self, draw: ImageDraw.ImageDraw, ss: int):
        self.d = draw
        self.ss = ss

    def _p(self, xy):
        return [c * self.ss for c in xy]

    def line(self, p0, p1, width, alpha=1.0):
        if alpha <= 0.002:
            return
        self.d.line([*self._p(p0), *self._p(p1)], fill=int(255 * clamp01(alpha)),
                    width=max(1, int(round(width * self.ss))), joint="curve")

    def polyline(self, pts, width, alpha=1.0, closed=False):
        if alpha <= 0.002 or len(pts) < 2:
            return
        flat = [c * self.ss for p in pts for c in p]
        if closed:
            flat += [pts[0][0] * self.ss, pts[0][1] * self.ss]
        self.d.line(flat, fill=int(255 * clamp01(alpha)),
                    width=max(1, int(round(width * self.ss))), joint="curve")

    def disc(self, c, r, alpha=1.0):
        if alpha <= 0.002 or r <= 0:
            return
        x, y = c
        self.d.ellipse([(x - r) * self.ss, (y - r) * self.ss,
                        (x + r) * self.ss, (y + r) * self.ss],
                       fill=int(255 * clamp01(alpha)))

    def ring(self, c, r, width, alpha=1.0):
        self.arc(c, r, 0, 360, width, alpha)

    def arc(self, c, r, a0, a1, width, alpha=1.0):
        if alpha <= 0.002 or r <= 0 or abs(a1 - a0) < 0.05:
            return
        x, y = c
        self.d.arc([(x - r) * self.ss, (y - r) * self.ss,
                    (x + r) * self.ss, (y + r) * self.ss],
                   a0, a1, fill=int(255 * clamp01(alpha)),
                   width=max(1, int(round(width * self.ss))))

    def rounded_rect(self, box, radius, width, alpha=1.0):
        if alpha <= 0.002:
            return
        x0, y0, x1, y1 = [c * self.ss for c in box]
        self.d.rounded_rectangle([x0, y0, x1, y1], radius=radius * self.ss,
                                 outline=int(255 * clamp01(alpha)),
                                 width=max(1, int(round(width * self.ss))))

    def polygon(self, pts, alpha=1.0):
        if alpha <= 0.002:
            return
        self.d.polygon([c * self.ss for p in pts for c in p],
                       fill=int(255 * clamp01(alpha)))


# ---------------------------------------------------------------- Frame -----
class Frame:
    """Sammelt Licht-Layer und komponiert sie zu einem Bild."""

    SS = 2

    def __init__(self, w: int, h: int):
        self.w, self.h = w, h
        self.u = min(w, h) / 1080.0          # Layout-Einheit
        self.cx, self.cy = w / 2, h / 2
        self.gw, self.gh = max(16, w // 6), max(16, h // 6)
        self.buf = np.zeros((h, w, 3), np.float32)
        self._shape: dict[tuple, tuple] = {}
        self._text: dict[tuple, tuple] = {}

    # -- Layer-Zugriff -------------------------------------------------
    def pen(self, color, glow: float = 1.0) -> Pen:
        key = (color, round(glow, 2))
        if key not in self._shape:
            img = Image.new("L", (self.w * self.SS, self.h * self.SS), 0)
            self._shape[key] = (img, Pen(ImageDraw.Draw(img), self.SS))
        return self._shape[key][1]

    def text_layer(self, color, glow: float = 1.0) -> ImageDraw.ImageDraw:
        key = (color, round(glow, 2))
        if key not in self._text:
            img = Image.new("L", (self.w, self.h), 0)
            self._text[key] = (img, ImageDraw.Draw(img))
        return self._text[key][1]

    # -- Text ----------------------------------------------------------
    def text(self, s: str, f, xy, color, alpha=1.0, anchor="mm",
             tracking=0.0, glow=1.0):
        if alpha <= 0.004 or not s:
            return
        d = self.text_layer(color, glow)
        fill = int(255 * clamp01(alpha))
        if not tracking:
            d.text(xy, s, font=f, fill=fill, anchor=anchor)
            return
        total = sum(f.getlength(ch) for ch in s) + tracking * (len(s) - 1)
        x, y = xy
        if anchor[0] == "m":
            x -= total / 2
        elif anchor[0] == "r":
            x -= total
        va = anchor[1]
        for ch in s:
            d.text((x, y), ch, font=f, fill=fill, anchor="l" + va)
            x += f.getlength(ch) + tracking

    # -- Direkte Arrays (Nebel, Korn ...) ------------------------------
    def add_array(self, arr: np.ndarray, color, gain: float = 1.0):
        if gain <= 0:
            return
        self.buf += arr[..., None] * (np.asarray(color, np.float32) * gain)

    # -- Komposition ---------------------------------------------------
    def compose(self):
        """Liefert (scharfes Bild, kleiner Lichtbuffer fuer den Glow)."""
        gw, gh = self.gw, self.gh
        glow = np.zeros((gh, gw, 3), np.float32)
        for (color, gstr), (img, _) in self._shape.items():
            col = np.asarray(color, np.float32)
            m = np.asarray(img.reduce(self.SS), np.float32) / 255.0
            self.buf += m[..., None] * col
            if gstr > 0.01:
                small = np.asarray(img.resize((gw, gh), Image.BILINEAR), np.float32) / 255.0
                glow += small[..., None] * (col * gstr)
        for (color, gstr), (img, _) in self._text.items():
            col = np.asarray(color, np.float32)
            self.buf += (np.asarray(img, np.float32) / 255.0)[..., None] * col
            if gstr > 0.01:
                small = np.asarray(img.resize((gw, gh), Image.BILINEAR), np.float32) / 255.0
                glow += small[..., None] * (col * gstr * 0.75)
        return self.buf, glow


def box_blur(a: np.ndarray, r: int) -> np.ndarray:
    """Separabler Box-Blur (3 Durchgaenge ~ Gauss) auf kleinen Arrays."""
    if r < 1:
        return a
    out = a
    for _ in range(3):
        for axis in (0, 1):
            n = out.shape[axis]
            pad = [(0, 0)] * out.ndim
            pad[axis] = (r, r)
            p = np.pad(out, pad, mode="edge")
            c = np.cumsum(p, axis=axis)
            zero = np.zeros_like(np.take(c, [0], axis=axis))
            c = np.concatenate([zero, c], axis=axis)
            lo = np.take(c, np.arange(0, n), axis=axis)
            hi = np.take(c, np.arange(2 * r + 1, n + 2 * r + 1), axis=axis)
            out = (hi - lo) / (2 * r + 1)
    return out


# ------------------------------------------------------------ Hintergrund ---
class Backdrop:
    """Tiefblauer Grund, driftende Nebelschleier, Sternenstaub, Korn, Vignette."""

    def __init__(self, w: int, h: int, seed: int = 7):
        self.w, self.h = w, h
        self.gw, self.gh = max(16, w // 6), max(16, h // 6)
        rng = np.random.default_rng(seed)
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        nx, ny = xx / w, yy / h
        r = np.sqrt((nx - 0.5) ** 2 + ((ny - 0.5) * (h / w)) ** 2)

        base = np.zeros((h, w, 3), np.float32)
        base[..., 0] = 0.021 + 0.040 * np.exp(-2.4 * r ** 2)
        base[..., 1] = 0.029 + 0.050 * np.exp(-2.4 * r ** 2)
        base[..., 2] = 0.054 + 0.092 * np.exp(-2.1 * r ** 2)
        base *= (0.75 + 0.25 * (1 - ny) ** 1.5)[..., None]

        stars = np.zeros((h, w), np.float32)
        n = int(w * h / 5200)
        ys, xs = rng.integers(0, h, n), rng.integers(0, w, n)
        stars[ys, xs] = rng.random(n) ** 2.2
        stars = np.asarray(
            Image.fromarray((stars * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.7)),
            np.float32) / 255.0
        base += stars[..., None] * np.asarray((0.30, 0.36, 0.48), np.float32)
        self.base = base

        # Nebel im kleinen Raster (wandert in den Lichtbuffer)
        self.clouds = []
        for _ in range(2):
            small = rng.random((max(3, self.gh // 14), max(3, self.gw // 14))).astype(np.float32)
            img = Image.fromarray((small * 255).astype(np.uint8)).resize(
                (self.gw, self.gh), Image.BICUBIC)
            c = np.asarray(img, np.float32) / 255.0
            c = (c - c.min()) / max(1e-6, float(np.ptp(c)))
            self.clouds.append(c ** 2.1)

        self.vig = np.clip(1.10 - 0.70 * (r * 1.34) ** 2.0, 0.34, 1.0).astype(np.float32)[..., None]
        self.grain = [rng.normal(0, 1, (h, w, 1)).astype(np.float32) for _ in range(6)]

    def mist(self, t: float, gain: float = 1.0) -> np.ndarray:
        """Nebelbeitrag fuer den Lichtbuffer."""
        mix = 0.5 + 0.5 * math.sin(t * 0.11)
        c = self.clouds[0] * mix + self.clouds[1] * (1 - mix)
        c = np.roll(c, (int(t * 1.6) % self.gh, int(t * 2.4) % self.gw), (0, 1))
        return c[..., None] * (np.asarray((0.030, 0.042, 0.105), np.float32) * gain)

    def finish(self, buf: np.ndarray, glow: np.ndarray, i: int,
               exposure: float = 1.0) -> np.ndarray:
        wide = box_blur(glow, max(2, self.gw // 40))
        tight = box_blur(glow, max(1, self.gw // 150))
        g = tight * 0.60 + wide * 0.95
        gimg = Image.fromarray(np.clip(g * 255.0, 0, 255).astype(np.uint8)).resize(
            (self.w, self.h), Image.BILINEAR)
        out = buf + self.base + np.asarray(gimg, np.float32) / 255.0
        out *= self.vig
        out *= exposure
        # Soft-Knee: Mitteltoene bleiben linear, nur Spitzen werden gerollt
        knee = 0.82
        hi = out > knee
        out[hi] = knee + (1.0 - knee) * (1.0 - np.exp(-(out[hi] - knee) / (1.0 - knee)))
        out += self.grain[i % len(self.grain)] * 0.006
        return (np.clip(out, 0, 1) * 255).astype(np.uint8)
