"""Partitur der TikTok-Fassung - 26 Sekunden bei 120 BPM.

Kurz, dicht, mit Haken in der ersten Sekunde: auf TikTok entscheidet sich in
zwei Sekunden, ob jemand bleibt. Danach Schlag auf Schlag - Chat, Fakten,
Drop, Einladung - und ein Schluss, der zum Anfang zurueckfuehrt (Loop).
"""
from __future__ import annotations

BPM = 120.0
BEAT = 60.0 / BPM          # 0.5 s
BAR = 4 * BEAT             # 2.0 s


def bar(n: float) -> float:
    return n * BAR


# ------------------------------------------------------------- Abschnitte ---
S_HOOK = bar(0)            #  0.0  Haken
S_CHAT = bar(2)            #  4.0  Schlagabtausch
S_FACTS = bar(6)           # 12.0  Fakten im Takt
S_CIRCLE = bar(8)          # 16.0  zwoelf Zeichen
S_DROP = bar(9)            # 18.0  Emblem
S_CTA = bar(11)            # 22.0  Einladung
END = bar(13)              # 26.0


# ------------------------------------------------------------------ Texte ---
# Der Haken: erst die Erwartung aufbauen, dann brechen
HOOK_WORDS = [
    ("CHRISTEN.", 0.00),
    ("MUSLIME.", 0.50),
    ("ATHEISTEN.", 1.00),
]
HOOK_TWIST = "EIN CHAT."
HOOK_PUNCH = "UND KEINER RASTET AUS."

# Der Schlagabtausch - kurz genug zum Mitlesen beim Scrollen
CHAT = [
    (-1, "Ohne Gott gibt es keine Moral.",      0.0),
    (+1, "Dann bist du nur gut aus Angst?",     1.2),
    (-1, "Woher kommt dann dein Gewissen?",     2.4),
    (+1, "Evolution. Nächste Frage.",           3.6),
    (-1, "Und warum gibt es überhaupt etwas?",  4.8),
    (+1, "… gute Frage.",                       6.0),
]
CHAT_CLOSER = "SO REDEN WIR HIER. JEDEN TAG."

# Fakten, jeweils auf einen Schlag
FACTS = [
    ("12", "Weltanschauungen am Tisch"),
    ("0", "Bekehrungsdruck"),
    ("20 UHR", "Voice-Runden jeden Abend"),
    ("24/7", "jemand, der antwortet"),
]

TITLE = "DIALOG DER RELIGIONEN"
LINK = "discord.gg/dialog-der-religionen"
CTA_LINE = "Komm rein. Stell deine Frage."
LOOP_LINE = "CHRISTEN. MUSLIME. ATHEISTEN."


def chat_times() -> list[float]:
    return [S_CHAT + off * BEAT for _, _, off in CHAT]


def fact_times() -> list[float]:
    return [S_FACTS + i * BEAT * 1.5 for i in range(len(FACTS))]


BIG_HITS = [S_HOOK + 1.5 * BEAT, S_CHAT, S_FACTS, S_CIRCLE, S_DROP, S_CTA]
SMALL_HITS = ([S_HOOK + w[1] for w in HOOK_WORDS] + chat_times() + fact_times())
ALL_HITS = sorted(BIG_HITS + SMALL_HITS)
