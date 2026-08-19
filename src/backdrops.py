"""Bewegte Hintergrundebenen - das "Filmmaterial" unter den Texten.

Alles ist simuliert, kein Stock-Footage: ein Sternenflug mit Tiefe, rotierende
Lichtschneisen, aufsteigende Glut, stroemender Nebel und Schockwellen auf den
Schlaegen. Die Ebenen zeichnen in dieselben Lichtmasken wie alles andere.
"""
from __future__ import annotations

import math

import numpy as np
from PIL import Image

from core import box_blur


class Starfield:
    """Flug durch Sternenstaub. Je schneller, desto laenger die Striche."""

    def __init__(self, n: int = 420, seed: int = 5):
        rng = np.random.default_rng(seed)
        self.x = rng.uniform(-1.6, 1.6, n)
        self.y = rng.uniform(-1.0, 1.0, n)
        self.z0 = rng.uniform(0.05, 1.0, n)
        self.bright = rng.uniform(0.25, 1.0, n) ** 1.6
        self.n = n

    def draw(self, frame, t: float, speed: float, gain: float, color, warp: float = 1.0):
        if gain <= 0.01:
            return
        h = min(frame.w, frame.h)
        z = (self.z0 - t * speed * 0.16) % 1.0 + 0.02
        zp = np.maximum(z - speed * 0.010 * warp, 0.012)
        f = 0.75 * h
        px, py = frame.cx + self.x * f / z, frame.cy + self.y * f / z
        qx, qy = frame.cx + self.x * f / zp, frame.cy + self.y * f / zp
        a = self.bright * np.clip(1.0 - z, 0, 1) ** 1.7 * gain
        pen = frame.pen(color, glow=0.55, ss=1)
        m = 2.2 * frame.u
        for i in range(self.n):
            if a[i] < 0.02:
                continue
            if not (-m < px[i] < frame.w + m and -m < py[i] < frame.h + m):
                continue
            wpx = max(1.0, 2.6 * frame.u * (1.0 - z[i]))
            if abs(qx[i] - px[i]) + abs(qy[i] - py[i]) > 2.0:
                pen.line((px[i], py[i]), (qx[i], qy[i]), wpx * 0.8, min(1.0, a[i]))
            else:
                pen.disc((px[i], py[i]), wpx * 0.5, min(1.0, a[i]))


class GodRays:
    """Lichtschneisen aus einem Punkt - langsam drehend, wie Fenster im Staub."""

    def __init__(self, count: int = 14, seed: int = 9):
        rng = np.random.default_rng(seed)
        self.phase = rng.uniform(0, math.tau, count)
        self.width = rng.uniform(0.010, 0.055, count)
        self.speed = rng.uniform(0.02, 0.06, count) * rng.choice([-1, 1], count)
        self.amp = rng.uniform(0.35, 1.0, count)
        self.count = count

    def draw(self, frame, t: float, origin, gain: float, color, length: float = 1.9):
        if gain <= 0.01:
            return
        pen = frame.soft(color, 1.0)
        ox, oy = origin
        far = length * max(frame.w, frame.h)
        for i in range(self.count):
            ang = self.phase[i] + t * self.speed[i]
            wob = 0.55 + 0.45 * math.sin(t * 0.7 + self.phase[i] * 3)
            a = gain * self.amp[i] * wob * 0.13
            if a < 0.01:
                continue
            hw = self.width[i]
            pts = [(ox, oy),
                   (ox + far * math.cos(ang - hw), oy + far * math.sin(ang - hw)),
                   (ox + far * math.cos(ang + hw), oy + far * math.sin(ang + hw))]
            pen.polygon(pts, a)


class Embers:
    """Aufsteigende Glut - Funken, die flackern und vergehen."""

    def __init__(self, n: int = 150, seed: int = 17):
        rng = np.random.default_rng(seed)
        self.x = rng.random(n)
        self.y0 = rng.random(n)
        self.sp = rng.uniform(0.020, 0.075, n)
        self.sw = rng.uniform(0.004, 0.020, n)
        self.ph = rng.uniform(0, math.tau, n)
        self.sz = rng.uniform(0.6, 2.1, n)
        self.n = n

    def draw(self, frame, t: float, gain: float, color):
        if gain <= 0.01:
            return
        pen = frame.pen(color, glow=1.3, ss=1)
        for i in range(self.n):
            y = (self.y0[i] - t * self.sp[i]) % 1.15 - 0.075
            life = 1.0 - abs(y - 0.45) * 1.55
            if life <= 0.05:
                continue
            x = self.x[i] + self.sw[i] * math.sin(t * 0.8 + self.ph[i]) * 3
            flick = 0.55 + 0.45 * math.sin(t * 6.5 + self.ph[i] * 5)
            pen.disc((x * frame.w, y * frame.h),
                     self.sz[i] * frame.u * 1.5, min(1.0, life * flick * gain))


class Flow:
    """Stroemender Nebel: zwei Rauschebenen, die sich gegenseitig verzerren."""

    def __init__(self, gw: int, gh: int, seed: int = 23):
        rng = np.random.default_rng(seed)
        self.gw, self.gh = gw, gh
        self.layers = []
        for octave, sc in enumerate((10, 5, 3)):
            small = rng.random((max(3, gh // sc), max(3, gw // sc))).astype(np.float32)
            img = Image.fromarray((small * 255).astype(np.uint8)).resize((gw, gh), Image.BICUBIC)
            arr = np.asarray(img, np.float32) / 255.0
            arr = (arr - arr.min()) / max(1e-6, float(np.ptp(arr)))
            self.layers.append(arr)
        yy, xx = np.mgrid[0:gh, 0:gw].astype(np.float32)
        self.nx, self.ny = xx / gw, yy / gh

    def field(self, t: float, gain: float, tint) -> np.ndarray:
        a, b, c = self.layers
        wx = int(t * 5.5) % self.gw
        wy = int(t * 2.2) % self.gh
        warp = np.roll(a, (wy, wx), (0, 1))
        base = np.roll(b, (int(t * 1.1) % self.gh, int(-t * 3.4) % self.gw), (0, 1))
        det = np.roll(c, (int(-t * 2.6) % self.gh, int(t * 6.1) % self.gw), (0, 1))
        f = (base * 0.62 + det * 0.38) * (0.45 + 0.85 * warp)
        f = np.clip(f - 0.20, 0, None) ** 1.35
        return f[..., None] * (np.asarray(tint, np.float32) * gain)


def shockwave(frame, center, progress: float, gain: float, color, spread: float = 1.05):
    """Expandierender Ring auf einen Schlag."""
    if not (0.0 <= progress < 1.0) or gain <= 0.01:
        return
    r = spread * max(frame.w, frame.h) * 0.5 * (progress ** 0.55)
    a = gain * (1.0 - progress) ** 2.1
    frame.pen(color, glow=1.2, ss=1).ring(center, r, (3.4 * (1 - progress) + 0.7) * frame.u, a)


def camera(img: Image.Image, zoom: float, dx: float, dy: float,
           roll: float = 0.0) -> Image.Image:
    """Zoom, Versatz und leichte Drehung auf das fertige Bild."""
    w, h = img.size
    if roll:
        img = img.rotate(roll, resample=Image.BILINEAR, expand=False)
    if abs(zoom - 1.0) < 1e-3 and abs(dx) < 0.5 and abs(dy) < 0.5:
        return img
    zoom = max(1.0, zoom)
    bw, bh = w / zoom, h / zoom
    cx, cy = w / 2 + dx, h / 2 + dy
    cx = min(max(cx, bw / 2), w - bw / 2)
    cy = min(max(cy, bh / 2), h - bh / 2)
    box = (cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2)
    return img.resize((w, h), Image.BILINEAR, box=box)


def shake_at(t: float, hits, strength: float = 1.0, decay: float = 7.0):
    """Kamerawackeln nach jedem Schlag, exponentiell abklingend."""
    dx = dy = 0.0
    for i, ht in enumerate(hits):
        dt = t - ht
        if 0 <= dt < 0.75:
            e = math.exp(-decay * dt) * strength
            dx += math.sin(dt * 61 + i) * 13 * e
            dy += math.sin(dt * 47 + i * 2.1) * 9 * e
    return dx, dy


def punch_at(t: float, hits, amount: float = 0.055, decay: float = 5.5):
    """Kurzer Zoomstoss nach jedem Schlag."""
    z = 1.0
    for ht in hits:
        dt = t - ht
        if 0 <= dt < 1.0:
            z += amount * math.exp(-decay * dt)
    return z
