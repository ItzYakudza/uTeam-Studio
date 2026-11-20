"""
Episode: 002_yawn_contagious_2026-11-18_1300
Channel: zuppy
"""

import math
from core.primitives import *

MODE = "shorts"
CHANNEL_NAME = "zuppy"

TEXTS = [
    "Don't you dare yawn right now. "
    "I bet you will anyway. "
    "Here is why it happens.",
    "A yawn is weirdly contagious. "
    "Seeing one can trigger yours. "
    "Even reading about it works.",
    "About half of adults catch them. "
    "Toddlers usually do not catch them. "
    "That changes around age four or five.",
    "Dogs can catch human yawns too. "
    "Most dogs did in one study. "
    "Family and friends catch yawns most.",
    "So why do we yawn at all? "
    "One idea says yawns cool the brain. "
    "Another links them to empathy and bonding.",
    "Scientists still debate both ideas. "
    "Now be honest, did you yawn? "
    "Watch again and do not yawn.",
]

CHAPTERS = [
    "Hook",
    "Yawns are contagious",
    "Who catches them",
    "Dogs and friends",
    "Why we yawn",
    "Loop",
]

META = {
    "title": "Why Yawns Are Contagious (Try Not To Yawn)",
    "description": (
        "Yawns spread from person to person, and even to dogs. "
        "Here is what science knows about why.\n\n"
        "SOURCES:\n"
        "- Provine, R. R. (1986). Yawning as a stereotyped action pattern and releasing stimulus. Ethology, 72(2), 109-122\n"
        "- Platek, S. M., Critton, S. R., Myers, T. E., & Gallup, G. G. (2003). Contagious yawning: the role of self-awareness and mental state attribution. Cognitive Brain Research, 17(2), 223-227\n"
        "- Millen, A., & Anderson, J. R. (2011). Neither infants nor toddlers catch yawns from their mothers. Biology Letters, 7(3), 440-442\n"
        "- Joly-Mascheroni, R. M., Senju, A., & Shepherd, A. J. (2008). Dogs catch human yawns. Biology Letters, 4(5), 446-448\n"
        "- Norscia, I., & Palagi, E. (2011). Yawn contagion and empathy in Homo sapiens. PLoS ONE, 6(12): e28472. https://doi.org/10.1371/journal.pone.0028472\n"
        "- Gallup, A. C., & Gallup, G. G. (2007). Yawning as a brain cooling mechanism. Evolutionary Psychology, 5(1), 92-101\n\n"
        "Educational content, not medical advice. If you feel unusually tired all the time, talk to a doctor.\n\n"
        "#shorts #science #psychology #facts #yawn"
    ),
    "tags": (
        "why do we yawn, contagious yawning, why yawns are contagious, yawning science, "
        "do dogs catch yawns, yawn challenge, try not to yawn, psychology facts, "
        "how the brain works, empathy and yawning, why is yawning contagious, yawning explained, "
        "amazing science facts, human behavior explained, 2d animation, animated explainer, "
        "science explained, psychology of yawning, zuppy science, brain cooling theory"
    ),
}
TITLE = META["title"]
DESC = META["description"]
TAGS = META["tags"]

RED = (210, 60, 60)
BLUE = (60, 90, 190)
YEL = (250, 200, 40)
GRN = (60, 150, 80)
DARK = (24, 18, 42)
TAN = (226, 184, 132)
BROWN = (150, 100, 70)
MOUTH = (190, 60, 80)
BG6 = (226, 222, 250)

Y1 = 620  # первая строка тезиса / заголовка
Y2 = 692  # вторая строка


def thesis(cv, t, T, k, l1, l2=None, col=WHITE):
    """Тезис предложения k: виден от T[k] до T[k+1], по центру экрана."""
    if not (T[k] <= t < T[k + 1]):
        return
    sc = pop(t, T[k], 0.22)
    sz = fit(l1, 54, 500)
    if l2:
        sz = min(sz, fit(l2, 54, 500))
    text(cv, 340, Y1, l1, sz, col, stroke=6, scale=sc)
    if l2:
        text(cv, 340, Y2, l2, sz, col, stroke=6, scale=sc)


def yawn_face(cv, cx, cy, hr, k=1.0, wide=1.0):
    """Зевающее лицо: закрытые глаза + большой открытый рот."""
    r = hr * k
    if r < 4:
        return
    face(cv, cx, cy, r, max(0.8, r / 60), "sleep")
    ell(cv, cx, cy + r * 0.42, r * 0.28, r * 0.38 * wide, MOUTH, max(4, r / 25))
    ell(cv, cx, cy + r * 0.66, r * 0.16, r * 0.09, (230, 110, 120), 0)


def hook_frame(cv, dx=0.0, dy=0.0, ring=10, wide=1.0, head=True):
    """Первый кадр Shorts: всё стоит на 100% масштаба, без появления."""
    ell(cv, 340 + dx, 360 + dy, 190, 190, None, ring, RED)
    yawn_face(cv, 340 + dx, 360 + dy, 150, 1.0, wide)
    if head:
        text(cv, 340, Y1, "DON'T YOU", 58, WHITE, stroke=6)
        text(cv, 340, Y2, "DARE YAWN", 58, YEL, stroke=6)


def dog(cv, cx, cy, k=1.0):
    if k <= 0.03:
        return
    ell(cv, cx - 100 * k, cy - 10 * k, 38 * k, 78 * k, BROWN, 6)
    ell(cv, cx + 100 * k, cy - 10 * k, 38 * k, 78 * k, BROWN, 6)
    ell(cv, cx, cy, 105 * k, 92 * k, TAN, 6)
    for sgn in (-1, 1):
        ex = cx + sgn * 45 * k
        line(cv, [(ex - 16 * k, cy - 18 * k), (ex, cy - 6 * k), (ex + 16 * k, cy - 18 * k)], 6)
    ell(cv, cx, cy + 14 * k, 22 * k, 15 * k, INK, 0)
    ell(cv, cx, cy + 55 * k, 30 * k, 34 * k, MOUTH, 5)


def s01(cv, t, T):
    # 0 dare (hook) | 1 bet you will | 2 why it happens
    on = ph(t, T[0], T[0] + 0.25)
    sh = on * (1 - ph(t, T[1], T[1] + 0.3))
    dx = 7 * math.sin(60 * t) * sh
    dy = 4 * math.cos(47 * t) * sh
    ring = 10 + 6 * (0.5 + 0.5 * math.sin(14 * t)) * on
    wide = 1.0 + 0.10 * math.sin(10 * t) * ph(t, T[1], T[1] + 0.3)
    hook_frame(cv, dx, dy, ring, wide, head=(t < T[1]))
    thesis(cv, t, T, 1, "YOU WILL", "ANYWAY")
    thesis(cv, t, T, 2, "WHY IT", "HAPPENS")
    if T[1] <= t < T[2]:
        text(cv, 340, 130, "aaaah!", 44, YEL, stroke=5, scale=pop(t, T[1] + 0.2))
    if t >= T[2]:
        text(cv, 565, 190, "?", 110, RED, scale=pop(t, T[2] + 0.1))


def s02(cv, t, T):
    # 0 contagious | 1 seeing triggers | 2 reading works
    yawn_face(cv, 200, 290, 85, pop(t, T[0] + 0.15))
    k1 = pop(t, T[1] + 0.3)
    if k1 > 0.03:
        if t < T[1] + 1.0:
            face(cv, 480, 290, 85 * k1, max(0.8, 85 * k1 / 60), "flat")
        else:
            yawn_face(cv, 480, 290, 85, 1.0)
        arrow(cv, 300, 290, 380, 290, 8, RED, rg(t, T[1] + 0.1, T[1] + 0.7))
    kb = pop(t, T[2] + 0.2)
    if kb > 0.03:
        rrect(cv, 340 - 150 * kb, 480 - 60 * kb, 340 + 150 * kb, 480 + 60 * kb, 14 * kb, WHITE, 5)
        line(cv, [(340, 480 - 60 * kb), (340, 480 + 60 * kb)], 4)
        if kb > 0.9:
            text(cv, 255, 480, "yawn", 40, INK)
            text(cv, 425, 480, "yawn", 40, INK)
    thesis(cv, t, T, 0, "YAWNS ARE", "CONTAGIOUS")
    thesis(cv, t, T, 1, "SEEING ONE", "TRIGGERS YOURS")
    thesis(cv, t, T, 2, "EVEN READING", "ABOUT IT")


def s03(cv, t, T):
    # 0 half of adults | 1 toddlers | 2 age four or five
    if t < T[1]:
        for j in range(10):
            x = 130 + (j % 5) * 105
            y = 250 + (j // 5) * 130
            k = pop(t, T[0] + 0.1 + 0.1 * j)
            if k <= 0.03:
                continue
            ell(cv, x, y, 38 * k, 38 * k, RED if j < 5 else WHITE, 5)
            if k > 0.9:
                for sx in (-12, 12):
                    ell(cv, x + sx, y - 8, 4, None, INK, 0)
                if j < 5:
                    ell(cv, x, y + 10, 9, 13, (120, 30, 50), 0)
                else:
                    line(cv, [(x - 9, y + 12), (x + 9, y + 12)], 4)
        text(cv, 340, 480, "about 5 in 10 adults", 38, INK, alpha=fa(t, T[0] + 1.4))
    else:
        k = pop(t, T[1] + 0.1)
        if t < T[2]:
            face(cv, 410, 295, 75 * k, max(0.8, 75 * k / 60), "flat")
        else:
            yawn_face(cv, 410, 295, 75, 1.0)
        rrect(cv, 60, 262, 220, 328, 18, WHITE, 5)
        text(cv, 140, 295, "yawn", 40, INK, scale=k)
        arrow(cv, 226, 295, 318, 295, 7, INK, rg(t, T[1] + 0.5, T[1] + 1.0))
        if T[1] + 1.1 <= t < T[2]:
            line(cv, [(252, 272), (292, 318)], 10, RED)
            line(cv, [(292, 272), (252, 318)], 10, RED)
        text(cv, 410, 405, "toddler", 34, INK, scale=k)
        if t >= T[2]:
            arrow(cv, 100, 500, 580, 500, 6, INK, rg(t, T[2] + 0.1, T[2] + 0.7))
            mx = 100 + 340 * ph(t, T[2] + 0.2, T[2] + 1.4)
            ell(cv, mx, 500, 16, 16, RED, 4)
            text(cv, 100, 545, "age 0", 32, INK, alpha=fa(t, T[2] + 0.3))
            text(cv, 440, 545, "age 4-5", 32, INK, alpha=fa(t, T[2] + 1.2))
    thesis(cv, t, T, 0, "ABOUT HALF", "OF ADULTS")
    thesis(cv, t, T, 1, "TODDLERS", "USUALLY DON'T")
    thesis(cv, t, T, 2, "AGE FOUR", "OR FIVE")


def s04(cv, t, T):
    # 0 dogs catch yawns | 1 most dogs | 2 family and friends most
    dog(cv, 340, 300, pop(t, T[0] + 0.15))
    text(cv, 340, 160, "aaah!", 44, RED, scale=pop(t, T[0] + 0.6))
    if T[1] <= t < T[2]:
        meter(cv, t, 870, 0.72 * rg(t, T[1] + 0.3, T[1] + 1.3), RED, "dogs that yawned", T[1] + 0.2)
    if t >= T[2]:
        for j, (name, w, col) in enumerate((("Family", 430, RED), ("Friends", 300, YEL), ("Strangers", 140, BLUE))):
            a = T[2] + 0.2 + 0.5 * j
            y = 790 + j * 80
            text(cv, 90, y, name, 32, INK, anchor="lm", scale=pop(t, a))
            if t >= a + 0.1:
                rrect(cv, 90, y + 18, 90 + max(w * rg(t, a + 0.1, a + 0.8), 12), y + 44, 10, col, 5)
    thesis(cv, t, T, 0, "DOGS CATCH", "YAWNS TOO")
    thesis(cv, t, T, 1, "MOST DOGS", "CAUGHT ONE")
    thesis(cv, t, T, 2, "CLOSER BOND", "MORE YAWNS")


def s05(cv, t, T):
    # 0 why yawn | 1 cool the brain | 2 empathy and bonding
    brain(cv, 340, 390, pop(t, T[0] + 0.1), 0.8)
    if t < T[1]:
        text(cv, 340, 170, "?", 110, RED, scale=pop(t, T[0] + 0.3))
    if T[1] <= t < T[2]:
        for j, dx in enumerate((-90, 0, 90)):
            arrow(cv, 340 + dx, 160, 340 + dx * 0.7, 250, 9, BLUE, rg(t, T[1] + 0.3 + 0.15 * j, T[1] + 0.9 + 0.15 * j))
        text(cv, 340, 118, "cool!", 44, BLUE, scale=pop(t, T[1] + 0.2))
    if t >= T[2]:
        k = pop(t, T[2] + 0.2)
        if k > 0.03:
            face(cv, 200, 880, 55 * k, max(0.8, 0.9 * k), "smile")
            face(cv, 480, 880, 55 * k, max(0.8, 0.9 * k), "smile")
            ell(cv, 326, 868, 22 * k, 22 * k, RED, 0)
            ell(cv, 354, 868, 22 * k, 22 * k, RED, 0)
            poly(cv, [(306 + 34 * (1 - k), 880), (374 - 34 * (1 - k), 880), (340, 880 + 45 * k)], RED, 0)
    thesis(cv, t, T, 0, "WHY DO", "WE YAWN?")
    thesis(cv, t, T, 1, "ONE IDEA:", "BRAIN COOLING")
    thesis(cv, t, T, 2, "ANOTHER IDEA:", "EMPATHY")


def s06(cv, t, T):
    # 0 still debated | 1 did you yawn | 2 loop: возврат к первому кадру
    dk = fa(t, T[2], 0.3)
    rrect(cv, -20, -20, 740, 1300, 1, mix(BG6, DARK, dk), 0)
    if t < T[1]:
        k = pop(t, T[0] + 0.15)
        if k > 0.03:
            for cx, hw, label in ((185, 135, "Brain cooling"), (475, 130, "Empathy")):
                rrect(cv, cx - hw * k, 310 - 60 * k, cx + hw * k, 310 + 60 * k, 18 * k, WHITE, 5)
                text(cv, cx, 310, label, fit(label, 36, 220), INK, scale=k)
        text(cv, 340, 470, "?", 110, RED, scale=pop(t, T[0] + 0.7))
        thesis(cv, t, T, 0, "STILL", "DEBATED")
    else:
        yawn_face(cv, 340, 360, 150, pop(t, T[1] + 0.1))
        thesis(cv, t, T, 1, "DID YOU", "YAWN?")
        if t >= T[2]:
            ell(cv, 340, 360, 190, 190, None, 10, mix(BG6, RED, dk))
            text(cv, 340, Y1, "DON'T YOU", 58, WHITE, stroke=6)
            text(cv, 340, Y2, "DARE YAWN", 58, YEL, stroke=6)


_FN = {"s01": s01, "s02": s02, "s03": s03, "s04": s04, "s05": s05, "s06": s06}
_BG = {
    "s01": DARK, "s02": (255, 236, 214), "s03": (222, 232, 255),
    "s04": (222, 247, 230), "s05": (255, 226, 226), "s06": BG6,
}
ORDER = ["s01", "s02", "s03", "s04", "s05", "s06"]
SCENES = [(_BG[k], _FN[k]) for k in ORDER]
