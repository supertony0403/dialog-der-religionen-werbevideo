"""Soundtrack des Werbevideos - vollstaendig synthetisiert (keine Fremdrechte).

Sakraler Ambient in d-Moll bei 90 BPM: Orgelpunkt, atmende Pad-Akkorde,
ruhiger Puls, Glocken auf den Wendepunkten, Aufschwung zum Emblem und
eine Dur-Wendung am Schluss. Erzeugt eine WAV-Datei in 48 kHz Stereo.
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path

import numpy as np

SR = 48000
BPM = 90.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT              # 2.667 s
DURATION = 40.0

# Halbtonabstaende ab A0; wir rechnen direkt in Hertz
def note(name: str, octave: int) -> float:
    base = {"C": -9, "C#": -8, "D": -7, "D#": -6, "E": -5, "F": -4,
            "F#": -3, "G": -2, "G#": -1, "A": 0, "A#": 1, "B": 2}[name]
    return 440.0 * 2 ** ((base + (octave - 4) * 12) / 12)


CHORDS = [
    # (Takt, Grundton, Akkordtoene)
    (0,  "D", [("D", 3), ("A", 3), ("D", 4), ("F", 4)]),
    (1,  "D", [("D", 3), ("A", 3), ("D", 4), ("F", 4)]),
    (2,  "A#", [("A#", 2), ("F", 3), ("A#", 3), ("D", 4)]),
    (3,  "F", [("F", 2), ("C", 3), ("F", 3), ("A", 3)]),
    (4,  "G", [("G", 2), ("D", 3), ("G", 3), ("A#", 3)]),
    (5,  "D", [("D", 3), ("A", 3), ("D", 4), ("F", 4)]),
    (6,  "A#", [("A#", 2), ("F", 3), ("A#", 3), ("D", 4)]),
    (7,  "C", [("C", 3), ("G", 3), ("C", 4), ("E", 4)]),
    (8,  "D", [("D", 3), ("A", 3), ("D", 4), ("F", 4)]),
    (9,  "G", [("G", 2), ("D", 3), ("G", 3), ("A#", 3)]),
    (10, "C", [("C", 3), ("G", 3), ("C", 4), ("E", 4)]),
    (11, "F", [("F", 2), ("C", 3), ("F", 3), ("A", 3)]),      # Emblem: Dur
    (12, "A#", [("A#", 2), ("F", 3), ("A#", 3), ("D", 4)]),
    (13, "F", [("F", 2), ("C", 3), ("F", 3), ("A", 3)]),
    (14, "D", [("D", 3), ("A", 3), ("D", 4), ("F#", 4)]),     # Schluss in Dur
]


def _t(n: int) -> np.ndarray:
    return np.arange(n, dtype=np.float64) / SR


def env_adsr(n: int, attack: float, decay: float, sustain: float, release: float) -> np.ndarray:
    a, d, r = int(attack * SR), int(decay * SR), int(release * SR)
    s = max(0, n - a - d - r)
    parts = [np.linspace(0, 1, a, endpoint=False) ** 1.6 if a else np.array([]),
             np.linspace(1, sustain, d, endpoint=False) if d else np.array([]),
             np.full(s, sustain),
             np.linspace(sustain, 0, r) ** 1.4 if r else np.array([])]
    e = np.concatenate([p for p in parts if p.size])
    if e.size < n:
        e = np.concatenate([e, np.zeros(n - e.size)])
    return e[:n]


def voice(freq: float, dur: float, partials: int = 9, detune: float = 0.0012,
          vib: float = 0.0018) -> np.ndarray:
    """Weiche Orgel-/Streicherstimme aus wenigen Teiltoenen."""
    n = int(dur * SR)
    t = _t(n)
    out = np.zeros(n)
    lfo = np.sin(2 * math.pi * 4.3 * t + freq) * vib
    for k in range(1, partials + 1):
        amp = 1.0 / (k ** 1.5)
        for det in (-detune, detune):
            f = freq * k * (1 + det + lfo)
            out += amp * np.sin(2 * math.pi * np.cumsum(f) / SR)
    return out / (partials * 2)


def bell(freq: float, dur: float = 4.5, bright: float = 1.0) -> np.ndarray:
    """Glocke aus inharmonischen Teiltoenen mit eigenem Abklingen."""
    n = int(dur * SR)
    t = _t(n)
    ratios = [1.0, 2.02, 2.99, 4.21, 5.44, 6.79, 8.21]
    amps = [1.0, 0.62, 0.44, 0.30, 0.20, 0.13, 0.09]
    decays = [1.0, 1.5, 2.1, 2.9, 3.6, 4.4, 5.2]
    out = np.zeros(n)
    for rt, a, dk in zip(ratios, amps, decays):
        out += a * np.sin(2 * math.pi * freq * rt * t) * np.exp(-dk * t / (dur * 0.42))
    strike = np.exp(-t * 90) * np.random.default_rng(int(freq)).normal(0, 1, n) * 0.25 * bright
    return (out / 2.4 + strike) * np.exp(-t / (dur * 0.9))


def sub_pulse(freq: float = 55.0, dur: float = 0.9) -> np.ndarray:
    n = int(dur * SR)
    t = _t(n)
    f = freq * (1 + 0.9 * np.exp(-t * 26))
    body = np.sin(2 * math.pi * np.cumsum(f) / SR) * np.exp(-t * 5.2)
    return body * 0.9


def impact(dur: float = 3.2) -> np.ndarray:
    n = int(dur * SR)
    t = _t(n)
    f = 92 * np.exp(-t * 1.6) + 32
    return np.sin(2 * math.pi * np.cumsum(f) / SR) * np.exp(-t * 1.5)


def riser(dur: float = 2.0, seed: int = 3) -> np.ndarray:
    """Rauschband, das langsam heller und lauter wird."""
    n = int(dur * SR)
    rng = np.random.default_rng(seed)
    x = rng.normal(0, 1, n)
    spec = np.fft.rfft(x)
    freqs = np.fft.rfftfreq(n, 1 / SR)
    out = np.zeros(n)
    steps = 26
    for i in range(steps):
        p = i / (steps - 1)
        cutoff = 260 * (1 - p) + 5200 * p
        band = spec * np.exp(-(freqs / cutoff) ** 2)
        seg = np.fft.irfft(band, n)
        w = np.zeros(n)
        lo, hi = int(n * i / steps), int(n * (i + 1) / steps)
        w[lo:hi] = 1.0
        out += seg * w
    env = np.linspace(0, 1, n) ** 2.2
    return out / (np.max(np.abs(out)) + 1e-9) * env


def shimmer(freq: float, dur: float, seed: int = 0) -> np.ndarray:
    """Hohe, schwebende Stimme fuer den Glanz ueber dem Akkord."""
    n = int(dur * SR)
    t = _t(n)
    rng = np.random.default_rng(seed)
    out = np.zeros(n)
    for det, ph in ((0.0, 0.0), (0.0022, 1.3), (-0.0019, 2.7)):
        wob = 0.0009 * np.sin(2 * math.pi * (0.7 + rng.random() * 0.5) * t + ph)
        out += np.sin(2 * math.pi * freq * (1 + det + wob) * t + ph)
    return out / 3.0


def eq(x: np.ndarray, points) -> np.ndarray:
    """Frequenzgang per FFT: Liste aus (Hertz, Dezibel)."""
    n = len(x)
    spec = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1 / SR)
    hz = np.array([p[0] for p in points], float)
    db = np.array([p[1] for p in points], float)
    gain = 10 ** (np.interp(np.log10(np.maximum(f, 1.0)), np.log10(hz), db) / 20.0)
    return np.fft.irfft(spec * gain, n)


def reverb(x: np.ndarray, seconds: float = 2.6, mix: float = 0.34, seed: int = 11) -> np.ndarray:
    """Kirchenhall per FFT-Faltung mit abklingendem Rauschen."""
    rng = np.random.default_rng(seed)
    m = int(seconds * SR)
    t = _t(m)
    ir = rng.normal(0, 1, m) * np.exp(-t * (3.4 / seconds))
    ir[:int(0.012 * SR)] *= np.linspace(0, 1, int(0.012 * SR))
    ir /= np.sqrt(np.sum(ir ** 2))
    n = 1 << (len(x) + m).bit_length()
    wet = np.fft.irfft(np.fft.rfft(x, n) * np.fft.rfft(ir, n), n)[:len(x)]
    wet *= np.max(np.abs(x)) / (np.max(np.abs(wet)) + 1e-9)
    return (1 - mix) * x + mix * wet


def place(track: np.ndarray, sig: np.ndarray, at: float, gain: float = 1.0):
    i = int(at * SR)
    if i >= len(track):
        return
    j = min(len(track), i + len(sig))
    track[i:j] += sig[:j - i] * gain


def build() -> np.ndarray:
    n = int(DURATION * SR)
    pad = np.zeros(n)
    bass = np.zeros(n)
    perc = np.zeros(n)
    fx = np.zeros(n)

    # Orgelpunkt: der Grundton traegt das ganze Stueck
    drone = voice(note("D", 2), DURATION + 2, partials=5, detune=0.0008)
    dt = _t(len(drone))
    drone *= 0.22 * (0.55 + 0.45 * np.sin(2 * math.pi * 0.055 * dt - 1.2))
    place(bass, drone, 0.0, 1.0)

    # Akkorde, je einen Takt lang und ineinander atmend
    for bar, root, tones in CHORDS:
        at = bar * BAR
        if at >= DURATION:
            break
        dur = BAR + 1.5
        loud = 0.30
        if bar < 2:
            loud = 0.14                       # Szene 1 bleibt fast still
        elif bar >= 11:
            loud = 0.40                       # Emblem und Einladung tragen
        for k, (nm, octv) in enumerate(tones):
            f = note(nm, octv + (1 if k >= 2 else 0))
            v = voice(f, dur, partials=10 if k else 7)
            v *= env_adsr(len(v), 0.85, 0.5, 0.78, 1.1)
            place(pad, v, at, loud / (1 + 0.30 * k))
        if bar >= 2:
            for k, (nm, octv) in enumerate(tones[1:3]):
                sh = shimmer(note(nm, octv + 2), dur, seed=bar * 7 + k)
                sh *= env_adsr(len(sh), 1.3, 0.6, 0.7, 1.3)
                place(pad, sh, at, loud * (0.16 if bar < 11 else 0.24))
        place(bass, voice(note(root, 2), dur, partials=4)
              * env_adsr(int(dur * SR), 0.5, 0.4, 0.8, 1.0), at, 0.17)

    # Ruhiger Puls ab Szene 2, dichter ab Szene 4
    beat = 0.0
    while beat < DURATION - 0.5:
        bar_idx = int(beat // BAR)
        pos = round((beat % BAR) / BEAT)
        if bar_idx >= 2:
            hit = pos in (0, 2) if bar_idx < 8 else True
            if hit:
                g = 0.30 if pos == 0 else 0.17
                if bar_idx >= 11:
                    g *= 1.25
                place(perc, sub_pulse(), beat, g)
        beat += BEAT

    # Glocken auf den Wendepunkten
    place(fx, bell(note("D", 5), 6.0), 13.3333, 0.34)
    place(fx, bell(note("A", 4), 5.0), 21.3333, 0.18)
    place(fx, bell(note("F", 5), 8.0, bright=1.3), 29.3333, 0.44)
    place(fx, bell(note("A", 5), 6.0), 29.3333 + BEAT * 2, 0.16)
    place(fx, bell(note("D", 5), 7.0), 38.4, 0.22)

    # Aufschwung und Aufschlag zum Emblem
    place(fx, riser(2.1), 29.3333 - 2.1, 0.30)
    place(fx, impact(3.4), 29.3333, 0.42)

    mix = pad * 1.0 + bass * 0.85 + perc * 0.45 + fx * 0.90
    mix = eq(mix, [(25, -9), (55, -3.5), (110, -1.0), (220, 0.5), (450, 0.5),
                   (900, -1.0), (1800, -0.5), (3500, 2.5), (7000, 4.5), (14000, 1.0)])
    mix = reverb(mix, 2.8, 0.30)

    # Stereobreite ueber zwei leicht verschiedene Hallfahnen
    left = reverb(mix, 2.2, 0.16, seed=21)
    right = reverb(mix, 2.2, 0.16, seed=43)
    st = np.stack([left, right], axis=1)

    # Aufblende, Abblende, weicher Limiter
    t = _t(n)
    st *= np.clip(t / 1.2, 0, 1)[:, None]
    st *= np.clip((DURATION - t) / 1.6, 0, 1)[:, None] ** 1.2
    st = np.tanh(st * 2.0) / 2.0
    st *= 0.89 / (np.max(np.abs(st)) + 1e-9)
    return st


def write_wav(path: Path, data: np.ndarray):
    import wave
    path.parent.mkdir(parents=True, exist_ok=True)
    pcm = (np.clip(data, -1, 1) * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="work/soundtrack.wav")
    a = ap.parse_args()
    audio = build()
    write_wav(Path(a.out), audio)
    rms = float(np.sqrt(np.mean(audio ** 2)))
    print(f"{a.out}: {audio.shape[0]/SR:.2f}s  peak={np.max(np.abs(audio)):.3f}  rms={rms:.3f} "
          f"({20*math.log10(rms+1e-9):.1f} dBFS)")
