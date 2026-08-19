"""Die Partitur: eine gemeinsame Zeitachse fuer Bild und Ton.

Alles laeuft auf 90 BPM. Szenengrenzen liegen auf Taktgrenzen, jeder Schlag im
Bild hat seine Entsprechung in der Musik - beide Module lesen aus dieser Datei.
"""
from __future__ import annotations

BPM = 90.0
BEAT = 60.0 / BPM          # 0.6667 s
BAR = 4 * BEAT             # 2.6667 s


def bar(n: float) -> float:
    return n * BAR


# ------------------------------------------------------------- Szenen -------
S_INTRO = bar(0)           #  0.00  Kaltstart: eine Frage im Dunkeln
S_STORM = bar(3)           #  8.00  Fragensturm
S_PHIL = bar(7)            # 18.67  Die Philosophen
S_DEBATE = bar(12)         # 32.00  Die Debatte
S_TWELVE = bar(17)         # 45.33  Zwoelf Wege
S_CLAIM = bar(21)          # 56.00  Die Haltung
S_EMBLEM = bar(23)         # 61.33  Emblem
S_CTA = bar(25)            # 66.67  Einladung
END = bar(27)              # 72.00


# ------------------------------------------------------------- Texte --------
OPENING = "Woran glaubst du?"

QUESTIONS = [
    # Text, Beatversatz ab S_STORM, Seite (-1 links, +1 rechts), Hoehenanteil
    ("Gibt es Gott – oder nur uns?",        1, -1, 0.30),
    ("Was kommt nach dem Tod?",             3,  1, 0.46),
    ("Warum lässt Gott das Leid zu?",       5, -1, 0.62),
    ("Braucht Moral einen Gott?",           7,  1, 0.34),
    ("Ist Glaube Privatsache?",             9, -1, 0.70),
    ("Hat die Wissenschaft Gott ersetzt?", 11,  1, 0.54),
    ("Wer entscheidet, was wahr ist?",     13, -1, 0.42),
    ("Und wenn wir uns alle irren?",       15,  1, 0.66),
]

# Der Philosophen-Part: sechs Stimmen, alle drei Schlaege eine
QUOTES = [
    ("Gott ist tot. Und wir haben ihn getötet.", "Friedrich Nietzsche"),
    ("Wenn es keinen Gott gibt, ist alles erlaubt.", "Fjodor Dostojewski"),
    ("Habe Mut, dich deines eigenen Verstandes zu bedienen.", "Immanuel Kant"),
    ("Unruhig ist unser Herz, bis es ruht in dir.", "Augustinus"),
    ("Der Zweifel führt zur Wahrheit.", "Al-Ghazali"),
    ("Man muss sich Sisyphos als glücklichen Menschen vorstellen.", "Albert Camus"),
]
QUOTE_STEP = 3 * BEAT       # 2.0 s pro Zitat
QUOTE_START = S_PHIL + 0.5 * BEAT

# Die simulierte Debatte - abwechselnd, wie im Chat
DEBATE = [
    (-1, "Ohne Gott gibt es keine Moral."),
    (+1, "Dann bist du nur gut, weil du Angst hast?"),
    (-1, "Religionen haben Kriege geführt."),
    (+1, "Ideologien ohne Gott auch."),
    (-1, "Die Wissenschaft erklärt alles."),
    (+1, "Warum es überhaupt etwas gibt, nicht."),
    (-1, "Dein heiliges Buch haben Menschen geschrieben."),
    (+1, "Deine Vernunft auch."),
]
DEBATE_STEP = 2 * BEAT      # 1.333 s pro Replik
DEBATE_START = S_DEBATE + 0.5 * BEAT
DEBATE_CLOSER = "UND DANN? REDET MAN WEITER."

CLAIM_A = "HIER WIRD GESTRITTEN."
CLAIM_B = "NICHT GEHETZT."
CLAIM_SUB = "Argumente statt Parolen. Neugier statt Feindbilder."
CAPTION_TWELVE = "ZWÖLF WEGE · EIN TISCH"
TITLE = "DIALOG DER RELIGIONEN"
SUBTITLE = "Der Discord für ehrliche Gespräche über Gott und die Welt."
LINK = "discord.gg/dialog-der-religionen"
CTA_LINE = "Komm rein. Stell deine Frage."
FEATURE_LINE = "Tägliche Debatten · Voice-Runden am Abend · moderiert · für Gläubige, Zweifler und Atheisten"


# -------------------------------------------------------------- Schlaege ----
def quote_times() -> list[float]:
    return [QUOTE_START + i * QUOTE_STEP for i in range(len(QUOTES))]


def debate_times() -> list[float]:
    return [DEBATE_START + i * DEBATE_STEP for i in range(len(DEBATE))]


def question_times() -> list[float]:
    return [S_STORM + b * BEAT for _, b, _, _ in QUESTIONS]


# grosse Schlaege: Szenenwechsel und Zitate - Kamera und Musik teilen sie sich
BIG_HITS = ([S_STORM, S_PHIL, S_DEBATE, S_TWELVE, S_CLAIM, S_EMBLEM, S_CTA]
            + quote_times())
# kleine Schlaege: jede Frage, jede Replik
SMALL_HITS = question_times() + debate_times() + [S_DEBATE + 16.5 * BEAT]

ALL_HITS = sorted(BIG_HITS + SMALL_HITS)
