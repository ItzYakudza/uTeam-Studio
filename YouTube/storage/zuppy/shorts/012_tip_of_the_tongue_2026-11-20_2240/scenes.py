"""
Episode: 012_tip_of_the_tongue
Channel: zuppy
Topic: tip-of-the-tongue state
"""
import math
from core.toolkit import *

MODE = "shorts"
CHANNEL_NAME = "zuppy"

TEXTS = [
    "Ever know a word, but suddenly can't say it? It's right there — just out of reach.",
    "Psychologists call this a tip-of-the-tongue state. You may remember its first letter, or how many syllables it has.",
    "That means part of the word is active, but the sound hasn't fully come back. Your memory isn't empty. The retrieval is incomplete.",
    "What's a word that's stuck on the tip of your tongue right now? Say it in the comments.",
]

CHAPTERS = ["The missing word", "Tip-of-the-tongue", "Partial retrieval", "Your turn"]
META = {
    "title": "Why Your Brain Can't Find a Word (Tip-of-the-Tongue)",
    "description": (
        "You know the word. You can almost say it. But it won't come out. "
        "This is the tip-of-the-tongue state: a temporary word-retrieval failure.\n\n"
        "SOURCES:\n"
        "- Brown, R. & McNeill, D. (1966). The “tip of the tongue” phenomenon. "
        "Journal of Verbal Learning and Verbal Behavior, 5(4), 325–337. "
        "https://doi.org/10.1016/S0022-5371(66)80040-3\n"
        "- Schwartz, B. L. & Metcalfe, J. (2011). Tip-of-the-tongue (TOT) states: "
        "retrieval, behavior, and experience. Memory & Cognition, 39, 737–749. "
        "https://doi.org/10.3758/s13421-010-0066-8\n\n"
        "#shorts #psychology #brain #memory #neuroscience"
    ),
    "tags": (
        "tip of the tongue, tip of the tongue phenomenon, why can't I remember a word, "
        "word retrieval, memory glitch, brain glitches, psychology, neuroscience, "
        "cognitive psychology, human brain, science explained, psychology facts, "
        "memory facts, 2d animation, zuppy"
    ),
    "pinned_comment": "What's a word you can almost remember right now?",
}
TITLE = META["title"]
DESC = META["description"]
TAGS = META["tags"]

VIO = (36, 16, 92)
BG2 = (222, 235, 255)
BG3 = (255, 239, 215)
BG4 = (221, 244, 230)
RED = (235, 50, 70)
YEL = (255, 205, 40)
BLUE = (70, 135, 235)
Y1, Y2 = 790, 862

def thesis(cv, t, T, k, a, b=None):
    if not (T[k] <= t < T[k+1]):
        return
    cx = cv.cfg.center_x
    sc = pop(t, T[k], 0.18)
    size = fit_safe(cv, a, 56)
    if b:
        size = min(size, fit_safe(cv, b, 56))
    text(cv, cx, Y1, a, size, WHITE, stroke=6, scale=sc)
    if b:
        text(cv, cx, Y2, b, size, YEL, stroke=6, scale=sc)

def s01(cv, t, T):
    cx = cv.cfg.center_x
    wobble = 5 * math.sin(t * 18)
    rrect(cv, cx-235, 270+wobble, cx+235, 570+wobble, 42, WHITE, 8)
    poly(cv, [(cx+95, 560+wobble), (cx+185, 650+wobble), (cx+165, 555+wobble)], WHITE, 5)
    text(cv, cx, 410, "???", 118, VIO, stroke=4)
    ell(cv, cx-190, 230, 20+5*math.sin(t*12), fill=YEL, w=0)
    ell(cv, cx+190, 230, 20+5*math.sin(t*12+1), fill=YEL, w=0)
    text(cv, cx, 150, "BRAIN GLITCH", 40, YEL, stroke=3)
    thesis(cv, t, T, 0, "KNOW THE WORD", "CAN'T SAY IT")
    thesis(cv, t, T, 1, "RIGHT THERE…", "OUT OF REACH")

def s02(cv, t, T):
    cx = cv.cfg.center_x
    brain(cv, cx, 340, 1.0, 1.0 + 0.035*math.sin(t*7))
    rrect(cv, cx-190, 560, cx+190, 680, 22, WHITE, 5)
    text(cv, cx, 620, "MEANING", 48, INK)
    if t >= T[1]:
        arrow(cv, cx, 490, cx, 535, 8, RED, rg(t, T[1]+0.1, T[1]+0.55))
        rrect(cv, cx-190, 690, cx+190, 790, 18, (255, 220, 215), 5)
        text(cv, cx, 740, "WORD SOUND  ?", 38, RED)
    thesis(cv, t, T, 0, "TIP-OF-THE-", "TONGUE STATE")
    thesis(cv, t, T, 1, "FIRST LETTER?", "SYLLABLES?")

def s03(cv, t, T):
    cx = cv.cfg.center_x
    text(cv, cx, 250, "WORD RETRIEVAL", 38, INK)
    for i, label in enumerate(("MEANING", "SOUND")):
        yy = 390 + i*210
        col = BLUE if i == 0 else RED
        text(cv, cx, yy, label, 36, col)
        for j in range(5):
            xx = 105 + j*102
            active = (j < 5) if i == 0 else (j < (2 if t < T[1] else 3))
            rrect(cv, xx, yy+45, xx+66, yy+100, 8, col if active else (225,225,230), 3)
    if t >= T[1]:
        text(cv, cx, 735, "SIGNAL NOT COMPLETE", 30, RED, stroke=2)
    thesis(cv, t, T, 0, "PART OF THE WORD", "IS ACTIVE")
    thesis(cv, t, T, 1, "NOT A BLANK", "MEMORY")

def s04(cv, t, T):
    cx = cv.cfg.center_x
    for i, x in enumerate((cx-145, cx, cx+145)):
        k = pop(t, T[0]+i*0.18, 0.22)
        ell(cv, x, 390, 55*k, fill=WHITE, w=5)
        text(cv, x, 390, "?" if i == 1 else "…", 54, RED, scale=k)
    if t < T[1]:
        text(cv, cx, 570, "YOU KNOW THE ONE", 38, INK, stroke=2)
    else:
        rrect(cv, cx-215, 315, cx+215, 490, 30, VIO, 0)
        text(cv, cx, 400, "WHAT WORD?", 58, WHITE, stroke=4,
             scale=1+0.025*math.sin(t*12))
    thesis(cv, t, T, 0, "WHAT WORD IS", "STUCK RIGHT NOW?")
    thesis(cv, t, T, 1, "SAY IT BELOW", "IN THE COMMENTS")

TRANSITIONS = {}
_FN = {"s01": s01, "s02": s02, "s03": s03, "s04": s04}
_BG = {"s01": VIO, "s02": BG2, "s03": BG3, "s04": BG4}
ORDER = ["s01", "s02", "s03", "s04"]
SCENES = [(_BG[k], _FN[k]) for k in ORDER]
