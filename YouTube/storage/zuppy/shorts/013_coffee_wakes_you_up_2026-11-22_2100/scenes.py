"""Episode: coffee_wakes_you_up | Channel: zuppy | Strict style"""

import math
from core.primitives import *

MODE = "shorts"
CHANNEL_NAME = "zuppy"

TEXTS = [
    "Coffee wakes you up—but adds no energy. Your brain builds adenosine while you're awake. It signals growing sleep pressure.",
    "Caffeine blocks the receptors that detect it. Think of it as a fake key. It jams the sleep signal's lock.",
    "But the sleepy chemical remains. Caffeine only masks tiredness for now. When it fades, will sleepiness return?",
]

CHAPTERS = ["The Wake-Up Trick", "Blocking Sleepiness"]

META = {
    "title": "Coffee Wakes You Up Without Energy (Here's Why)",
    "description": (
        "Coffee wakes you up—but it doesn't add energy. "
        "Here's the caffeine trick that blocks sleepiness.\n\n"
        "SOURCES:\n"
        "- NIH News in Health, Tired or Wired? Caffeine and Your Brain\n"
        "- Caffeine, StatPearls / NCBI Bookshelf\n"
        "- Review of caffeine's effects on cognitive, physical and occupational performance, Neurobiology of Aging\n\n"
        "#shorts #science #coffee #brain #psychology"
    ),
    "tags": (
        "why coffee wakes you up, caffeine explained, coffee energy, caffeine and adenosine, "
        "why caffeine works, brain science, sleep pressure, tiredness explained, neuroscience, "
        "health science, psychology facts, coffee facts, science shorts, 2d animation, "
        "animated explainer, science explained, everyday science, caffeine receptors, "
        "adenosine receptor blocker, how caffeine works in your brain, alertness mechanism"
    ),
    "pinned_comment": "Does coffee wake you up—or just hide your tiredness? 👇",
}
TITLE = META["title"]
DESC = META["description"]
TAGS = META["tags"]


INK = (35, 35, 45)
WHITE = (255, 255, 255)
YEL = (255, 220, 55)
RED = (220, 65, 65)
BLUE = (65, 115, 210)
GRN = (65, 175, 115)
BG1 = (40, 45, 105)
BG2 = (225, 240, 255)
BG3 = (255, 235, 190)

Y1 = 620
Y2 = 692


def thesis(cv, t, T, k, l1, l2=None, col=WHITE):
    if not (T[k] <= t < T[k + 1]):
        return
    sc = pop(t, T[k], 0.18)
    sz = fit(l1, 54, 500)
    if l2:
        sz = min(sz, fit(l2, 54, 500))
    text(cv, 340, Y1, l1, sz, col, stroke=6, scale=sc)
    if l2:
        text(cv, 340, Y2, l2, sz, col, stroke=6, scale=sc)


def coffee_cup(cv, cx, cy, scale=1.0, steam=True, shake=0.0):
    # Large cup and handle, built only from core primitives.
    x = cx + shake
    rrect(cv, x - 125 * scale, cy - 80 * scale, 250 * scale, 240 * scale,
          18 * scale, WHITE, 6)
    line(cv, [(x - 105 * scale, cy - 55 * scale), (x + 105 * scale, cy - 55 * scale)],
         14 * scale, (80, 55, 35))
    ell(cv, x + 145 * scale, cy + 10 * scale, 55 * scale, 70 * scale, WHITE, 6)
    ell(cv, x + 145 * scale, cy + 10 * scale, 32 * scale, 47 * scale, BG1, 0)
    ell(cv, x, cy - 56 * scale, 104 * scale, 20 * scale, (95, 60, 35), 0)
    if steam:
        for dx, sway in [(-45, 0), (0, 12), (45, -10)]:
            line(cv, [(x + dx * scale, cy - 130 * scale),
                      (x + (dx + sway) * scale, cy - 175 * scale),
                      (x + (dx - sway) * scale, cy - 215 * scale)],
                 8 * scale, WHITE)


def adenosine(cv, cx, cy, scale=1.0, blocked=False):
    # Sleep signal molecule, with simple receptor marks.
    ell(cv, cx, cy, 105 * scale, 105 * scale, (155, 185, 245), 6)
    text(cv, cx, cy, "A", 76 * scale, INK, stroke=2)
    for a in range(0, 360, 45):
        rad = math.radians(a)
        px, py = cx + 130 * scale * math.cos(rad), cy + 130 * scale * math.sin(rad)
        ell(cv, px, py, 15 * scale, 15 * scale, (105, 140, 210), 0)
    if blocked:
        line(cv, [(cx - 150 * scale, cy - 150 * scale),
                  (cx + 150 * scale, cy + 150 * scale)], 18 * scale, RED)
        line(cv, [(cx - 150 * scale, cy + 150 * scale),
                  (cx + 150 * scale, cy - 150 * scale)], 18 * scale, RED)


def receptor(cv, cx, cy, scale=1.0, occupied=False):
    # Receptor as a U-shaped docking slot.
    line(cv, [(cx - 65 * scale, cy - 70 * scale),
              (cx - 65 * scale, cy + 70 * scale),
              (cx, cy + 110 * scale),
              (cx + 65 * scale, cy + 70 * scale),
              (cx + 65 * scale, cy - 70 * scale)], 18 * scale, INK)
    if occupied:
        ell(cv, cx, cy - 20 * scale, 55 * scale, 55 * scale, YEL, 5)
        text(cv, cx, cy - 20 * scale, "C", 48 * scale, INK, stroke=1)


def s01(cv, t, T):
    # Immediate hook frame: coffee cup + high-contrast alert visual already on screen.
    pulse = 1 + 0.04 * math.sin(26 * t)
    coffee_cup(cv, 340, 360, 0.95 * pulse, steam=True, shake=5 * math.sin(42 * t))
    text(cv, 340, 170, "NO ENERGY?", 58, WHITE, stroke=6)
    text(cv, 340, 445, "STILL AWAKE", 54, YEL, stroke=6, scale=1 + 0.03 * math.sin(22 * t))
    if t >= T[1]:
        adenosine(cv, 150, 275, 0.62 * pop(t, T[1] + 0.1))
        text(cv, 150, 150, "ADENOSINE", 38, WHITE, stroke=4, scale=pop(t, T[1] + 0.2))
    if t >= T[2]:
        receptor(cv, 520, 290, 0.7 * pop(t, T[2] + 0.05), occupied=True)
        text(cv, 520, 155, "BLOCKED", 42, YEL, stroke=5, scale=pop(t, T[2] + 0.1))
    thesis(cv, t, T, 0, "COFFEE WAKES", "WITHOUT ENERGY")
    thesis(cv, t, T, 1, "SLEEP SIGNAL", "BUILDS UP")
    thesis(cv, t, T, 2, "CAFFEINE BLOCKS", "THE SIGNAL")


def s02(cv, t, T):
    # Fake-key analogy and the lingering sleep pressure.
    rrect(cv, -20, -20, 740, 1300, 1, BG2, 0)
    if t < T[1]:
        receptor(cv, 340, 320, 1.15 * pop(t, T[0] + 0.05), occupied=True)
        text(cv, 340, 160, "FAKE KEY", 58, BLUE, stroke=5, scale=pop(t, T[0] + 0.1))
        line(cv, [(120, 550), (235, 550), (265, 515)], 14, YEL)
    elif t < T[2]:
        adenosine(cv, 230, 330, 0.9 * pop(t, T[1] + 0.05), blocked=False)
        receptor(cv, 490, 330, 0.9 * pop(t, T[1] + 0.1), occupied=True)
        arrow(cv, 350, 330, 415, 330, 8, RED, rg(t, T[1] + 0.3, T[1] + 0.8))
        text(cv, 340, 170, "TIREDNESS REMAINS", 46, INK, stroke=4, scale=pop(t, T[1] + 0.2))
    else:
        coffee_cup(cv, 340, 390, 0.75 * (1 - 0.4 * pop(t, T[2] + 0.2)), steam=False)
        adenosine(cv, 510, 260, 0.55 * pop(t, T[2] + 0.1))
        text(cv, 340, 180, "SLEEP PRESSURE", 48, INK, stroke=4, scale=pop(t, T[2] + 0.1))
        text(cv, 340, 240, "CAN RETURN", 48, RED, stroke=4, scale=pop(t, T[2] + 0.2))
    thesis(cv, t, T, 0, "CAFFEINE =", "A FAKE KEY", col=INK)
    thesis(cv, t, T, 1, "TIREDNESS IS", "NOT ERASED", col=INK)
    thesis(cv, t, T, 2, "WHEN IT WEARS OFF…", "YOU FEEL IT", col=INK)


def s03(cv, t, T):
    # The underlying sleep pressure remains as caffeine's effect fades.
    rrect(cv, -20, -20, 740, 1300, 1, BG3, 0)
    coffee_cup(cv, 220, 390, 0.55, steam=False)
    adenosine(cv, 485, 315, 0.72 * (1 - 0.45 * pop(t, T[2] + 0.1)))
    if t >= T[1]:
        text(cv, 340, 180, "TIREDNESS IS STILL THERE", 44, INK, stroke=4, scale=pop(t, T[1] + 0.1))
        arrow(cv, 335, 335, 400, 335, 8, RED, rg(t, T[1] + 0.2, T[1] + 0.6))
    if t >= T[2]:
        text(cv, 340, 250, "WHEN CAFFEINE FADES…", 42, RED, stroke=4, scale=pop(t, T[2] + 0.1))
        text(cv, 340, 505, "SLEEPINESS RETURNS?", 44, INK, stroke=4, scale=pop(t, T[2] + 0.2))
    thesis(cv, t, T, 0, "SLEEP SIGNAL", "NEVER DISAPPEARS", col=INK)
    thesis(cv, t, T, 1, "COFFEE MASKS", "THE TIREDNESS", col=INK)
    thesis(cv, t, T, 2, "WHEN IT FADES…", "WHAT HAPPENS?", col=INK)


_FN = {"s01": s01, "s02": s02, "s03": s03}
_BG = {"s01": BG1, "s02": BG2, "s03": BG3}
ORDER = ["s01", "s02", "s03"]
SCENES = [(_BG[k], _FN[k]) for k in ORDER]
