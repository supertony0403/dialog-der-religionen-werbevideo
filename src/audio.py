"""Trailer-Score - vollstaendig synthetisiert, ohne Fremdrechte.

Wuchtig, aber nicht schrill: Sub und Trommeln tragen die Energie, die Hoehen
sind bewusst gedeckelt (Tiefpass ab ~12 kHz, keine harten Transienten oben).
Alle Einsaetze kommen aus timing.py - dieselbe Partitur, die das Bild benutzt.
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path

import numpy as np

import timing as T

SR = 48000
BEAT, BAR = T.BEAT, T.BAR
DURATION = T.END


def note(name: str, octave: int) -> float:
    base = {"C": -9, "C#": -8, "D": -7, "D#": -6, "E": -5, "F": -4,
            "F#": -3, "G": -2, "G#": -1, "A": 0, "A#": 1, "B": 2}[name]
    return 440.0 * 2 ** ((base + (octave - 4) * 12) / 12)


# Akkordfolge in d-Moll, ein Eintrag je Takt, mit Dur-Aufhellung am Schluss
PROGRESSION = [
    "D", "D", "D",                       # 0-2   Intro
    "D", "A#", "F", "C",                 # 3-6   Fragensturm
    "D", "D", "G", "A#", "A",            # 7-11  Philosophen
    "D", "A#", "G", "C", "D",            # 12-16 Debatte
    "A#", "F", "C", "D",                 # 17-20 Zwoelf Wege
    "A#", "C",                           # 21-22 Haltung
    "F", "A#",                           # 23-24 Emblem
    "F", "C",                            # 25-26 Einladung
]
TRIADS = {
    "D": [("D", 3), ("F", 3), ("A", 3)],
    "A#": [("A#", 2), ("D", 3), ("F", 3)],
    "F": [("F", 2), ("A", 3), ("C", 4)],
    "C": [("C", 3), ("E", 3), ("G", 3)],
    "G": [("G", 2), ("A#", 3), ("D", 4)],
    "A": [("A", 2), ("C#", 3), ("E", 3)],
}


def _t(n: int) -> np.ndarray:
    return np.arange(n, dtype=np.float64) / SR


def lowpass(x: np.ndarray, cutoff: float, order: float = 2.0) -> np.ndarray:
    n = len(x)
    spec = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1 / SR)
    return np.fft.irfft(spec / (1 + (f / cutoff) ** (2 * order)), n)


def highpass(x: np.ndarray, cutoff: float) -> np.ndarray:
    n = len(x)
    spec = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1 / SR)
    g = (f / cutoff) ** 2 / (1 + (f / cutoff) ** 2)
    return np.fft.irfft(spec * g, n)


def formant(x: np.ndarray, freqs=(760, 1180, 2540), widths=(120, 190, 320),
            tilt: float = 0.55) -> np.ndarray:
    """Vokalfilter - macht aus einer Saegezahnstimme einen Chorlaut."""
    n = len(x)
    spec = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1 / SR)
    g = np.full_like(f, 0.10)
    for fc, bw, amp in zip(freqs, widths, (1.0, 0.72, 0.38)):
        g += amp * np.exp(-0.5 * ((f - fc) / bw) ** 2)
    g *= 1.0 / (1 + (f / 4200) ** (2 * tilt * 3))
    return np.fft.irfft(spec * g, n)


# ------------------------------------------------------------ Bausteine -----
def saw_stack(freq: float, dur: float, voices: int = 5, detune: float = 0.004,
              vib: float = 0.0016, seed: int = 0) -> np.ndarray:
    n = int(dur * SR)
    t = _t(n)
    rng = np.random.default_rng(seed)
    out = np.zeros(n)
    for i in range(voices):
        d = detune * (i - (voices - 1) / 2) / max(1, (voices - 1) / 2)
        ph = rng.random()
        wob = vib * np.sin(2 * math.pi * (4.1 + 0.7 * i) * t + ph * 6.283)
        phase = np.cumsum(freq * (1 + d + wob)) / SR + ph
        out += 2.0 * (phase % 1.0) - 1.0
    return out / voices


def choir(freq: float, dur: float, seed: int = 0, vowel=(760, 1180, 2540)) -> np.ndarray:
    """Chorstimme: Saegezahn-Stack durch Vokalfilter, weich eingeschwungen."""
    x = saw_stack(freq, dur, voices=6, detune=0.006, vib=0.0022, seed=seed)
    x = formant(x, vowel)
    return lowpass(x, 5200)


def braam(freq: float, dur: float = 3.4, grit: float = 1.6) -> np.ndarray:
    """Tiefes Trailer-Horn: additive Obertoene, die langsam aufgehen."""
    n = int(dur * SR)
    t = _t(n)
    open_ = 1 - np.exp(-t * 2.6)
    out = np.zeros(n)
    for k in range(1, 22):
        amp = np.exp(-k / (2.0 + 9.0 * open_)) / (k ** 0.45)
        det = 1 + 0.0016 * ((k % 3) - 1)
        out += amp * np.sin(2 * math.pi * freq * k * det * t)
    out = np.tanh(out * grit) / grit
    env = np.minimum(1.0, t / 0.10) * np.exp(-t / (dur * 0.55))
    return lowpass(out * env, 3600)


def taiko(dur: float = 1.4, tone: float = 68.0, punch: float = 1.0,
          seed: int = 1) -> np.ndarray:
    """Grosse Trommel: Koerper mit Tonhoehenabfall plus gedaempftes Fell."""
    n = int(dur * SR)
    t = _t(n)
    f = tone * (1 + 2.6 * np.exp(-t * 26))
    body = np.sin(2 * math.pi * np.cumsum(f) / SR) * np.exp(-t * 6.5)
    rng = np.random.default_rng(seed)
    skin = lowpass(rng.normal(0, 1, n) * np.exp(-t * 30), 3800) * 1.05
    sub = np.sin(2 * math.pi * 41 * t) * np.exp(-t * 5.0) * 0.22
    return (body * 0.72 + skin + sub) * punch


def impact(dur: float = 4.0, seed: int = 2) -> np.ndarray:
    """Aufschlag: Kick, Sub-Absturz und ein dumpfer Rauschschlag."""
    n = int(dur * SR)
    t = _t(n)
    rng = np.random.default_rng(seed)
    kick = np.sin(2 * math.pi * np.cumsum(130 * np.exp(-t * 9) + 34) / SR) * np.exp(-t * 2.4)
    boom = lowpass(rng.normal(0, 1, n) * np.exp(-t * 6.0), 1900) * 0.85
    sub = np.sin(2 * math.pi * np.cumsum(58 * np.exp(-t * 1.1) + 27) / SR) * np.exp(-t * 1.1)
    return kick * 0.70 + boom * 0.65 + sub * 0.45


def stab(freq: float, dur: float = 0.42, seed: int = 3) -> np.ndarray:
    """Kurzer Streicherakzent."""
    n = int(dur * SR)
    t = _t(n)
    x = saw_stack(freq, dur, voices=4, detune=0.005, seed=seed)
    rng = np.random.default_rng(seed + 7)
    bow = lowpass(rng.normal(0, 1, n), 3200) * np.exp(-t * 40) * 0.25
    env = np.minimum(1.0, t / 0.012) * np.exp(-t * 8.0)
    return lowpass((x + bow) * env, 3600)


def riser(dur: float = 2.6, seed: int = 4) -> np.ndarray:
    """Anschwellendes Rauschen mit steigender Tonhoehe."""
    n = int(dur * SR)
    t = _t(n)
    rng = np.random.default_rng(seed)
    noise = rng.normal(0, 1, n)
    spec = np.fft.rfft(noise)
    f = np.fft.rfftfreq(n, 1 / SR)
    out = np.zeros(n)
    steps = 24
    for i in range(steps):
        p = i / (steps - 1)
        band = spec * np.exp(-((f - (250 + 3400 * p)) / (300 + 900 * p)) ** 2)
        seg_ = np.fft.irfft(band, n)
        w = np.zeros(n)
        w[int(n * i / steps):int(n * (i + 1) / steps)] = 1.0
        out += seg_ * w
    tone = np.sin(2 * math.pi * np.cumsum(110 * 2 ** (np.linspace(0, 2.2, n))) / SR)
    env = np.linspace(0, 1, n) ** 2.4
    return lowpass((out / (np.max(np.abs(out)) + 1e-9) * 0.8 + tone * 0.35) * env, 7000)


def reverse_swell(dur: float = 1.8, seed: int = 6) -> np.ndarray:
    n = int(dur * SR)
    rng = np.random.default_rng(seed)
    t = _t(n)
    x = lowpass(rng.normal(0, 1, n), 3800) * np.exp(-t * 3.0)
    return x[::-1] * 0.6


def bell(freq: float, dur: float = 6.0) -> np.ndarray:
    n = int(dur * SR)
    t = _t(n)
    out = np.zeros(n)
    for rt, a, dk in zip((1.0, 2.01, 2.98, 4.18, 5.42), (1.0, 0.55, 0.38, 0.24, 0.15),
                         (1.0, 1.6, 2.2, 3.0, 3.8)):
        out += a * np.sin(2 * math.pi * freq * rt * t) * np.exp(-dk * t / (dur * 0.4))
    return lowpass(out / 2.3, 6000)


def reverb(x: np.ndarray, seconds: float = 3.2, mix: float = 0.30, seed: int = 11):
    rng = np.random.default_rng(seed)
    m = int(seconds * SR)
    t = _t(m)
    ir = rng.normal(0, 1, m) * np.exp(-t * (3.2 / seconds))
    ir = lowpass(ir, 4200)
    ir[:int(0.015 * SR)] *= np.linspace(0, 1, int(0.015 * SR))
    ir /= np.sqrt(np.sum(ir ** 2))
    n = 1 << (len(x) + m).bit_length()
    wet = np.fft.irfft(np.fft.rfft(x, n) * np.fft.rfft(ir, n), n)[:len(x)]
    wet *= np.max(np.abs(x)) / (np.max(np.abs(wet)) + 1e-9)
    return (1 - mix) * x + mix * wet


def eq(x: np.ndarray, points) -> np.ndarray:
    n = len(x)
    spec = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1 / SR)
    hz = np.array([p[0] for p in points], float)
    db = np.array([p[1] for p in points], float)
    gain = 10 ** (np.interp(np.log10(np.maximum(f, 1.0)), np.log10(hz), db) / 20.0)
    return np.fft.irfft(spec * gain, n)


def place(track: np.ndarray, sig: np.ndarray, at: float, gain: float = 1.0):
    i = int(at * SR)
    if i >= len(track) or gain == 0:
        return
    j = min(len(track), i + len(sig))
    track[i:j] += sig[:j - i] * gain


# ------------------------------------------------------------ Arrangement ---
def chord_at(t: float):
    idx = min(len(PROGRESSION) - 1, max(0, int(t / BAR)))
    return TRIADS[PROGRESSION[idx]]


def build() -> np.ndarray:
    n = int(DURATION * SR)
    pad = np.zeros(n)      # Chor und Flaechen
    low = np.zeros(n)      # Orgelpunkt und Braams
    drum = np.zeros(n)     # Trommeln und Aufschlaege
    fx = np.zeros(n)       # Riser, Glocken, Schwellen
    duck_hits: list[float] = []

    # Orgelpunkt
    drone_len = DURATION + 2
    dt = _t(int(drone_len * SR))
    drone = lowpass(saw_stack(note("D", 2), drone_len, voices=3, detune=0.002), 520)
    drone *= 0.20 * (0.6 + 0.4 * np.sin(2 * math.pi * 0.05 * dt))
    place(low, drone, 0.0)

    # Chor je Takt
    for b, name in enumerate(PROGRESSION):
        at = b * BAR
        if at >= DURATION:
            break
        loud = 0.30
        if b >= 3:
            loud = 0.86
        if b >= 7:
            loud = 0.30                       # Philosophen: Luft lassen
        if b >= 12:
            loud = 0.50
        if b >= 17:
            loud = 0.74                       # Zwoelf Wege: voller Chor
        if b >= 23:
            loud = 0.46                       # Emblem
        if b >= 25:
            loud = 0.62
        for k, (nm, octv) in enumerate(TRIADS[name]):
            f = note(nm, octv + (1 if b >= 17 and k else 0))
            v = choir(f, BAR + 1.4, seed=b * 5 + k)
            env = np.minimum(1.0, _t(len(v)) / 0.55) * np.exp(-_t(len(v)) / (BAR * 1.4))
            place(pad, v * env, at, loud / (1 + 0.4 * k))

    # Puls: Trommeln je nach Abschnitt
    beat_i = 0
    t_beat = 0.0
    while t_beat < DURATION - 0.3:
        pos = beat_i % 4
        g = 0.0
        if t_beat < T.S_STORM:                       # Herzschlag im Intro
            g = 0.22 if pos == 0 else 0.0
        elif t_beat < T.S_PHIL:                      # Fragensturm: 1 und 3
            g = 0.55 if pos in (0, 2) else 0.14
        elif t_beat < T.S_DEBATE:                    # Philosophen: fast still
            g = 0.16 if pos == 0 else 0.0
        elif t_beat < T.S_TWELVE:                    # Debatte: treibend
            g = 0.50 if pos in (0, 2) else 0.26
        elif t_beat < T.S_CLAIM:                     # Zwoelf Wege: voll
            g = 0.68 if pos == 0 else 0.34
        elif t_beat < T.S_EMBLEM:                    # Haltung: halftime, schwer
            g = 0.85 if pos in (0, 2) else 0.0
        elif t_beat < T.S_CTA:
            g = 0.55 if pos == 0 else 0.0
        else:
            g = 0.32 if pos == 0 else 0.0
        if g > 0:
            place(drum, taiko(seed=beat_i % 7), t_beat, g)
            if g > 0.4:
                duck_hits.append(t_beat)
        beat_i += 1
        t_beat = beat_i * BEAT

    # Streicherfiguren: Achtel im Sturm, Sechzehntel in der Debatte
    for start, stop, step, gain in ((T.S_STORM, T.S_PHIL, BEAT / 2, 0.34),
                                    (T.S_DEBATE, T.S_TWELVE, BEAT / 2, 0.36),
                                    (T.S_TWELVE, T.S_CLAIM, BEAT / 2, 0.22)):
        k = 0
        tt = start
        while tt < stop:
            tri = chord_at(tt)
            nm, octv = tri[k % len(tri)]
            f = note(nm, octv + 1)
            place(pad, stab(f, seed=k % 11), tt, gain * (1.25 if k % 4 == 0 else 0.8))
            k += 1
            tt = start + k * step

    # Grosse Ereignisse
    for at, gain in ((T.S_STORM, 0.55), (T.S_PHIL, 0.40), (T.S_DEBATE, 0.42),
                     (T.S_TWELVE, 0.52), (T.S_CLAIM, 0.60), (T.S_EMBLEM, 0.85)):
        root = PROGRESSION[min(len(PROGRESSION) - 1, int(at / BAR))]
        place(low, braam(note(root, 2), 3.6), at, gain)
        place(drum, impact(seed=int(at) % 5), at, gain * 0.9)
        place(fx, riser(2.4), at - 2.4, gain * 0.45)
        place(fx, reverse_swell(1.6), at - 1.6, gain * 0.35)
        duck_hits.append(at)

    # Philosophen: jedes Zitat bekommt seinen eigenen Schlag
    for i, qt in enumerate(T.quote_times()):
        place(drum, taiko(1.6, tone=58, seed=i), qt, 0.48)
        place(drum, impact(2.4, seed=i + 9), qt, 0.22)
        place(fx, reverse_swell(1.0, seed=i + 3), qt - 1.0, 0.22)
        duck_hits.append(qt)

    # Debatte: trockener Akzent auf jede Replik
    for i, dt_ in enumerate(T.debate_times()):
        place(drum, taiko(0.7, tone=96, punch=0.6, seed=i + 2), dt_, 0.30)

    # Glocken und Ausklang
    place(fx, bell(note("D", 5), 7.0), T.S_TWELVE, 0.34)
    place(fx, bell(note("F", 5), 9.0), T.S_EMBLEM, 0.50)
    place(fx, bell(note("A", 5), 7.0), T.S_EMBLEM + 2 * BEAT, 0.16)
    place(fx, bell(note("D", 5), 8.0), T.S_CTA + BAR, 0.16)

    # leichtes Ducking: die Flaechen weichen den Schlaegen aus
    t_all = _t(n)
    duck = np.ones(n)
    for ht in sorted(set(duck_hits)):
        i0 = int(ht * SR)
        i1 = min(n, i0 + int(0.55 * SR))
        if i0 >= n:
            continue
        seg_ = t_all[i0:i1] - ht
        duck[i0:i1] = np.minimum(duck[i0:i1], 1.0 - 0.38 * np.exp(-seg_ * 7.0))
    pad *= duck
    low *= 0.5 + 0.5 * duck

    mix = pad * 1.15 + low * 0.70 + drum * 0.80 + fx * 0.75
    mix = eq(mix, [(25, -15), (45, -7.5), (90, -5.0), (200, -0.5), (500, -0.5),
                   (1200, 1.5), (2500, 4.5), (5000, 3.5), (9000, -3.0), (15000, -14.0)])
    mix = reverb(mix, 3.0, 0.26)
    mix = lowpass(mix, 12500, order=1.5)          # nichts, was in den Ohren sticht

    left = reverb(mix, 2.0, 0.14, seed=21)
    right = reverb(mix, 2.0, 0.14, seed=43)
    st = np.stack([left, right], axis=1)

    t2 = t_all[:, None]
    st *= np.clip(t2 / 0.8, 0, 1)
    st *= np.clip((DURATION - t2) / 1.4, 0, 1) ** 1.1
    st = np.tanh(st * 2.3) / 2.3                  # weiche Saettigung statt Clipping
    st *= 0.92 / (np.max(np.abs(st)) + 1e-9)
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
    print(f"{a.out}: {audio.shape[0]/SR:.1f}s peak={np.max(np.abs(audio)):.3f} "
          f"rms={20*math.log10(rms+1e-9):.1f} dBFS")
