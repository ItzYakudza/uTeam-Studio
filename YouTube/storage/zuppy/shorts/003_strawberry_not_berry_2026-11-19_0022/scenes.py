"""
Episode: 004_strawberry_not_berry_2026-11-19_1300
Channel: zuppy
Experimental: 20 seconds, high energy, hook-first (first 3 seconds)
"""

import math
from core.primitives import *

MODE = "shorts"
CHANNEL_NAME = "zuppy"

TEXTS = [
    "Strawberries are not berries. "
    "But bananas are real berries. "
    "Botany just broke your brain.",
    "Real berries hide seeds inside. "
    "Bananas, grapes, even tomatoes qualify. "
    "Strawberry seeds sit on the outside.",
    "Each seed is its own fruit. "
    "The red part is something else. "
    "Mind blown, watch it again.",
]

CHAPTERS = [
    "Hook",
    "What is a berry",
    "The truth",
]

META = {
    "title": "Strawberries Are NOT Berries (But Bananas Are)",
    "description": (
        "Strawberries are not berries, but bananas are. "
        "Here is the quick botany behind the most surprising fruit fact.\n\n"
        "SOURCES:\n"
        "- Live Science: Why are bananas berries but strawberries aren't? https://www.livescience.com/57477-why-are-bananas-considered-berries.html\n"
        "- Science Notes: Is a Strawberry a Berry? https://sciencenotes.org/is-a-strawberry-a-berry-why-the-answer-is-surprisingly-no/\n"
        "- Science ABC: Why Is Strawberry Not A Berry? https://www.scienceabc.com/nature/why-is-strawberry-not-a-berry.html\n"
        "- Judd, W. S., Campbell, C. S., Kellogg, E. A., Stevens, P. F., & Donoghue, M. J. (2016). Plant Systematics: A Phylogenetic Approach (4th ed.). Sinauer Associates\n\n"
        "#shorts #botany #facts #science #fruit"
    ),
    "tags": (
        "strawberries are not berries, bananas are berries, is a banana a berry, "
        "is a strawberry a berry, botany facts, fruit facts, what is a berry, accessory fruit, "
        "interesting facts for kids, mind blowing facts, surprising food facts, science for kids, "
        "amazing science facts, science explained, 2d animation, animated explainer, "
        "quick facts, things you didn't know, zuppy science, biology explained"
    ),
}
TITLE = META["title"]
DESC = META["description"]
TAGS = META["tags"]

RED = (210, 60, 60)
GRN = (60, 150, 80)
YEL = (255, 205, 40)
BANANA = (250, 220, 70)
PURPLE = (150, 90, 180)
BROWN = (120, 80, 50)
BG2 = (205, 235, 255)
BG3 = (255, 236, 200)

Y1 = 620  # первая строка тезиса / заголовка
Y2 = 692  # вторая строка


def thesis(cv, t, T, k, l1, l2=None, col=WHITE):
    """Тезис предложения k: виден от T[k] до T[k+1], по центру экрана."""
    if not (T[k] <= t < T[k + 1]):
        return
    sc = pop(t, T[k], 0.18)
    sz = fit(l1, 54, 500)
    if l2:
        sz = min(sz, fit(l2, 54, 500))
    text(cv, 340, Y1, l1, sz, col, stroke=6, scale=sc)
    if l2:
        text(cv, 340, Y2, l2, sz, col, stroke=6, scale=sc)


def burst(cv, cx, cy, r1, r2, n, rot, fill):
    """Звезда-вспышка с n лучами."""
    pts = []
    for i in range(n * 2):
        r = r1 if i % 2 == 0 else r2
        a = rot + math.pi * i / n
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    poly(cv, pts, fill, 0)


SEEDS = [(-45, -30), (0, -45), (45, -30), (-60, 10), (-15, 0), (30, 5),
         (65, 15), (-30, 50), (15, 55), (50, 55), (-10, 95)]


def strawberry(cv, cx, cy, k=1.0):
    if k <= 0.03:
        return
    poly(cv, [(cx - 90 * k, cy + 40 * k), (cx + 90 * k, cy + 40 * k), (cx, cy + 135 * k)], RED, 6)
    ell(cv, cx, cy - 10 * k, 105 * k, 95 * k, RED, 6)
    for dx, dy in SEEDS:
        ell(cv, cx + dx * k, cy + dy * k, 5 * k, 8 * k, YEL, 0)
    poly(cv, [(cx - 55 * k, cy - 85 * k), (cx - 20 * k, cy - 105 * k), (cx, cy - 130 * k),
              (cx + 20 * k, cy - 105 * k), (cx + 55 * k, cy - 85 * k), (cx, cy - 70 * k)], GRN, 5)


def banana(cv, cx, cy, k=1.0):
    if k <= 0.03:
        return
    R = 110 * k
    pts = [(cx + R * math.cos(math.radians(a)), cy + R * math.sin(math.radians(a))) for a in range(20, 161, 10)]
    line(cv, pts, 52 * k, INK)
    line(cv, pts, 40 * k, BANANA)
    ell(cv, pts[0][0], pts[0][1] - 4 * k, 8 * k, 8 * k, GRN, 3)


def grape(cv, cx, cy, r, k=1.0):
    """Виноградина в разрезе: семена внутри мякоти."""
    if k <= 0.03:
        return
    ell(cv, cx, cy, r * k, r * k, PURPLE, 6)
    ell(cv, cx, cy, r * k * 0.8, r * k * 0.8, (205, 175, 225), 0)
    for dx, dy in ((-0.25, -0.1), (0.25, -0.1), (0, 0.3)):
        ell(cv, cx + dx * r * k, cy + dy * r * k, 0.1 * r * k, 0.16 * r * k, BROWN, 0)


def tomato(cv, cx, cy, r, k=1.0):
    if k <= 0.03:
        return
    ell(cv, cx, cy, r * k, r * k, RED, 6)
    ell(cv, cx, cy - 0.85 * r * k, 0.35 * r * k, 0.14 * r * k, GRN, 4)


def check(cv, x, y, k=1.0):
    if k <= 0.03:
        return
    line(cv, [(x - 18 * k, y), (x - 4 * k, y + 16 * k), (x + 22 * k, y - 18 * k)], 10, GRN)


def hook_frame(cv, dx=0.0, dy=0.0, pulse=1.0, rot=0.0, head=True):
    """Первый кадр Shorts: всё стоит на 100% масштаба, без появления."""
    burst(cv, 340, 345, 215 * pulse, 140 * pulse, 14, rot, WHITE)
    strawberry(cv, 340 + dx, 345 + dy, 1.05)
    if head:
        text(cv, 340, Y1, "STRAWBERRIES", 58, WHITE, stroke=6)
        text(cv, 340, Y2, "NOT BERRIES", 58, RED, stroke=6)


def s01(cv, t, T):
    # 0 strawberries not berries (hook) | 1 bananas are real berries | 2 botany broke your brain
    on = ph(t, T[0], T[0] + 0.2)
    calm = 1 - ph(t, T[0] + 0.9, T[0] + 1.2)
    sh2 = ph(t, T[2], T[2] + 0.15) * (1 - ph(t, T[2] + 0.5, T[2] + 0.8))
    dx = 9 * math.sin(70 * t) * (on * calm + sh2)
    dy = 6 * math.cos(63 * t) * (on * calm + sh2)
    pulse = 1 + 0.06 * math.sin(30 * t) * on
    rot = 0.6 * (t - T[0]) * on
    hook_frame(cv, dx, dy, pulse, rot, head=(t < T[1]))
    if T[0] + 0.6 <= t < T[1]:
        r = rg(t, T[0] + 0.6, T[0] + 0.85)
        line(cv, [(250, 255), (250 + 180 * r, 255 + 185 * r)], 22, RED)
        line(cv, [(430, 255), (430 - 180 * r, 255 + 185 * r)], 22, RED)
    if t >= T[1]:
        r = rg(t, T[1] + 0.02, T[1] + 0.3)
        banana(cv, 520 + 200 * (1 - r), 400, 0.8)
        text(cv, 520, 330, "YES!", 56, GRN, stroke=5, scale=pop(t, T[1] + 0.3))
    if t >= T[2]:
        brain(cv, 135, 230, pop(t, T[2] + 0.05), 0.45)
        text(cv, 135, 140, "BOOM!", 56, RED, stroke=5, scale=pop(t, T[2] + 0.1))
    thesis(cv, t, T, 1, "BANANAS ARE", "REAL BERRIES")
    thesis(cv, t, T, 2, "BOTANY BROKE", "YOUR BRAIN")


def s02(cv, t, T):
    # 0 seeds inside | 1 banana, grape, tomato qualify | 2 strawberry seeds outside
    if t < T[1]:
        grape(cv, 340, 320, 120, pop(t, T[0] + 0.1))
        text(cv, 500, 230, "seeds", 40, RED, scale=pop(t, T[0] + 0.6))
        arrow(cv, 470, 245, 385, 300, 7, RED, rg(t, T[0] + 0.7, T[0] + 1.1))
    elif t < T[2]:
        banana(cv, 150, 300, 0.75 * pop(t, T[1] + 0.1))
        grape(cv, 340, 330, 60, pop(t, T[1] + 0.5))
        tomato(cv, 530, 330, 60, pop(t, T[1] + 0.9))
        check(cv, 150, 230, pop(t, T[1] + 0.3))
        check(cv, 340, 230, pop(t, T[1] + 0.7))
        check(cv, 530, 230, pop(t, T[1] + 1.1))
    else:
        strawberry(cv, 300, 340, 0.95 * pop(t, T[2] + 0.1))
        text(cv, 530, 240, "seeds", 44, RED, scale=pop(t, T[2] + 0.5))
        text(cv, 530, 290, "outside!", 44, RED, scale=pop(t, T[2] + 0.5))
        arrow(cv, 470, 320, 365, 312, 7, RED, rg(t, T[2] + 0.6, T[2] + 1.0))
    thesis(cv, t, T, 0, "SEEDS HIDE", "INSIDE")
    thesis(cv, t, T, 1, "BANANAS, GRAPES,", "TOMATOES")
    thesis(cv, t, T, 2, "STRAWBERRY SEEDS:", "OUTSIDE")


def s03(cv, t, T):
    # 0 each seed = tiny fruit | 1 red part = flower base | 2 loop: возврат к первому кадру
    dk = fa(t, T[2], 0.25)
    rrect(cv, -20, -20, 740, 1300, 1, mix(BG3, YEL, dk), 0)
    if t >= T[2]:
        burst(cv, 340, 345, 215, 140, 14, 0.0, mix(BG3, WHITE, dk))
    strawberry(cv, 340, 345, 1.05 * pop(t, T[0] + 0.05))
    if T[0] <= t < T[1]:
        kb = pop(t, T[0] + 0.3)
        ell(cv, 520, 255, 70 * kb, 70 * kb, WHITE, 6)
        ell(cv, 520, 255, 20 * kb, 32 * kb, YEL, 5)
        text(cv, 520, 355, "tiny fruit", 34, INK, scale=kb)
    if T[1] <= t < T[2]:
        text(cv, 520, 235, "flower", 40, INK, scale=pop(t, T[1] + 0.2))
        text(cv, 520, 280, "base!", 40, INK, scale=pop(t, T[1] + 0.2))
        arrow(cv, 470, 300, 400, 340, 7, RED, rg(t, T[1] + 0.4, T[1] + 0.8))
    if t >= T[2]:
        text(cv, 340, Y1, "STRAWBERRIES", 58, WHITE, stroke=6)
        text(cv, 340, Y2, "NOT BERRIES", 58, RED, stroke=6)
    thesis(cv, t, T, 0, "EACH SEED =", "TINY FRUIT")
    thesis(cv, t, T, 1, "RED PART =", "FLOWER BASE")


_FN = {"s01": s01, "s02": s02, "s03": s03}
_BG = {"s01": YEL, "s02": BG2, "s03": BG3}
ORDER = ["s01", "s02", "s03"]
SCENES = [(_BG[k], _FN[k]) for k in ORDER]