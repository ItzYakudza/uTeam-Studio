"""
Episode: 005_octopus_three_hearts_2026-11-19_1400
Channel: zuppy
Experimental: 18 seconds, high energy, hook-first
"""

import math
from core.primitives import *

MODE = "shorts"
CHANNEL_NAME = "zuppy"

TEXTS = [
    "Octopuses have three hearts. "
    "Their blood is blue too. "
    "Let me explain fast.",
    "Two hearts serve the gills. "
    "One heart feeds the body. "
    "Copper turns their blood blue.",
    "Swimming stops the main heart. "
    "So octopuses prefer crawling. "
    "Watch again, count hearts.",
]

CHAPTERS = [
    "Hook",
    "How the hearts work",
    "Swim or crawl",
]

META = {
    "title": "Octopuses Have 3 Hearts and Blue Blood",
    "description": (
        "Octopuses have three hearts and blue blood. "
        "Here is the quick science behind it.\n\n"
        "SOURCES:\n"
        "- Smithsonian Magazine: Ten Wild Facts About Octopuses: They Have Three Hearts, Big Brains and Blue Blood. https://www.smithsonianmag.com/science-nature/ten-wild-facts-about-octopuses-they-have-three-hearts-big-brains-and-blue-blood-7625828/\n"
        "- Wells, M. J., & Smith, P. J. S. (1987). The performance of the octopus circulatory system: a triumph of engineering over design. Experientia, 43, 487-499\n\n"
        "#shorts #octopus #animals #science #facts"
    ),
    "tags": (
        "octopus three hearts, octopus blue blood, how many hearts does an octopus have, "
        "why is octopus blood blue, octopus facts, animal facts, ocean animals, hemocyanin explained, "
        "marine biology, amazing animal facts, science for kids, amazing science facts, "
        "science explained, 2d animation, animated explainer, quick facts, "
        "things you didn't know, zuppy science, biology explained, weird animals"
    ),
}
TITLE = META["title"]
DESC = META["description"]
TAGS = META["tags"]

RED = (235, 50, 70)
BLUE = (60, 140, 255)
YEL = (255, 205, 40)
LIL = (190, 110, 200)
COPPER = (200, 120, 60)
NAVY = (14, 28, 60)
BG2 = (200, 235, 250)
BG3 = (235, 225, 250)

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


def box(cv, cx, cy, hw, hh, label, k=1.0, fill=WHITE, size=36):
    if k <= 0.03:
        return
    rrect(cv, cx - hw * k, cy - hh * k, cx + hw * k, cy + hh * k, 16 * k, fill, 5)
    text(cv, cx, cy, label, fit(label, size, hw * 1.8), INK, scale=k)


def heart(cv, cx, cy, r, col):
    if r <= 1:
        return
    ell(cv, cx - 0.5 * r, cy - 0.35 * r, 0.55 * r, 0.55 * r, col, 0)
    ell(cv, cx + 0.5 * r, cy - 0.35 * r, 0.55 * r, 0.55 * r, col, 0)
    poly(cv, [(cx - 1.0 * r, cy - 0.05 * r), (cx + 1.0 * r, cy - 0.05 * r), (cx, cy + 1.0 * r)], col, 0)


def octo(cv, cx, cy, k=1.0, hc=RED, beat=1.0, w=0.0):
    """Осьминог с тремя сердцами внутри головы (рентген-стиль)."""
    if k <= 0.03:
        return
    for i, x0 in enumerate((-120, -72, -24, 24, 72, 120)):
        pts = [(cx + (x0 + 10 * math.sin(w + i + j * 0.7)) * k, cy + (130 + j * 22) * k) for j in range(7)]
        line(cv, pts, 36 * k, INK)
        line(cv, pts, 26 * k, LIL)
    ell(cv, cx, cy, 140 * k, 150 * k, LIL, 6)
    for sx in (-1, 1):
        ell(cv, cx + sx * 55 * k, cy + 90 * k, 24 * k, 24 * k, WHITE, 4)
        ell(cv, cx + sx * 55 * k, cy + 92 * k, 11 * k, 11 * k, INK, 0)
    heart(cv, cx, cy - 30 * k, 62 * k * beat, hc)
    heart(cv, cx - 70 * k, cy - 85 * k, 32 * k * beat, hc)
    heart(cv, cx + 70 * k, cy - 85 * k, 32 * k * beat, hc)


def hook_frame(cv, dy=0.0, beat=1.0, hc=RED, w=0.0, head=True):
    """Первый кадр Shorts: всё стоит на 100% масштаба, без появления."""
    octo(cv, 340, 285 + dy, 1.0, hc, beat, w)
    if head:
        text(cv, 340, Y1, "OCTOPUS", 58, WHITE, stroke=6)
        text(cv, 340, Y2, "THREE HEARTS", 58, YEL, stroke=6)


def s01(cv, t, T):
    # 0 three hearts (hook) | 1 blood is blue | 2 let me explain
    on = ph(t, T[0], T[0] + 0.2)
    beat = 1 + 0.15 * max(0.0, math.sin(16 * (t - T[0]))) * on
    dy = 8 * math.sin(7 * t) * on
    hc = mix(RED, BLUE, ph(t, T[1] + 0.1, T[1] + 0.4))
    hook_frame(cv, dy, beat, hc, 9 * t * on, head=(t < T[1]))
    if t < T[1]:
        text(cv, 530, 170, "x3", 80, YEL, stroke=6, scale=pop(t, T[0] + 0.5))
    elif t < T[2]:
        text(cv, 530, 170, "blue!", 64, BLUE, stroke=6, scale=pop(t, T[1] + 0.3))
    thesis(cv, t, T, 1, "BLUE BLOOD", "TOO!")
    thesis(cv, t, T, 2, "LET ME", "EXPLAIN FAST")


def s02(cv, t, T):
    # 0 two hearts: gills | 1 one heart: body | 2 copper = blue blood
    hc = mix(RED, BLUE, ph(t, T[2] + 0.2, T[2] + 0.6))
    k = pop(t, T[0] + 0.1)
    heart(cv, 130, 320, 45 * k, hc)
    heart(cv, 550, 320, 45 * k, hc)
    box(cv, 340, 320, 95, 45, "gills", pop(t, T[0] + 0.4))
    arrow(cv, 182, 320, 240, 320, 7, INK, rg(t, T[0] + 0.5, T[0] + 0.9))
    arrow(cv, 498, 320, 440, 320, 7, INK, rg(t, T[0] + 0.5, T[0] + 0.9))
    if t >= T[1]:
        heart(cv, 340, 470, 80 * pop(t, T[1] + 0.1), hc)
        arrow(cv, 340, 370, 340, 395, 7, INK, rg(t, T[1] + 0.3, T[1] + 0.6))
        text(cv, 520, 470, "body", 44, INK, scale=pop(t, T[1] + 0.5))
        arrow(cv, 430, 470, 470, 470, 7, INK, rg(t, T[1] + 0.5, T[1] + 0.9))
    if t >= T[2]:
        kc = pop(t, T[2] + 0.1)
        ell(cv, 340, 185, 55 * kc, 55 * kc, COPPER, 6)
        text(cv, 340, 185, "Cu", 52, WHITE, stroke=4, scale=kc)
    thesis(cv, t, T, 0, "TWO HEARTS:", "GILLS")
    thesis(cv, t, T, 1, "ONE HEART:", "BODY")
    thesis(cv, t, T, 2, "COPPER =", "BLUE BLOOD")


def s03(cv, t, T):
    # 0 swimming stops main heart | 1 prefer crawling | 2 loop: возврат к первому кадру
    dk = fa(t, T[2], 0.25)
    rrect(cv, -20, -20, 740, 1300, 1, mix(BG3, NAVY, dk), 0)
    if t >= T[2]:
        hook_frame(cv)
        return
    beat = 1 + 0.15 * max(0.0, math.sin(16 * t))
    if t < T[1]:
        octo(cv, 440, 330 - 40 * rg(t, T[0] + 0.2, T[0] + 0.8), 0.5, RED, 1.0, 10 * t)
        hk = pop(t, T[0] + 0.1)
        heart(cv, 140, 300, 60 * hk, RED)
        if t >= T[0] + 0.5:
            rrect(cv, 115, 275, 135, 335, 6, WHITE, 4)
            rrect(cv, 145, 275, 165, 335, 6, WHITE, 4)
        text(cv, 140, 400, "main heart", 34, INK, scale=hk)
    else:
        line(cv, [(60, 525), (600, 525)], 8, INK)
        octo(cv, 440 - 140 * rg(t, T[1] + 0.1, T[1] + 1.2), 385, 0.5, RED, 1.0, 6 * t)
        heart(cv, 140, 300, 60 * beat, RED)
        text(cv, 140, 400, "main heart", 34, INK)
    thesis(cv, t, T, 0, "SWIMMING STOPS", "MAIN HEART")
    thesis(cv, t, T, 1, "SO THEY", "CRAWL")


_FN = {"s01": s01, "s02": s02, "s03": s03}
_BG = {"s01": NAVY, "s02": BG2, "s03": BG3}
ORDER = ["s01", "s02", "s03"]
SCENES = [(_BG[k], _FN[k]) for k in ORDER]