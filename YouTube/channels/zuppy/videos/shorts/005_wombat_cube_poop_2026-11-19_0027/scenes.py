"""
Episode: 006_wombat_cube_poop_2026-11-19_1500
Channel: zuppy
Experimental: 18 seconds, high energy, hook-first
"""

import math
from core.primitives import *

MODE = "shorts"
CHANNEL_NAME = "zuppy"

TEXTS = [
    "Wombats poop perfect cubes. "
    "No other animal does it. "
    "Here is the secret.",
    "The secret is their gut. "
    "Stiff and stretchy parts alternate. "
    "That squeezes waste into cubes.",
    "Cubes may stay put. "
    "Scientists think that marks territory. "
    "Watch again, count corners.",
]

CHAPTERS = [
    "Hook",
    "The secret gut",
    "Why cubes",
]

META = {
    "title": "Why Wombats Poop Cubes (Seriously)",
    "description": (
        "Wombats are the only known animal that poops cubes. "
        "Here is the quick science behind it.\n\n"
        "SOURCES:\n"
        "- Royal Society of Chemistry: Wombat research that's not to be sniffed at (Soft Matter, 2021). https://www.rsc.org/news-events/articles/2021/jan/wombat-poo/\n"
        "- ScienceAlert: Wombats Have Cube-Shaped Faeces. Scientists Just Figured Out How They Poo It. https://www.sciencealert.com/wombats-have-cube-shaped-faeces-scientists-just-figured-out-how-they-poo-it\n"
        "- Gizmodo: Scientists Learn Even More About Wombats and Their Beautiful Cube-Shaped Poop. https://gizmodo.com/scientists-learn-even-more-about-wombats-and-their-beau-1846159392\n\n"
        "#shorts #wombat #animals #science #facts"
    ),
    "tags": (
        "wombat cube poop, why do wombats poop cubes, wombat facts, cube shaped poop, "
        "animal facts, weird animals, australian animals, wombat intestine, "
        "bizarre animal facts, funny science facts, science for kids, amazing science facts, "
        "science explained, 2d animation, animated explainer, quick facts, "
        "things you didn't know, zuppy science, biology explained, mind blowing animal facts"
    ),
}
TITLE = META["title"]
DESC = META["description"]
TAGS = META["tags"]

YEL = (255, 205, 40)
RED = (210, 60, 60)
SKY = (60, 170, 240)
BG2 = (255, 240, 215)
BG3 = (255, 226, 215)
GREY = (170, 170, 180)
GUT = (235, 150, 150)
STIFF = (200, 70, 80)
STRETCH = (245, 180, 185)
POOP = (130, 85, 55)

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


def cube(cv, cx, cy, s):
    """Изометрический куб: верх, левая и правая грани."""
    if s <= 2:
        return
    poly(cv, [(cx - s, cy - s * 0.5), (cx, cy), (cx, cy + s), (cx - s, cy + s * 0.5)], (120, 78, 48), 6)
    poly(cv, [(cx, cy), (cx + s, cy - s * 0.5), (cx + s, cy + s * 0.5), (cx, cy + s)], (148, 98, 62), 6)
    poly(cv, [(cx, cy - s), (cx + s, cy - s * 0.5), (cx, cy), (cx - s, cy - s * 0.5)], (175, 120, 75), 6)


def star(cv, x, y, r):
    if r <= 1:
        return
    poly(cv, [(x, y - r), (x + 0.25 * r, y - 0.25 * r), (x + r, y), (x + 0.25 * r, y + 0.25 * r),
              (x, y + r), (x - 0.25 * r, y + 0.25 * r), (x - r, y), (x - 0.25 * r, y - 0.25 * r)], YEL, 4)


def hook_frame(cv, sc=1.0, dy=0.0, tw=0.0, head=True):
    """Первый кадр Shorts: всё стоит на 100% масштаба, без появления."""
    cube(cv, 340, 340 + dy, 150 * sc)
    for x, y in ((170, 230), (520, 250), (500, 440)):
        star(cv, x, y, 22 * (1 + tw))
    if head:
        text(cv, 340, Y1, "WOMBATS POOP", 58, WHITE, stroke=6)
        text(cv, 340, Y2, "CUBES", 58, YEL, stroke=6)


def s01(cv, t, T):
    # 0 wombats poop cubes (hook) | 1 no other animal | 2 here is the secret
    on = ph(t, T[0], T[0] + 0.2)
    sc = 1 + 0.05 * math.sin(24 * (t - T[0])) * on
    dy = 8 * math.sin(9 * t) * on
    tw = 0.35 * math.sin(20 * t) * on
    hook_frame(cv, sc, dy, tw, head=(t < T[1]))
    if T[1] <= t < T[2]:
        s = "ONLY WOMBATS!"
        text(cv, 340, 125, s, fit(s, 56, 520), YEL, stroke=6, scale=pop(t, T[1] + 0.2))
    if t >= T[2]:
        text(cv, 110, 300, "?", 120, RED, stroke=6, scale=pop(t, T[2] + 0.1))
        text(cv, 570, 300, "?", 120, RED, stroke=6, scale=pop(t, T[2] + 0.25))
    thesis(cv, t, T, 1, "NO OTHER", "ANIMAL DOES IT")
    thesis(cv, t, T, 2, "THE SECRET", "IS INSIDE")


def s02(cv, t, T):
    # 0 the gut | 1 stiff and stretchy alternate | 2 squeezes into cubes
    if t < T[1]:
        pts = [(80 + 520 * i / 24, 330 + 50 * math.sin(i * 0.7)) for i in range(25)]
        n = int(25 * rg(t, T[0] + 0.1, T[0] + 0.9))
        if n >= 2:
            line(cv, pts[:n], 60, INK)
            line(cv, pts[:n], 48, GUT)
        text(cv, 340, 450, "intestine", 40, INK, alpha=fa(t, T[0] + 0.8))
    elif t < T[2]:
        kk = pop(t, T[1] + 0.1)
        for i in range(8):
            a0 = math.radians(i * 45 - 22.5)
            a1 = math.radians((i + 1) * 45 - 22.5)
            pts = [(340, 320)]
            for j in range(7):
                a = a0 + (a1 - a0) * j / 6
                pts.append((340 + 120 * kk * math.cos(a), 320 + 120 * kk * math.sin(a)))
            poly(cv, pts, STIFF if i % 2 == 0 else STRETCH, 4)
        if t >= T[1] + 0.6:
            rrect(cv, 70, 480, 110, 520, 6, STIFF, 4)
            text(cv, 130, 500, "stiff", 34, INK, anchor="lm")
            rrect(cv, 330, 480, 370, 520, 6, STRETCH, 4)
            text(cv, 390, 500, "stretchy", 34, INK, anchor="lm")
    else:
        p = rg(t, T[2] + 0.3, T[2] + 1.2)
        rrect(cv, 230, 210, 450, 430, max(8, 110 * (1 - p)), POOP, 6)
        a = rg(t, T[2] + 0.1, T[2] + 0.4)
        arrow(cv, 130, 320, 205, 320, 9, RED, a)
        arrow(cv, 550, 320, 475, 320, 9, RED, a)
        arrow(cv, 340, 150, 340, 203, 9, RED, a)
        arrow(cv, 340, 490, 340, 437, 9, RED, a)
    thesis(cv, t, T, 0, "THE SECRET", "IS THE GUT")
    thesis(cv, t, T, 1, "STIFF + STRETCHY", "PARTS")
    thesis(cv, t, T, 2, "SQUEEZED", "INTO CUBES")


def s03(cv, t, T):
    # 0 cubes may stay put | 1 marks territory | 2 loop: возврат к первому кадру
    dk = fa(t, T[2], 0.25)
    rrect(cv, -20, -20, 740, 1300, 1, mix(BG3, SKY, dk), 0)
    if t >= T[2]:
        hook_frame(cv)
        return
    ell(cv, 340, 470, 210, 60, GREY, 6)
    cube(cv, 270, 390, 55 * pop(t, T[0] + 0.15))
    cube(cv, 410, 390, 55 * pop(t, T[0] + 0.4))
    cube(cv, 340, 335, 55 * pop(t, T[0] + 0.65))
    if t >= T[1]:
        box(cv, 500, 205, 105, 38, "my turf!", pop(t, T[1] + 0.3))
        arrow(cv, 455, 246, 405, 295, 7, RED, rg(t, T[1] + 0.5, T[1] + 0.9))
    thesis(cv, t, T, 0, "CUBES MAY", "STAY PUT")
    thesis(cv, t, T, 1, "MARKING", "TERRITORY")


_FN = {"s01": s01, "s02": s02, "s03": s03}
_BG = {"s01": SKY, "s02": BG2, "s03": BG3}
ORDER = ["s01", "s02", "s03"]
SCENES = [(_BG[k], _FN[k]) for k in ORDER]