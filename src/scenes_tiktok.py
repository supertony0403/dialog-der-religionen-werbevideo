"""Storyboard der TikTok-Fassung.

Alles Wichtige liegt im sicheren Bereich zwischen TikToks Oberflaeche: oben
Statusleiste und Name, rechts die Buttons, unten Caption und Menue. Der Rest
ist Tempo - auf jeden Schlag passiert etwas.
"""
from __future__ import annotations

import math

import backdrops as bd
import symbols
import timing_tiktok as T
from core import (BLUE, DIM, GOLD, GOLD_PALE, TEAL, VIOLET, WARM, ease_in,
                  ease_out, fade, font, seg, smooth, wrap)


class Layout:
    """Sicherer Bereich: y(0) oben, y(1) unten - dazwischen ist alles sichtbar."""

    TOP, BOTTOM = 0.115, 0.760

    def __init__(self, frame):
        self.f = frame
        self.w, self.h, self.u = frame.w, frame.h, frame.u
        self.cx = frame.cx
        self.tall = frame.h > frame.w
        self.text_w = self.w * 0.84
        if not self.tall:                      # Vorschau im Querformat
            self.TOP, self.BOTTOM = 0.10, 0.92

    def y(self, u: float) -> float:
        return self.h * (self.TOP + (self.BOTTOM - self.TOP) * u)

    def fit(self, name: str, size: float, weight: int, text: str,
            max_frac: float = 0.86, tracking: float = 0.0):
        limit = self.w * max_frac
        for _ in range(18):
            f = font(name, size * self.u, weight)
            w = sum(f.getlength(ch) for ch in text) + tracking * max(0, len(text) - 1)
            if w <= limit or size < 10:
                return f
            size *= 0.94
        return font(name, size * self.u, weight)


def block(frame, L, text, f, y, color, alpha, tracking=0.0, lead=1.16):
    rows = []
    for para in text.split("\n"):
        rows += wrap(f, para, L.text_w, tracking) if para else [""]
    step = f.size * lead
    top = y - step * (len(rows) - 1) / 2
    for i, row in enumerate(rows):
        frame.text(row, f, (L.cx, top + i * step), color, alpha, anchor="mm",
                   tracking=tracking)
    return len(rows) * step


# ------------------------------------------------------------- Buehne -------
class Stage:
    def __init__(self, w: int, h: int, gw: int, gh: int):
        self.stars = bd.Starfield(360, seed=5)
        self.dust = bd.Starfield(180, seed=31)
        self.rays = bd.GodRays(13, seed=9)
        self.embers = bd.Embers(120, seed=17)
        self.flow = bd.Flow(gw, gh, seed=23)

    def background(self, fr, L, t):
        warp = (0.5 + 2.4 * smooth(seg(t, T.S_HOOK, T.S_HOOK + 1.2))
                - 1.9 * smooth(seg(t, T.S_CHAT - 0.3, T.S_CHAT + 0.6))
                + 2.8 * smooth(seg(t, T.S_FACTS - 0.4, T.S_FACTS + 0.8))
                - 1.6 * smooth(seg(t, T.S_CIRCLE, T.S_CIRCLE + 1.0))
                + 2.2 * smooth(seg(t, T.S_DROP - 0.5, T.S_DROP + 0.3))
                - 2.4 * smooth(seg(t, T.S_DROP + 0.5, T.S_DROP + 1.6)))
        self.stars.draw(fr, t, max(0.15, warp), 0.85, WARM, warp=max(0.2, warp) * 1.7)
        self.dust.draw(fr, t, 0.15, 0.32, BLUE, warp=0.4)

        rays = (0.35 + 0.5 * smooth(seg(t, T.S_FACTS, T.S_FACTS + 1.0))
                + 0.9 * smooth(seg(t, T.S_DROP, T.S_DROP + 0.6))
                - 0.4 * smooth(seg(t, T.S_CHAT, T.S_CHAT + 0.8)))
        origin = (L.cx, L.y(0.30) if t < T.S_DROP else L.y(0.22))
        self.rays.draw(fr, t, origin, max(0.0, rays), GOLD, length=1.6)
        self.embers.draw(fr, t, 0.45 + 0.35 * smooth(seg(t, T.S_DROP, T.S_DROP + 1.0)), GOLD)

        for ht in T.BIG_HITS:
            p = (t - ht) / 1.1
            if 0 <= p < 1:
                bd.shockwave(fr, (L.cx, L.y(0.42)), p, 0.55, GOLD_PALE)
        p = (t - T.S_DROP) / 1.8
        if 0 <= p < 1:
            bd.shockwave(fr, (L.cx, L.y(0.26)), p, 1.6, WARM, spread=1.8)
            bd.shockwave(fr, (L.cx, L.y(0.26)), min(1.0, p * 1.6), 0.9, GOLD, spread=1.2)

    def mist(self, t):
        gain = 0.55 + 0.35 * smooth(seg(t, 1.0, 10.0))
        return self.flow.field(t, gain, (0.045, 0.060, 0.150))


def camera_params(t: float):
    zoom = bd.punch_at(t, T.BIG_HITS, 0.055, 5.5)
    zoom *= bd.punch_at(t, T.SMALL_HITS, 0.022, 8.0)
    zoom *= bd.punch_at(t, [T.S_DROP], 0.085, 3.4)
    zoom *= 1.0 + 0.020 * seg(t, T.S_CIRCLE, T.S_DROP)
    dx, dy = bd.shake_at(t, T.BIG_HITS, 0.9)
    sx, sy = bd.shake_at(t, T.SMALL_HITS, 0.28)
    ex, ey = bd.shake_at(t, [T.S_DROP], 1.8, 5.0)
    return zoom, dx + sx + ex, dy + sy + ey


def exposure(t: float) -> float:
    e = 1.34 * smooth(seg(t, 0.0, 0.25))
    for ht in T.BIG_HITS:
        e += 0.26 * math.exp(-((t - ht - 0.03) / 0.14) ** 2)
    for ht in T.SMALL_HITS:
        e += 0.12 * math.exp(-((t - ht - 0.03) / 0.10) ** 2)
    e += 1.0 * math.exp(-((t - T.S_DROP - 0.04) / 0.20) ** 2)
    return e


# ---------------------------------------------------------------- Haken -----
def scene_hook(fr, L, t):
    if t > T.S_CHAT + 0.4:
        return
    u = L.u
    out = 1.0 - smooth(seg(t, T.S_CHAT - 0.45, T.S_CHAT + 0.1))
    step = 118 * u
    for i, (word, off) in enumerate(T.HOOK_WORDS):
        t0 = T.S_HOOK + off
        a = fade(t, t0, t0 + 0.12, T.S_CHAT, T.S_CHAT + 0.2) * out
        if a <= 0.004:
            continue
        pop = ease_out(seg(t, t0, t0 + 0.22), 2.6)
        f = L.fit("Cinzel", 84 * (0.86 + 0.14 * pop), 720, word, 0.88, tracking=3 * u)
        col = (WARM, GOLD_PALE, BLUE)[i]
        if pop < 1:
            fr.pen(col, glow=1.6, ss=1).ring((L.cx, L.y(0.15) + i * step),
                                             (60 + 260 * pop) * u, 2.0 * u * (1 - pop),
                                             (1 - pop) * 0.5)
        fr.text(word, f, (L.cx, L.y(0.15) + i * step), col, a, anchor="mm",
                tracking=3 * u)

    tw = fade(t, T.S_HOOK + 1.55, T.S_HOOK + 1.70, T.S_CHAT, T.S_CHAT + 0.2) * out
    if tw > 0:
        pop = ease_out(seg(t, T.S_HOOK + 1.55, T.S_HOOK + 1.85), 2.4)
        f = L.fit("Cinzel", 96 * (0.80 + 0.20 * pop), 760, T.HOOK_TWIST, 0.86,
                  tracking=6 * u)
        fr.text(T.HOOK_TWIST, f, (L.cx, L.y(0.53)), GOLD, tw, anchor="mm", tracking=6 * u)
        half = L.w * 0.30 * ease_out(seg(t, T.S_HOOK + 1.6, T.S_HOOK + 2.0))
        fr.pen(GOLD, glow=1.3, ss=1).line((L.cx - half, L.y(0.61)),
                                          (L.cx + half, L.y(0.61)), 2.2 * u, tw * 0.85)

    pn = fade(t, T.S_HOOK + 2.3, T.S_HOOK + 2.45, T.S_CHAT - 0.1, T.S_CHAT + 0.2) * out
    if pn > 0:
        pop = ease_out(seg(t, T.S_HOOK + 2.3, T.S_HOOK + 2.7), 2.2)
        f = L.fit("Inter", 62 * (0.88 + 0.12 * pop), 800, "UND KEINER", 0.80)
        block(fr, L, T.HOOK_PUNCH, f, L.y(0.73), WARM, pn, lead=1.14)


# ----------------------------------------------------------------- Chat -----
def _metrics(L, text):
    f = font("Inter", 50 * L.u, 500)
    rows = wrap(f, text, L.w * 0.62)
    w = max(f.getlength(r) for r in rows)
    return f, rows, w, len(rows) * f.size * 1.26


def scene_chat(fr, L, t):
    if not (T.S_CHAT - 0.3 <= t <= T.S_FACTS + 0.3):
        return
    u = L.u
    times = T.chat_times()
    metrics = [_metrics(L, txt) for _, txt, _ in T.CHAT]
    pad_x, pad_y, gap = 34 * u, 24 * u, 20 * u
    heights = [m[3] + 2 * pad_y for m in metrics]
    exit_ = smooth(seg(t, times[-1] + 0.85, times[-1] + 1.35))
    base_y = L.y(0.90)

    for i, ((side, text, _), t0) in enumerate(zip(T.CHAT, times)):
        appear = smooth(seg(t, t0 + 0.06, t0 + 0.24))
        if appear <= 0.004:
            continue
        push = sum((heights[j] + gap) * smooth(seg(t, times[j] - 0.02, times[j] + 0.16))
                   for j in range(i + 1, len(T.CHAT)))
        f, rows, tw, th = metrics[i]
        h = heights[i]
        drop = (1 - ease_out(seg(t, t0 + 0.06, t0 + 0.30), 2.4)) * 40 * u
        slide = (1 - ease_out(seg(t, t0 + 0.06, t0 + 0.34), 2.6)) * 60 * u * side
        y_bottom = base_y - push + drop - 150 * u * exit_
        y_top = y_bottom - h
        depth = push / max(1.0, heights[0] + gap)
        alpha = appear * max(0.0, 1.0 - 0.16 * depth) * (1 - exit_)
        if alpha <= 0.01:
            continue
        bw = tw + 2 * pad_x
        x0 = (L.w * 0.06 if side < 0 else L.w * 0.94 - bw) + slide
        color = GOLD if side < 0 else BLUE
        fr.soft(color, 0.34).rounded_rect((x0, y_top, x0 + bw, y_bottom), 24 * u,
                                          26 * u, alpha * 0.55)
        fr.pen(color, glow=1.1).rounded_rect((x0, y_top, x0 + bw, y_bottom),
                                             24 * u, 2.0 * u, alpha * 0.95)
        for k, row in enumerate(rows):
            fr.text(row, f, (x0 + pad_x, y_top + pad_y + f.size * 1.26 * (k + 0.5)),
                    WARM, alpha, anchor="lm")

    closer = fade(t, times[-1] + 1.45, times[-1] + 1.70, T.S_FACTS - 0.45, T.S_FACTS - 0.05)
    if closer > 0:
        f = L.fit("Cinzel", 72, 700, "SO REDEN WIR HIER.", 0.86, tracking=5 * u)
        block(fr, L, T.CHAT_CLOSER, f, L.y(0.42), GOLD_PALE, closer, tracking=5 * u)


# --------------------------------------------------------------- Fakten -----
def scene_facts(fr, L, t):
    if not (T.S_FACTS - 0.3 <= t <= T.S_CIRCLE + 0.4):
        return
    u = L.u
    times = T.fact_times()
    for i, ((big, small), t0) in enumerate(zip(T.FACTS, times)):
        last = i == len(T.FACTS) - 1
        hold = (T.S_CIRCLE - t0) if last else (times[i + 1] - t0)
        a = fade(t, t0, t0 + 0.10, t0 + hold - 0.14, t0 + hold + 0.02)
        if a <= 0.004:
            continue
        pop = ease_out(seg(t, t0, t0 + 0.26), 2.8)
        shown = big
        if big.isdigit() and int(big) > 0:
            count = ease_out(seg(t, t0, t0 + 0.34), 2.0)
            shown = str(max(1, int(round(int(big) * count))))
        fb = L.fit("Cinzel", 190 * (0.82 + 0.18 * pop), 800, shown, 0.84, tracking=4 * u)
        fr.text(shown, fb, (L.cx, L.y(0.34)), (GOLD, WARM, TEAL, VIOLET)[i % 4], a,
                anchor="mm", tracking=4 * u)
        fs = L.fit("Inter", 52, 520, small, 0.86)
        block(fr, L, small, fs, L.y(0.52), WARM, a)


# --------------------------------------------------------- Zwoelf Zeichen ---
def scene_circle(fr, L, t):
    if not (T.S_CIRCLE - 0.3 <= t <= T.S_DROP + 0.8):
        return
    u = L.u
    n = len(symbols.ORDER)
    pull = smooth(seg(t, T.S_DROP, T.S_DROP + 0.55))
    c = (L.cx, L.y(0.36) + (L.y(0.20) - L.y(0.36)) * pull)
    R = 300 * u * (1 - 0.72 * pull)
    spin = math.radians(-90) + 0.35 * ease_out(seg(t, T.S_CIRCLE, T.S_DROP), 1.6)
    ring = ease_in(seg(t, T.S_CIRCLE, T.S_CIRCLE + 0.5), 1.2)
    pres = 1.0 - 0.75 * pull
    if ring > 0:
        fr.pen(GOLD, glow=1.2).arc(c, R, -90, -90 + 360 * ring, 2.6 * u, 0.95 * pres)

    for i, name in enumerate(symbols.ORDER):
        t0 = T.S_CIRCLE + 0.20 + i * 0.075
        app = ease_out(seg(t, t0, t0 + 0.32), 2.4)
        if app <= 0.004:
            continue
        ang = spin + i * math.tau / n
        # fliegt von aussen herein
        rr = R * (1 + 1.35 * (1 - app))
        p = (c[0] + rr * math.cos(ang), c[1] + rr * math.sin(ang))
        a = app * pres * max(0.0, 1 - 2.2 * pull)
        symbols.draw(fr, name, p, 52 * u * (0.6 + 0.4 * app) * (1 - 0.4 * pull),
                     2.6 * u, a, GOLD_PALE)
        if app < 1:
            fr.pen(WARM, glow=2.0, ss=1).disc(p, 22 * u * (1 - app) + 2 * u, (1 - app))

    cap = fade(t, T.S_CIRCLE + 1.15, T.S_CIRCLE + 1.35, T.S_DROP - 0.25, T.S_DROP)
    if cap > 0:
        txt = "ZWÖLF WEGE · EIN TISCH"
        f = L.fit("Cinzel", 52, 680, txt, 0.90, tracking=6 * u)
        block(fr, L, txt, f, L.y(0.68), GOLD_PALE, cap, tracking=6 * u)


# ----------------------------------------------------------------- Drop -----
def emblem(fr, L, t, alpha):
    if alpha <= 0.004:
        return
    u = L.u
    cx, cy = L.cx, L.y(0.20)
    R = 92 * u
    close = ease_out(seg(t, T.S_DROP, T.S_DROP + 0.6), 2.4)
    off = (1 - close) * 120 * u + R * 0.42
    pen = fr.pen(GOLD, glow=1.4)
    pen.ring((cx - off, cy), R, 2.4 * u, alpha * 0.92)
    pen.ring((cx + off, cy), R, 2.4 * u, alpha * 0.92)
    pen.ring((cx, cy), R * 1.62, 1.3 * u, alpha * 0.40)
    fr.pen(GOLD_PALE, glow=2.1, ss=1).disc((cx, cy), 6.0 * u * (0.6 + 0.4 * close),
                                           alpha * close)


def scene_drop(fr, L, t):
    if t < T.S_DROP - 0.2:
        return
    u = L.u
    flash = math.exp(-((t - T.S_DROP - 0.03) / 0.20) ** 2)
    if flash > 0.01:
        fr.pen(WARM, glow=2.0, ss=1).disc((L.cx, L.y(0.20)),
                                          46 * u * (0.5 + 0.9 * flash), 0.5 * flash)
    loop_out = 1.0 - smooth(seg(t, T.END - 0.75, T.END - 0.35))
    emb = fade(t, T.S_DROP + 0.05, T.S_DROP + 0.4, T.END + 9, T.END + 9) * loop_out
    emblem(fr, L, t, emb)

    ta = fade(t, T.S_DROP + 0.35, T.S_DROP + 0.65, T.END + 9, T.END + 9) * loop_out
    if ta > 0:
        prog = ease_out(seg(t, T.S_DROP + 0.35, T.S_DROP + 1.2), 2.4)
        tr = (42 - 32 * prog) * u
        f = L.fit("Cinzel", 82, 700, "RELIGIONEN", 0.84, tracking=tr)
        block(fr, L, "DIALOG DER\nRELIGIONEN", f, L.y(0.42), WARM, ta,
              tracking=tr, lead=1.18)


# ------------------------------------------------------------ Einladung -----
def scene_cta(fr, L, t):
    if t < T.S_CTA - 0.5:
        return
    u = L.u
    loop_out = 1.0 - smooth(seg(t, T.END - 0.75, T.END - 0.35))
    a = fade(t, T.S_CTA - 0.25, T.S_CTA + 0.15, T.END + 9, T.END + 9) * loop_out
    if a > 0:
        f = L.fit("Inter", 54, 680, T.LINK + "aa", 0.88)
        tw = f.getlength(T.LINK)
        pad_x, pad_y = 44 * u, 30 * u
        y = L.y(0.60) + (1 - ease_out(seg(t, T.S_CTA - 0.25, T.S_CTA + 0.3), 2.6)) * 30 * u
        box = (L.cx - tw / 2 - pad_x, y - pad_y - 6 * u,
               L.cx + tw / 2 + pad_x, y + pad_y + 6 * u)
        breath = 0.68 + 0.32 * (0.5 + 0.5 * math.sin((t - T.S_CTA) * 5.0))
        fr.soft(GOLD, 0.30).rounded_rect(box, 40 * u, 30 * u, a * 0.5)
        fr.pen(GOLD, glow=1.8).rounded_rect(box, 40 * u, 2.6 * u, a * breath)
        fr.text(T.LINK, f, (L.cx, y), GOLD_PALE, a, anchor="mm")

    b = fade(t, T.S_CTA + 0.45, T.S_CTA + 0.8, T.END + 9, T.END + 9) * loop_out
    if b > 0:
        f = L.fit("EBGaramond-Italic", 58, 480, T.CTA_LINE, 0.86)
        block(fr, L, T.CTA_LINE, f, L.y(0.72), WARM, b)

    # Schluss fuehrt zurueck zum Anfang, damit die Schleife sauber laeuft
    lp = fade(t, T.END - 0.6, T.END - 0.35, T.END, T.END)
    if lp > 0:
        f = L.fit("Cinzel", 70, 720, "ATHEISTEN.", 0.86, tracking=3 * u)
        block(fr, L, T.LOOP_LINE, f, L.y(0.30), WARM, lp, tracking=3 * u, lead=1.20)


def render(fr, L, t, stage: Stage | None = None):
    if stage is not None:
        stage.background(fr, L, t)
    scene_hook(fr, L, t)
    scene_chat(fr, L, t)
    scene_facts(fr, L, t)
    scene_circle(fr, L, t)
    scene_drop(fr, L, t)
    scene_cta(fr, L, t)
