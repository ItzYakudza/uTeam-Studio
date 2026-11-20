"""
Episode: 001_bedtime_intrusive_thoughts_2026-11-18_1200
Channel: zuppy
"""

import math
from core.primitives import *

MODE = "shorts"
CHANNEL_NAME = "zuppy"

TEXTS = [
    "The second you lie down, your brain starts a debate. "
    "It replays awkward moments and invents tomorrow's worries. "
    "Why?",
    "By day, noise and screens keep you busy. "
    "At night it goes quiet, and the leftovers surface. "
    "Worries come first.",
    "Stress keeps your brain on alert. "
    "Researchers call it pre-sleep arousal. "
    "Poor sleepers show more of it.",
    "Trying to stop them backfires. "
    "Told not to think of a white bear, people kept thinking of it. "
    "Pushing thoughts away keeps them close.",
    "So try this. "
    "Write tomorrow's to-do list for five minutes. "
    "In a sleep lab study, that beat writing about finished tasks by about nine minutes.",
    "Empty your head onto paper tonight. "
    "Give your thoughts somewhere to go. "
    "Or the debate starts again.",
]

CHAPTERS = [
    "Hook",
    "Why it happens at night",
    "Pre-sleep arousal",
    "The white bear effect",
    "The to-do list trick",
    "Loop",
]

TITLE = "Why Your Brain Overthinks Right Before Sleep #shorts"
DESC = """Why do intrusive thoughts show up the moment you lie down? Quiet, stress, and trying to push thoughts away can all keep your mind racing. A five-minute to-do list may help.

SOURCES
- Wegner, Schneider, Carter, White (1987), Paradoxical effects of thought suppression, Journal of Personality and Social Psychology 53(1): 5-13
- Harvey (2002), A cognitive model of insomnia, Behaviour Research and Therapy 40(8): 869-893
- Schmidt et al. (2011), Cognitive and affective control in insomnia, Frontiers in Psychology: https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2011.00349/full
- Scullin et al. (2018), bedtime writing study, Journal of Experimental Psychology: General. Summary: https://www2.baylor.edu/baylorproud/2018/02/trouble-falling-asleep-baylor-profs-research-identifies-a-simple-trick-that-can-help/

Educational content, not medical advice. If sleep problems last, talk to a doctor.

#sleep #psychology #shorts"""
TAGS = "sleep, overthinking, intrusive thoughts, why can't I sleep, insomnia, psychology facts, white bear effect, to-do list, sleep tips, zuppy"

RED = (210, 60, 60)
BLUE = (60, 90, 190)
YEL = (250, 200, 40)
GRN = (60, 150, 80)
PAPER = (255, 250, 235)
NIGHT = (60, 55, 110)
CXS = 340


def bub(cv, t, a, s, x, y, size=34, fill=WHITE, col=INK, maxw=500):
    k = pop(t, a)
    if k <= 0.03:
        return
    sz = fit(s, size, maxw)
    w = twidth(s, sz) / 2 + 26
    h = sz * 0.75
    rrect(cv, x - w * k, y - h * k, x + w * k, y + h * k, 18, fill, 4)
    text(cv, x, y, s, sz, col, scale=k)


def bear(cv, x, y, s=1.0):
    ell(cv, x, y, 120 * s, 85 * s, WHITE, 6)
    for dx in (-70, 60):
        rrect(cv, x + dx * s - 20 * s, y + 60 * s, x + dx * s + 20 * s, y + 120 * s, 12 * s, WHITE, 6)
    ell(cv, x - 5 * s, y - 105 * s, 70 * s, 62 * s, WHITE, 6)
    ell(cv, x - 55 * s, y - 160 * s, 22 * s, 22 * s, WHITE, 6)
    ell(cv, x + 45 * s, y - 160 * s, 22 * s, 22 * s, WHITE, 6)
    ell(cv, x - 28 * s, y - 115 * s, 6 * s, None, INK, 0)
    ell(cv, x + 22 * s, y - 115 * s, 6 * s, None, INK, 0)
    ell(cv, x - 3 * s, y - 90 * s, 12 * s, 8 * s, INK, 0)


def s01(cv, t, T):
    # 0 debate (hook) | 1 awkward + worries | 2 why?
    brain(cv, CXS, 560, 0.8)
    big(cv, t, T[0] + 0.1, "Why your brain starts", 150, 60, BLUE)
    big(cv, t, T[0] + 0.3, "a debate at night", 225, 60, BLUE)
    if t < T[2]:
        bub(cv, t, T[1] + 0.2, "Awkward moment", 250, 800, 34)
        bub(cv, t, T[1] + 1.2, "Tomorrow's worries", 390, 920, 34)
    if t >= T[2]:
        big(cv, t, T[2] + 0.1, "?", 840, 260, RED)


def s02(cv, t, T):
    # 0 by day busy | 1 night quiet | 2 leftovers surface
    night = fa(t, T[1] + 0.2, 0.8)
    rrect(cv, -20, -20, 740, 1300, 1, mix((255, 236, 214), NIGHT, night), 0)
    tc = mix(INK, WHITE, night)
    if night < 0.5:
        big(cv, t, T[0] + 0.1, "Day: noise + screens", 170, 54, INK, out=T[1])
        k = pop(t, T[0] + 0.3)
        for j in range(10):
            a = j * math.pi / 5
            line(cv, [(480 + 78 * k * math.cos(a), 420 + 78 * k * math.sin(a)),
                      (480 + 102 * k * math.cos(a), 420 + 102 * k * math.sin(a))], 6, YEL)
        ell(cv, 480, 420, 62 * k, 62 * k, YEL, 5)
        rrect(cv, 130, 340, 290, 560, 24 * k, WHITE, 6)
    else:
        big(cv, t, T[1] + 0.3, "Night: quiet", 170, 56, WHITE)
        ell(cv, 480, 420, 62, 62, WHITE, 4)
        ell(cv, 505, 405, 54, 54, NIGHT, 0)
        for sx, sy in ((150, 380), (250, 480), (360, 340), (150, 560)):
            text(cv, sx, sy, "+", 40, WHITE, scale=pop(t, T[1] + 0.6))
    bub(cv, t, T[2] + 0.1, "to-do list", 200, 700, 36)
    bub(cv, t, T[2] + 0.6, "worry", 460, 800, 36)
    bub(cv, t, T[2] + 1.1, "awkward moment", 280, 900, 36)
    if night > 0.5 and t >= T[2]:
        text(cv, CXS, 990, "leftovers surface", 40, tc, scale=pop(t, T[2] + 1.4))


def s03(cv, t, T):
    # 0 alert | 1 pre-sleep arousal | 2 poor sleepers more of it
    brain(cv, CXS, 470, 0.7)
    big(cv, t, T[0] + 0.2, "ALERT!", 215, 80, RED)
    if t >= T[0] + 0.5:
        for dx in (-130, 0, 130):
            line(cv, [(CXS + dx, 330), (CXS + dx, 305)], 8, RED)
    title(cv, t, "Pre-sleep arousal", 46, 700, a=T[1] + 0.1)
    if t >= T[2] + 0.2:
        text(cv, 90, 800, "Good sleepers", 34, INK, anchor="lm", scale=pop(t, T[2] + 0.2))
        wg = 150 * rg(t, T[2] + 0.3, T[2] + 1.0)
        rrect(cv, 90, 830, 90 + max(wg, 12), 870, 14, GRN, 5)
    if t >= T[2] + 1.0:
        text(cv, 90, 910, "Poor sleepers", 34, INK, anchor="lm", scale=pop(t, T[2] + 1.0))
        wp = 420 * rg(t, T[2] + 1.1, T[2] + 2.0)
        rrect(cv, 90, 940, 90 + max(wp, 12), 980, 14, RED, 5)


def s04(cv, t, T):
    # 0 stopping backfires | 1 white bear | 2 pushing thoughts keeps them close
    if t < T[1]:
        big(cv, t, T[0] + 0.1, "Stop thinking!", 190, 64, RED)
        k = pop(t, T[0] + 0.5)
        brain(cv, CXS, 520, 0.7 * k)
        if k > 0.9:
            ell(cv, CXS, 520, 170, 170, None, 14, RED)
            line(cv, [(CXS - 120, 400), (CXS + 120, 640)], 14, RED)
    else:
        big(cv, t, T[1] + 0.1, "Don't think of it!", 190, 60, RED)
        dx = 120 * ph(t, T[2] + 0.2, T[2] + 1.0) - 120 * ph(t, T[3] - 1.6, T[3] - 0.6)
        bear(cv, CXS + dx, 640, 1.1)
        if t >= T[2] + 0.2:
            big(cv, t, T[2] + 0.2, "Push it away...", 930, 50, RED, out=T[3] - 1.4)
            big(cv, t, T[3] - 1.4, "...it comes back", 930, 50, BLUE)


def s05(cv, t, T):
    # 0 so try this | 1 to-do list five minutes | 2 beat finished tasks by nine minutes
    big(cv, t, T[0] + 0.1, "Try this", 160, 66, GRN)
    k = pop(t, T[0] + 0.3)
    if k > 0.03:
        hw = 230 * k
        hh = 200 * k
        rrect(cv, CXS - hw, 500 - hh, CXS + hw, 500 + hh, 22, PAPER, 6)
    if k > 0.9:
        text(cv, CXS, 345, "Tomorrow", 36, BLUE)
        for j, w in enumerate(("Call mom", "Pay bills", "Finish report")):
            a = T[1] + 0.2 + 0.6 * j
            kk = pop(t, a)
            if kk > 0.03:
                y = 430 + j * 75
                rrect(cv, 140, y - 18, 176, y + 18, 6, WHITE, 4)
                text(cv, 200, y, w, 38, INK, anchor="lm", scale=kk)
        kc = pop(t, T[1] + 0.4)
        if kc > 0.05:
            clock(cv, 500, 380, 48, 0, 150, kc)
            text(cv, 500, 450, "5 min", 28, INK, scale=kc)
    if t >= T[2] + 0.2:
        text(cv, 90, 790, "To-do list", 32, INK, anchor="lm", scale=pop(t, T[2] + 0.2))
        wa = 250 * rg(t, T[2] + 0.3, T[2] + 1.0)
        rrect(cv, 90, 815, 90 + max(wa, 12), 845, 12, GRN, 5)
    if t >= T[2] + 0.8:
        text(cv, 90, 890, "Finished-task list", 32, INK, anchor="lm", scale=pop(t, T[2] + 0.8))
        wb = 400 * rg(t, T[2] + 0.9, T[2] + 1.7)
        rrect(cv, 90, 915, 90 + max(wb, 12), 945, 12, RED, 5)
    if t >= T[2] + 1.4:
        text(cv, 480, 830, "9 min faster", 34, GRN, scale=pop(t, T[2] + 1.4))


def s06(cv, t, T):
    # 0 empty head onto paper | 1 somewhere to go | 2 or the debate starts again
    brain(cv, CXS, 560, 0.8)
    if t < T[3] - 0.6:
        big(cv, t, T[0] + 0.1, "Write it down", 170, 60, BLUE, out=T[1])
        if t >= T[1]:
            big(cv, t, T[1] + 0.1, "Give it somewhere to go", 170, 54, GRN)
        kp = pop(t, T[0] + 0.3)
        if kp > 0.03:
            rrect(cv, CXS - 140 * kp, 880 - 80 * kp, CXS + 140 * kp, 880 + 80 * kp, 16, PAPER, 5)
        for j in range(4):
            p = rg(t, T[0] + 0.6 + j * 0.25, T[0] + 1.6 + j * 0.25)
            if 0.02 < p < 0.98:
                ell(cv, CXS + (j - 1.5) * 30 * (1 - p), 700 + 140 * p, 9, 9, BLUE, 0)
        if t >= T[1] + 0.2:
            for j in range(3):
                kl = rg(t, T[1] + 0.2 + j * 0.3, T[1] + 0.8 + j * 0.3)
                line(cv, [(CXS - 110, 850 + j * 30), (CXS - 110 + 220 * kl, 850 + j * 30)], 5, INK)
        if t >= T[2]:
            bub(cv, t, T[2] + 0.1, "Awkward moment", 250, 330, 34)
            bub(cv, t, T[2] + 0.6, "Tomorrow's worries", 390, 400, 34)


_FN = {"s01": s01, "s02": s02, "s03": s03, "s04": s04, "s05": s05, "s06": s06}
_BG = {
    "s01": (226, 222, 250), "s02": (255, 236, 214), "s03": (222, 232, 255),
    "s04": (255, 226, 226), "s05": (222, 247, 230), "s06": (226, 222, 250),
}
ORDER = ["s01", "s02", "s03", "s04", "s05", "s06"]
SCENES = [(_BG[k], _FN[k]) for k in ORDER]
