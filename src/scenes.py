"""Storyboard des Trailers - 72 Sekunden in acht Bewegungen.

Zeiten und Texte stehen in timing.py, damit Bild und Musik dieselbe Partitur
lesen. Jede Szene bringt ihre eigene Hintergrundstimmung mit: Sternenflug,
Lichtschneisen, Glut, stroemender Nebel - und Kamerastoesse auf den Schlaegen.
"""
from __future__ import annotations

import math

import backdrops as bd
import symbols
import timing as T
from core import (BLUE, DIM, GOLD, GOLD_PALE, TEAL, VIOLET, WARM, ease_in,
                  ease_out, fade, font, seg, smooth, sys_font, wrap)

RING_R = 372.0
EMBLEM_Y = 0.300


class Layout:
    def __init__(self, frame):
        self.f = frame
        self.w, self.h, self.u = frame.w, frame.h, frame.u
        self.cx, self.cy = frame.cx, frame.cy
        self.tall = frame.h > frame.w
        self.text_w = self.w * 0.86

    def y(self, frac: float) -> float:
        if self.tall:
            frac = 0.5 + (frac - 0.5) * 0.80
        return self.h * frac

    def x(self, dx: float, width: float = 0.0) -> float:
        x = self.cx + dx * self.u
        margin = self.w * 0.055 + width / 2
        return max(margin, min(self.w - margin, x))

    def fit(self, name: str, size: float, weight: int, text: str,
            max_frac: float = 0.88, tracking: float = 0.0):
        limit = self.w * max_frac
        for _ in range(16):
            f = font(name, size * self.u, weight)
            w = sum(f.getlength(ch) for ch in text) + tracking * max(0, len(text) - 1)
            if w <= limit or size < 11:
                return f
            size *= 0.94
        return font(name, size * self.u, weight)


def block(frame, L, text, f, y, color, alpha, tracking=0.0, lead=1.30):
    rows = []
    for para in text.split("\n"):
        rows += wrap(f, para, L.text_w, tracking) if para else [""]
    step = f.size * lead
    top = y - step * (len(rows) - 1) / 2
    for i, row in enumerate(rows):
        frame.text(row, f, (L.cx, top + i * step), color, alpha,
                   anchor="mm", tracking=tracking)
    return len(rows) * step


# ------------------------------------------------------------- Buehne -------
class Stage:
    """Haelt die bewegten Hintergrundebenen (einmal pro Prozess erzeugt)."""

    def __init__(self, w: int, h: int, gw: int, gh: int):
        self.stars = bd.Starfield(430, seed=5)
        self.dust = bd.Starfield(220, seed=31)
        self.rays = bd.GodRays(15, seed=9)
        self.embers = bd.Embers(150, seed=17)
        self.flow = bd.Flow(gw, gh, seed=23)

    # Stimmung je Szene ------------------------------------------------
    def background(self, fr, L, t):
        warp = (0.25 + 2.9 * smooth(seg(t, T.S_STORM, T.S_STORM + 3.0))
                - 2.0 * smooth(seg(t, T.S_PHIL - 0.6, T.S_PHIL + 1.2))
                + 1.4 * smooth(seg(t, T.S_TWELVE - 0.5, T.S_TWELVE + 1.5))
                - 1.1 * smooth(seg(t, T.S_TWELVE + 2.0, T.S_TWELVE + 5.0))
                + 2.6 * smooth(seg(t, T.S_CLAIM, T.S_CLAIM + 1.6))
                - 2.4 * smooth(seg(t, T.S_EMBLEM, T.S_EMBLEM + 1.2)))
        warp = max(0.12, warp)
        star_gain = (0.30 + 0.70 * smooth(seg(t, T.S_STORM - 1.0, T.S_STORM + 1.0))
                     - 0.45 * smooth(seg(t, T.S_DEBATE, T.S_DEBATE + 1.2))
                     + 0.40 * smooth(seg(t, T.S_TWELVE, T.S_TWELVE + 1.0)))
        self.stars.draw(fr, t, warp, max(0.0, star_gain) * 0.85, WARM, warp=warp * 1.6)
        self.dust.draw(fr, t, 0.12, 0.35, BLUE, warp=0.4)

        ray_gain = (0.55 * smooth(seg(t, T.S_PHIL - 0.5, T.S_PHIL + 1.5))
                    - 0.45 * smooth(seg(t, T.S_DEBATE - 0.5, T.S_DEBATE + 1.0))
                    + 0.75 * smooth(seg(t, T.S_TWELVE, T.S_TWELVE + 2.0))
                    - 0.35 * smooth(seg(t, T.S_CLAIM, T.S_CLAIM + 1.5))
                    + 0.85 * smooth(seg(t, T.S_EMBLEM, T.S_EMBLEM + 0.8)))
        origin = (L.cx, L.y(0.5) if t < T.S_EMBLEM else L.y(EMBLEM_Y))
        self.rays.draw(fr, t, origin, max(0.0, ray_gain), GOLD, length=1.6)

        ember_gain = (0.35 + 0.45 * smooth(seg(t, T.S_PHIL, T.S_PHIL + 2.0))
                      + 0.35 * smooth(seg(t, T.S_CLAIM, T.S_CLAIM + 1.0))
                      - 0.30 * smooth(seg(t, T.S_CTA, T.S_CTA + 1.5)))
        self.embers.draw(fr, t, max(0.0, ember_gain) * 0.55, GOLD)

        # Schockwellen auf den grossen Schlaegen
        for ht in T.BIG_HITS:
            p = (t - ht) / 1.5
            if 0 <= p < 1:
                bd.shockwave(fr, (L.cx, L.y(0.5)), p, 0.55, GOLD_PALE)
        p = (t - T.S_EMBLEM) / 2.2
        if 0 <= p < 1:
            bd.shockwave(fr, (L.cx, L.y(EMBLEM_Y)), p, 1.5, WARM, spread=1.7)
            bd.shockwave(fr, (L.cx, L.y(EMBLEM_Y)), min(1.0, p * 1.5), 0.9, GOLD, spread=1.2)

    def mist(self, t):
        gain = (0.55 + 0.45 * smooth(seg(t, 2.0, 12.0))
                - 0.20 * smooth(seg(t, T.S_EMBLEM, T.S_EMBLEM + 2.0)))
        tint = (0.045, 0.060, 0.150)
        return self.flow.field(t, gain, tint)


# ------------------------------------------------------------ Kamera --------
def camera_params(t: float):
    zoom = bd.punch_at(t, T.BIG_HITS, 0.052, 5.0)
    zoom *= bd.punch_at(t, T.SMALL_HITS, 0.016, 7.0)
    zoom *= bd.punch_at(t, [T.S_EMBLEM], 0.075, 3.2)
    # ruhige Eigenbewegung, je Szene neu ansetzend
    for a, b in ((T.S_INTRO, T.S_STORM), (T.S_STORM, T.S_PHIL), (T.S_PHIL, T.S_DEBATE),
                 (T.S_DEBATE, T.S_TWELVE), (T.S_TWELVE, T.S_CLAIM),
                 (T.S_CLAIM, T.S_EMBLEM), (T.S_EMBLEM, T.END)):
        if a <= t < b:
            zoom *= 1.0 + 0.022 * seg(t, a, b)
            break
    dx, dy = bd.shake_at(t, T.BIG_HITS, 1.0)
    sx, sy = bd.shake_at(t, T.SMALL_HITS, 0.30)
    ex, ey = bd.shake_at(t, [T.S_EMBLEM], 1.9, 5.0)
    return zoom, dx + sx + ex, dy + sy + ey


def exposure(t: float) -> float:
    e = 1.32 * smooth(seg(t, 0.0, 1.2))
    for ht in T.BIG_HITS:
        e += 0.30 * math.exp(-((t - ht - 0.04) / 0.16) ** 2)
    for ht in T.SMALL_HITS:
        e += 0.10 * math.exp(-((t - ht - 0.03) / 0.12) ** 2)
    e += 1.05 * math.exp(-((t - T.S_EMBLEM - 0.05) / 0.22) ** 2)
    e *= 1.0 - 0.30 * smooth(seg(t, T.END - 0.5, T.END))
    return e


# ---------------------------------------------------------------- S1 --------
def scene_intro(fr, L, t):
    if t > T.S_STORM + 1.2:
        return
    u = L.u
    grow = ease_out(seg(t, 0.2, 3.0), 2.0)
    beat = 0.5 + 0.5 * math.sin(t * math.tau / (2 * T.BEAT) - 1.2)
    a = fade(t, 0.2, 1.2, T.S_STORM - 1.0, T.S_STORM + 0.1)
    r = (3.5 + 8.0 * grow) * u * (0.88 + 0.22 * beat)
    pen = fr.pen(GOLD_PALE, glow=1.7, ss=1)
    pen.disc((L.cx, L.y(0.44)), r, a)
    pen.ring((L.cx, L.y(0.44)), r * 4.2 + 30 * u * grow, 1.2 * u, a * 0.28)

    q = fade(t, 1.4, 2.6, T.S_STORM - 1.0, T.S_STORM + 0.05)
    if q > 0:
        f = L.fit("EBGaramond-Italic", 100, 430, T.OPENING, 0.84)
        drift = (1 - ease_out(seg(t, 1.4, 3.6))) * 20 * u
        block(fr, L, T.OPENING, f, L.y(0.60) + drift, WARM, q)


# ---------------------------------------------------------------- S2 --------
def scene_storm(fr, L, t):
    if not (T.S_STORM - 0.6 <= t <= T.S_PHIL + 0.8):
        return
    u = L.u
    for i, (text, beats, side, yf) in enumerate(T.QUESTIONS):
        t0 = T.S_STORM + beats * T.BEAT
        a = fade(t, t0, t0 + 0.45, t0 + 3.6, t0 + 4.6)
        a *= 1.0 - smooth(seg(t, T.S_PHIL - 0.9, T.S_PHIL - 0.1))
        if a <= 0.004:
            continue
        pop = ease_out(seg(t, t0, t0 + 0.55), 2.6)
        size = (52 + 14 * (i % 3)) * (0.78 + 0.22 * pop)
        f = L.fit("EBGaramond-Italic", size, 440, text, 0.82)
        rise = (1 - ease_out(seg(t, t0, t0 + 3.0))) * 30 * u
        x = L.x(side * 230, f.getlength(text))
        fr.text(text, f, (x, L.y(yf) + rise), WARM if i % 2 else GOLD_PALE, a, anchor="mm")


# ---------------------------------------------------------------- S3 --------
def scene_philosophers(fr, L, t):
    if not (T.S_PHIL - 0.5 <= t <= T.S_DEBATE + 0.6):
        return
    u = L.u
    times = T.quote_times()
    for i, ((quote, who), t0) in enumerate(zip(T.QUOTES, times)):
        last = i == len(T.QUOTES) - 1
        hold = T.QUOTE_STEP + (0.9 if last else 0.0)
        a = fade(t, t0, t0 + 0.32, t0 + hold - 0.55, t0 + hold - 0.05)
        if a <= 0.004:
            continue
        prog = ease_out(seg(t, t0, t0 + 0.9), 2.2)
        yf = 0.44 + 0.03 * ((i % 3) - 1)
        fq = L.fit("EBGaramond-Italic", 86, 500, quote, 0.84)
        tr = (26 - 26 * prog) * u
        h = block(fr, L, quote, fq, L.y(yf), WARM, a, tracking=tr, lead=1.24)

        fn = L.fit("Cinzel", 38, 640, who.upper(), 0.70, tracking=11 * u)
        na = fade(t, t0 + 0.30, t0 + 0.75, t0 + hold - 0.55, t0 + hold - 0.05)
        ny = L.y(yf) + h / 2 + 52 * u
        block(fr, L, who.upper(), fn, ny, GOLD, na, tracking=10 * u)
        pen = fr.pen(GOLD, glow=1.2, ss=1)
        half = L.w * 0.05 * ease_out(seg(t, t0 + 0.30, t0 + 0.9))
        pen.line((L.cx - half, ny - 34 * u), (L.cx + half, ny - 34 * u), 1.2 * u, na * 0.8)


# ---------------------------------------------------------------- S4 --------
def _bubble_metrics(L, text):
    f = font("Inter", 46 * L.u, 440)
    rows = wrap(f, text, L.w * 0.56)
    w = max(f.getlength(r) for r in rows)
    lead = f.size * 1.28
    return f, rows, w, len(rows) * lead


def scene_debate(fr, L, t):
    if not (T.S_DEBATE - 0.5 <= t <= T.S_TWELVE + 0.5):
        return
    u = L.u
    times = T.debate_times()
    metrics = [_bubble_metrics(L, txt) for _, txt in T.DEBATE]
    pad_x, pad_y, gap = 42 * u, 30 * u, 30 * u
    heights = [m[3] + 2 * pad_y for m in metrics]

    exit_ = smooth(seg(t, times[-1] + 1.1, times[-1] + 1.9))
    base_y = L.y(0.80) + (1 - ease_out(seg(t, T.S_DEBATE, T.S_DEBATE + 0.6))) * 40 * u

    for i, ((side, text), t0) in enumerate(zip(T.DEBATE, times)):
        appear = smooth(seg(t, t0 + 0.12, t0 + 0.42))
        if appear <= 0.004:
            continue
        # alles darunter schiebt die Aelteren nach oben
        push = sum((heights[j] + gap) * smooth(seg(t, times[j] - 0.04, times[j] + 0.22))
                   for j in range(i + 1, len(T.DEBATE)))
        f, rows, tw, th = metrics[i]
        h = heights[i]
        drop = (1 - ease_out(seg(t, t0 + 0.12, t0 + 0.5), 2.4)) * 46 * u
        slide = (1 - ease_out(seg(t, t0 + 0.12, t0 + 0.55), 2.6)) * 70 * u * side
        y_bottom = base_y - push - 120 * u * exit_ + drop
        y_top = y_bottom - h
        depth = push / max(1.0, (heights[0] + gap))
        alpha = appear * max(0.0, 1.0 - 0.17 * depth) * (1 - exit_)
        if alpha <= 0.01:
            continue
        bw = tw + 2 * pad_x
        x0 = (L.w * 0.08 if side < 0 else L.w * 0.92 - bw) + slide
        color = GOLD if side < 0 else BLUE
        fr.soft(color, 0.30).rounded_rect((x0, y_top, x0 + bw, y_bottom),
                                          24 * u, 26 * u, alpha * 0.5)
        fr.pen(color, glow=1.1).rounded_rect((x0, y_top, x0 + bw, y_bottom),
                                             24 * u, 1.8 * u, alpha * 0.9)
        for k, row in enumerate(rows):
            fr.text(row, f, (x0 + pad_x, y_top + pad_y + f.size * 1.28 * (k + 0.5)),
                    WARM, alpha, anchor="lm")
        fr.pen(color, glow=1.4, ss=1).disc((x0 + (-10 * u if side < 0 else bw + 10 * u),
                                            y_top + pad_y + f.size * 0.64), 4.0 * u, alpha)

    closer = fade(t, times[-1] + 1.5, times[-1] + 2.1, T.S_TWELVE - 0.5, T.S_TWELVE + 0.1)
    if closer > 0:
        f = L.fit("Cinzel", 56, 680, T.DEBATE_CLOSER, 0.86, tracking=10 * u)
        block(fr, L, T.DEBATE_CLOSER, f, L.y(0.48), GOLD_PALE, closer, tracking=10 * u)


# ---------------------------------------------------------------- S5 --------
LINKS = [(0, 5), (1, 7), (2, 9), (3, 11), (4, 8), (6, 10), (0, 6), (2, 5),
         (1, 4), (7, 11), (3, 8), (9, 0), (10, 2)]


def ring_geometry(L, t):
    spin = math.radians(-90 + 2.0 * math.sin(t * 0.16))
    pull = smooth(seg(t, T.S_EMBLEM, T.S_EMBLEM + 0.9))
    zoom_in = 1.0 + 0.10 * (1 - ease_out(seg(t, T.S_TWELVE, T.S_TWELVE + 4.0), 2.0))
    r = RING_R * L.u * zoom_in * (1 - 0.74 * pull)
    cy = L.y(0.47) + (L.y(EMBLEM_Y) - L.y(0.47)) * pull
    return (L.cx, cy), r, spin, pull


def sym_positions(L, t):
    c, r, spin, pull = ring_geometry(L, t)
    n = len(symbols.ORDER)
    pts = [(c[0] + r * math.cos(spin + i * math.tau / n),
            c[1] + r * math.sin(spin + i * math.tau / n)) for i in range(n)]
    return pts, c, r, pull


def scene_twelve(fr, L, t):
    if t < T.S_TWELVE - 0.5:
        return
    u = L.u
    pts, c, r, pull = sym_positions(L, t)
    presence = 1.0
    if t >= T.S_CLAIM:
        presence = 1.0 - 0.86 * smooth(seg(t, T.S_CLAIM, T.S_CLAIM + 0.9))
    if pull > 0:
        presence = max(presence, 0.16 + 0.5 * pull)

    draw = ease_in(seg(t, T.S_TWELVE + 0.1, T.S_TWELVE + 1.15), 1.3)
    if draw > 0:
        pen = fr.pen(GOLD, glow=1.1)
        pen.arc(c, r, -90, -90 + 360 * draw, 2.2 * u, 0.95 * presence)
        if draw < 1:
            ang = math.radians(-90 + 360 * draw)
            fr.pen(WARM, glow=1.9, ss=1).disc(
                (c[0] + r * math.cos(ang), c[1] + r * math.sin(ang)), 5.5 * u, 1.0)

    sym_r = 58 * u * (1 - 0.5 * pull)
    for i, name in enumerate(symbols.ORDER):
        t0 = T.S_TWELVE + 1.15 + i * 0.30
        app = ease_out(seg(t, t0, t0 + 0.55), 2.4)
        if app <= 0.004:
            continue
        a = app * presence * max(0.0, 1 - 2.4 * pull)
        symbols.draw(fr, name, pts[i], sym_r * (0.7 + 0.3 * app), 2.5 * u, a, GOLD_PALE)
        if app < 1:
            fr.pen(WARM, glow=2.0, ss=1).disc(pts[i], sym_r * 0.3 * (1 - app) + 2 * u,
                                              (1 - app) * 0.9)

    for k, (a_i, b_i) in enumerate(LINKS):
        t0 = T.S_TWELVE + 4.3 + k * 0.16
        grow = ease_out(seg(t, t0, t0 + 0.55), 2.0)
        if grow <= 0.004:
            continue
        p0, p1 = pts[a_i], pts[b_i]
        tip = (p0[0] + (p1[0] - p0[0]) * grow, p0[1] + (p1[1] - p0[1]) * grow)
        fr.pen(BLUE, glow=0.7, ss=1).line(p0, tip, 1.2 * u, 0.42 * presence * (1 - pull))
        if grow >= 1 and pull < 0.3:
            phase = ((t - t0) * 0.5 + k * 0.11) % 1.0
            mp = (p0[0] + (p1[0] - p0[0]) * phase, p0[1] + (p1[1] - p0[1]) * phase)
            fr.pen(TEAL, glow=1.8, ss=1).disc(mp, 3.4 * u, 0.9 * presence * (1 - pull))

    cap = fade(t, T.S_TWELVE + 7.0, T.S_TWELVE + 7.6, T.S_CLAIM - 0.35, T.S_CLAIM + 0.1)
    if cap > 0:
        f = L.fit("Cinzel", 48, 640, T.CAPTION_TWELVE, 0.84, tracking=13 * u)
        block(fr, L, T.CAPTION_TWELVE, f, L.y(0.90), GOLD_PALE, cap, tracking=13 * u)


# ---------------------------------------------------------------- S6 --------
def scene_claim(fr, L, t):
    if not (T.S_CLAIM - 0.4 <= t <= T.S_EMBLEM + 0.3):
        return
    u = L.u
    a1 = fade(t, T.S_CLAIM + 0.15, T.S_CLAIM + 0.6, T.S_EMBLEM - 0.5, T.S_EMBLEM - 0.05)
    if a1 <= 0.004:
        return
    big = L.fit("Cinzel", 88, 720, "HIER WIRD", 0.60, tracking=8 * u)
    rows_a = wrap(big, T.CLAIM_A, L.text_w, 8 * u)
    step = big.size * 1.20
    top = L.y(0.44) - (len(rows_a) * step + step) / 2
    rise = (1 - ease_out(seg(t, T.S_CLAIM + 0.15, T.S_CLAIM + 1.0), 2.6)) * 26 * u
    for i, row in enumerate(rows_a):
        fr.text(row, big, (L.cx, top + i * step + rise), WARM, a1, anchor="mm",
                tracking=8 * u)
    a2 = fade(t, T.S_CLAIM + 1.75, T.S_CLAIM + 2.15, T.S_EMBLEM - 0.5, T.S_EMBLEM - 0.05)
    y2 = top + len(rows_a) * step + step * 0.24
    pop = 1.0 + 0.06 * math.exp(-((t - T.S_CLAIM - 1.85) / 0.18) ** 2)
    fr.text(T.CLAIM_B, L.fit("Cinzel", 88 * pop, 720, T.CLAIM_B, 0.72, tracking=8 * u),
            (L.cx, y2), GOLD, a2, anchor="mm", tracking=8 * u)
    a3 = fade(t, T.S_CLAIM + 3.3, T.S_CLAIM + 3.8, T.S_EMBLEM - 0.5, T.S_EMBLEM - 0.05)
    if a3 > 0:
        f = L.fit("Inter", 40, 380, T.CLAIM_SUB, 0.80)
        block(fr, L, T.CLAIM_SUB, f, y2 + step * 1.05, DIM, a3)


# ---------------------------------------------------------------- S7 --------
def emblem(fr, L, t, alpha):
    if alpha <= 0.004:
        return
    u = L.u
    cx, cy = L.cx, L.y(EMBLEM_Y)
    R = 100 * u
    close = ease_out(seg(t, T.S_EMBLEM + 0.1, T.S_EMBLEM + 1.1), 2.4)
    off = (1 - close) * 110 * u + R * 0.42
    pen = fr.pen(GOLD, glow=1.3)
    pen.ring((cx - off, cy), R, 2.0 * u, alpha * 0.92)
    pen.ring((cx + off, cy), R, 2.0 * u, alpha * 0.92)
    pen.ring((cx, cy), R * 1.66, 1.1 * u, alpha * 0.38)
    fr.pen(GOLD_PALE, glow=2.0, ss=1).disc((cx, cy), 5.5 * u * (0.6 + 0.4 * close),
                                           alpha * close)
    for i in range(len(symbols.ORDER)):
        ang = -math.pi / 2 + i * math.tau / len(symbols.ORDER)
        rr = R * 1.66
        fr.pen(GOLD, glow=1.1, ss=1).disc((cx + rr * math.cos(ang), cy + rr * math.sin(ang)),
                                          2.4 * u, alpha * 0.6 * close)


def scene_emblem(fr, L, t):
    if t < T.S_EMBLEM - 0.2:
        return
    u = L.u
    flash = math.exp(-((t - T.S_EMBLEM - 0.05) / 0.24) ** 2)
    if flash > 0.01:
        fr.pen(WARM, glow=2.0, ss=1).disc((L.cx, L.y(EMBLEM_Y)),
                                          40 * u * (0.5 + 0.9 * flash), 0.5 * flash)
    emb = fade(t, T.S_EMBLEM + 0.1, T.S_EMBLEM + 0.7, T.END + 9, T.END + 9)
    emblem(fr, L, t, emb)

    ta = fade(t, T.S_EMBLEM + 0.75, T.S_EMBLEM + 1.5, T.END + 9, T.END + 9)
    if ta > 0:
        prog = ease_out(seg(t, T.S_EMBLEM + 0.75, T.S_EMBLEM + 2.2), 2.4)
        tr = (56 - 42 * prog) * u
        if L.tall:
            f = L.fit("Cinzel", 76, 660, "RELIGIONEN", 0.80, tracking=tr)
            block(fr, L, "DIALOG DER\nRELIGIONEN", f, L.y(0.455), WARM, ta,
                  tracking=tr, lead=1.22)
        else:
            f = L.fit("Cinzel", 76, 660, T.TITLE, 0.86, tracking=tr)
            block(fr, L, T.TITLE, f, L.y(0.455), WARM, ta, tracking=tr, lead=1.22)

    ln = fade(t, T.S_EMBLEM + 1.8, T.S_EMBLEM + 2.1, T.END + 9, T.END + 9)
    if ln > 0:
        half = L.w * 0.17 * ease_out(seg(t, T.S_EMBLEM + 1.8, T.S_EMBLEM + 2.7), 2.0)
        y = L.y(0.525)
        fr.pen(GOLD, glow=1.1, ss=1).line((L.cx - half, y), (L.cx + half, y), 1.4 * u, 0.8)

    sa = fade(t, T.S_EMBLEM + 2.1, T.S_EMBLEM + 2.7, T.END + 9, T.END + 9)
    if sa > 0:
        f = L.fit("Inter", 36, 380, T.SUBTITLE, 0.82)
        block(fr, L, T.SUBTITLE, f, L.y(0.585), DIM, sa)


# ---------------------------------------------------------------- S8 --------
def scene_cta(fr, L, t):
    if t < T.S_CTA - 0.6:
        return
    u = L.u
    a = fade(t, T.S_CTA - 0.35, T.S_CTA + 0.35, T.END + 9, T.END + 9)
    if a > 0:
        f = L.fit("Inter", 46, 620, T.LINK + "aaaa", 0.84)
        tw = f.getlength(T.LINK)
        pad_x, pad_y = 56 * u, 32 * u
        y = L.y(0.715) + (1 - ease_out(seg(t, T.S_CTA - 0.35, T.S_CTA + 0.5), 2.6)) * 30 * u
        box = (L.cx - tw / 2 - pad_x, y - pad_y - 6 * u,
               L.cx + tw / 2 + pad_x, y + pad_y + 6 * u)
        breath = 0.70 + 0.30 * (0.5 + 0.5 * math.sin((t - T.S_CTA) * 2.6))
        fr.pen(GOLD, glow=1.7).rounded_rect(box, 42 * u, 2.2 * u, a * breath)
        fr.text(T.LINK, f, (L.cx, y), GOLD_PALE, a, anchor="mm")

    b = fade(t, T.S_CTA + 0.7, T.S_CTA + 1.3, T.END + 9, T.END + 9)
    if b > 0:
        f = L.fit("EBGaramond-Italic", 56, 450, T.CTA_LINE, 0.84)
        block(fr, L, T.CTA_LINE, f, L.y(0.83), WARM, b)

    c = fade(t, T.S_CTA + 1.5, T.S_CTA + 2.1, T.END + 9, T.END + 9)
    if c > 0:
        f = L.fit("Inter", 26, 400, T.FEATURE_LINE, 0.88)
        block(fr, L, T.FEATURE_LINE, f, L.y(0.925), DIM, c * 0.85)


def render(fr, L, t, stage: Stage | None = None):
    if stage is not None:
        stage.background(fr, L, t)
    scene_intro(fr, L, t)
    scene_storm(fr, L, t)
    scene_philosophers(fr, L, t)
    scene_debate(fr, L, t)
    scene_twelve(fr, L, t)
    scene_claim(fr, L, t)
    scene_emblem(fr, L, t)
    scene_cta(fr, L, t)
