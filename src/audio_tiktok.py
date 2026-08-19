"""Soundtrack der TikTok-Fassung - 120 BPM, druckvoll, ohne Ohrenschmerzen.

Der Aufbau folgt der Aufmerksamkeitskurve: Haken mit Sub-Schlag, treibender
Beat unter dem Chat, Verdichtung zu den Fakten, Drop beim Emblem, offener
Ausklang. Hoehen sind hart gedeckelt (Tiefpass ~11 kHz), Zischeln gibt es
keins - laut wird das Stueck ueber Bass und Trommeln, nicht ueber Schaerfe.
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path

import numpy as np

import timing_tiktok as T
from audio import (SR, bell, braam, choir, eq, impact, lowpass, note, place,
                   reverb, riser, saw_stack, stab, taiko, write_wav)

BEAT, BAR = T.BEAT, T.BAR
DURATION = T.END

PROGRESSION = ["D", "D", "A#", "A#", "F", "F", "G", "G", "A#", "F", "F", "A#", "C"]
TRIADS = {
    "D": [("D", 3), ("F", 3), ("A", 3)],
    "A#": [("A#", 2), ("D", 3), ("F", 3)],
    "F": [("F", 2), ("A", 3), ("C", 4)],
    "C": [("C", 3), ("E", 3), ("G", 3)],
    "G": [("G", 2), ("A#", 3), ("D", 4)],
}


def _t(n: int) -> np.ndarray:
    return np.arange(n, dtype=np.float64) / SR


def clap(dur: float = 0.5, seed: int = 3) -> np.ndarray:
    """Trockener Klatscher aus drei versetzten Rauschstoessen."""
    n = int(dur * SR)
    rng = np.random.default_rng(seed)
    t = _t(n)
    out = np.zeros(n)
    for k, off in enumerate((0.0, 0.011, 0.023)):
        i = int(off * SR)
        seg_ = rng.normal(0, 1, n - i) * np.exp(-(t[: n - i]) * (52 - 8 * k))
        out[i:] += seg_ * (1.0 - 0.22 * k)
    body = lowpass(out, 3400)
    return body - lowpass(body, 420)          # Bandpass: kein Dröhnen, kein Zischen


def hat(dur: float = 0.10, seed: int = 5, open_: bool = False) -> np.ndarray:
    n = int(dur * SR)
    rng = np.random.default_rng(seed)
    t = _t(n)
    x = rng.normal(0, 1, n) * np.exp(-t * (26 if open_ else 95))
    x = lowpass(x, 9000)
    return x - lowpass(x, 3600)


def sub_hit(dur: float = 1.1, f0: float = 78, f1: float = 33) -> np.ndarray:
    n = int(dur * SR)
    t = _t(n)
    f = f1 + (f0 - f1) * np.exp(-t * 7.0)
    return np.sin(2 * math.pi * np.cumsum(f) / SR) * np.exp(-t * 2.2)


def blip(freq: float, dur: float = 0.22) -> np.ndarray:
    """Kurzer Ton fuer jede Chat-Nachricht."""
    n = int(dur * SR)
    t = _t(n)
    x = np.sin(2 * math.pi * freq * t) + 0.4 * np.sin(2 * math.pi * freq * 2 * t)
    return lowpass(x * np.exp(-t * 26), 5200)


def chord_at(t: float):
    return TRIADS[PROGRESSION[min(len(PROGRESSION) - 1, max(0, int(t / BAR)))]]


def build() -> np.ndarray:
    n = int(DURATION * SR)
    pad = np.zeros(n)
    low = np.zeros(n)
    drum = np.zeros(n)
    fx = np.zeros(n)

    # Flaeche: Chor je Takt
    for b, name in enumerate(PROGRESSION):
        at = b * BAR
        if at >= DURATION:
            break
        loud = 0.26
        if at < T.S_CHAT:
            loud = 0.20
        if at >= T.S_FACTS:
            loud = 0.34
        if at >= T.S_DROP:
            loud = 0.52
        if at >= T.END - BAR:
            loud = 0.34
        for k, (nm, octv) in enumerate(TRIADS[name]):
            v = choir(note(nm, octv + (1 if k else 0)), BAR + 1.0, seed=b * 5 + k)
            env = np.minimum(1.0, _t(len(v)) / 0.35) * np.exp(-_t(len(v)) / (BAR * 1.1))
            place(pad, v * env, at, loud / (1 + 0.35 * k))

    # Orgelpunkt
    drone = lowpass(saw_stack(note("D", 2), DURATION + 1, voices=3, detune=0.002), 460)
    place(low, drone * 0.17, 0.0)

    # Beat
    i = 0
    tb = 0.0
    while tb < DURATION - 0.2:
        pos = i % 4
        if tb < T.S_CHAT:                                  # Haken: nur Herzschlag
            if pos == 0:
                place(drum, taiko(1.2, seed=i % 5), tb, 0.55)
                place(low, sub_hit(), tb, 0.42)
        elif tb < T.S_CIRCLE:                              # Chat und Fakten: treibend
            if pos in (0, 2):
                place(drum, taiko(0.9, tone=74, seed=i % 5), tb, 0.60)
                place(low, sub_hit(0.9), tb, 0.34)
            if pos in (1, 3):
                place(drum, clap(seed=i % 7), tb, 0.30)
            for half in (0.0, 0.5):
                place(drum, hat(seed=(i * 2 + int(half * 2)) % 9,
                                open_=(pos == 3 and half == 0.5)),
                      tb + half * BEAT, 0.10 if half else 0.15)
        elif tb < T.S_DROP:                                # Verdichtung
            place(drum, taiko(0.7, tone=80, seed=i % 5), tb, 0.42)
            for q in (0.0, 0.25, 0.5, 0.75):
                place(drum, hat(seed=(i * 4 + int(q * 4)) % 9), tb + q * BEAT, 0.13)
        else:                                              # Drop: schwer, halftime
            if pos in (0, 2):
                place(drum, taiko(1.3, tone=66, seed=i % 5), tb, 0.85)
                place(low, sub_hit(1.3), tb, 0.60)
            if pos == 2:
                place(drum, clap(seed=i % 7), tb, 0.34)
            for half in (0.0, 0.5):
                place(drum, hat(seed=(i * 2) % 9, open_=(pos == 3)), tb + half * BEAT, 0.11)
        i += 1
        tb = i * BEAT

    # Chat: jede Nachricht ein Ton, abwechselnd tiefer und heller
    for k, ct in enumerate(T.chat_times()):
        f = note("D", 5) if k % 2 else note("A", 4)
        place(fx, blip(f), ct, 0.20)

    # Fakten: Streicherakzent auf jede Zahl
    for k, ft in enumerate(T.fact_times()):
        tri = chord_at(ft)
        nm, octv = tri[k % len(tri)]
        place(pad, stab(note(nm, octv + 1), seed=k), ft, 0.42)
        place(drum, taiko(0.8, tone=90, punch=0.7, seed=k), ft, 0.34)

    # Grosse Momente
    for at, g in ((T.S_HOOK + 1.5 * BEAT, 0.55), (T.S_CHAT, 0.40),
                  (T.S_FACTS, 0.45), (T.S_CIRCLE, 0.50), (T.S_DROP, 1.0),
                  (T.S_CTA, 0.40)):
        root = PROGRESSION[min(len(PROGRESSION) - 1, int(at / BAR))]
        place(low, braam(note(root, 2), 2.8), at, g * 0.85)
        place(drum, impact(3.0, seed=int(at * 3) % 5), at, g * 0.9)
        place(low, sub_hit(2.0, 92, 30), at, g * 0.7)
    place(fx, riser(2.0), T.S_DROP - 2.0, 0.5)
    place(fx, riser(1.6), T.S_FACTS - 1.6, 0.28)
    place(fx, bell(note("F", 5), 5.0), T.S_DROP, 0.34)
    place(fx, bell(note("D", 5), 4.0), T.S_CTA, 0.18)

    mix = pad * 1.30 + low * 0.70 + drum * 1.00 + fx * 0.80
    mix = eq(mix, [(25, -17), (45, -9.0), (90, -6.5), (200, -1.0), (500, 1.5),
                   (1200, 3.5), (2500, 5.0), (5000, 3.5), (9000, -4.0), (14000, -18.0)])
    mix = reverb(mix, 1.9, 0.20)
    mix = lowpass(mix, 12000, order=1.6)

    left = reverb(mix, 1.2, 0.10, seed=21)
    right = reverb(mix, 1.2, 0.10, seed=43)
    st = np.stack([left, right], axis=1)
    tt = _t(n)[:, None]
    st *= np.clip(tt / 0.25, 0, 1)
    st *= np.clip((DURATION - tt) / 0.8, 0, 1) ** 1.1
    st = np.tanh(st * 2.6) / 2.6
    st *= 0.94 / (np.max(np.abs(st)) + 1e-9)
    return st


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="work/soundtrack_tiktok.wav")
    a = ap.parse_args()
    audio = build()
    write_wav(Path(a.out), audio)
    rms = float(np.sqrt(np.mean(audio ** 2)))
    print(f"{a.out}: {audio.shape[0]/SR:.1f}s peak={np.max(np.abs(audio)):.2f} "
          f"rms={20*math.log10(rms+1e-9):.1f} dBFS")
