"""
Episode: 006_stopped_clock_illusion_2026-11-20_1000
Channel: zuppy
Topic: saccadic chronostasis (stopped-clock illusion), ~40 s, hook-first, loop ending
"""

import math
from core.toolkit import *

MODE = "shorts"
CHANNEL_NAME = "zuppy"

TEXTS = [
    "Stare at the red dot. "
    "Now snap your eyes to the clock. "
    "Did that first tick feel longer?",
    "You're not imagining it. "
    "Scientists call it chronostasis. "
    "That literally means time standing still.",
    "Your eyes jump several times every second. "
    "During each jump, your vision mostly shuts off. "
    "You never notice the blackout.",
    "So your brain fills the gap. "
    "It stretches the new image backward in time. "
    "That's why the first second drags.",
    "It happens every time you look around. "
    "You only catch it with a clock. "
    "Be honest: did yours freeze?",
]

CHAPTERS = [
    "Hook: the clock test",
    "Chronostasis",
    "Blind eye jumps",
    "Brain edits time",
    "Loop: test again",
]

META = {
    "title": "The Clock Illusion Everyone Falls For (Test Yourself)",
    "description": (
        "Stare at the dot, snap your eyes to the clock, and the first tick seems to last longer. "
        "Your brain is quietly editing time, and this is how it does it.\n\n"
        "SOURCES:\n"
        "- Yarrow, K., Haggard, P., Heal, R., Brown, P., & Rothwell, J. C. (2001). Illusory perceptions of space "
        "and time preserve cross-saccadic perceptual continuity. Nature, 414(6861), 302-305. doi:10.1038/35104551\n"
        "- Ross, J., Morrone, M. C., Goldberg, M. E., & Burr, D. C. (2001). Changes in visual perception at the "
        "time of saccades. Trends in Neurosciences, 24(2), 113-121.\n\n"
        "#shorts #psychology #illusion #neuroscience #brain"
    ),
    "tags": (
        "stopped clock illusion, chronostasis, time illusion, saccadic chronostasis, brain illusion test, "
        "optical illusion, time perception, why does the first second feel longer, clock looks frozen, "
        "eye movement illusion, saccade, perception test, psychology facts, neuroscience facts, "
        "science explained, 2d animation, animated explainer, brain tricks, mind blowing facts, zuppy science"
    ),
    "pinned_comment": "Did the first tick freeze for you? Yes or No, be honest 👇",
}
TITLE = META["title"]
DESC = META["description"]
TAGS = META["tags"]

# ---------------- палитра ----------------
RED = (235, 50, 70)
YEL = (255, 205, 40)
BLUE = (60, 140, 255)
VIO = (36, 16, 92)        # контрастный фон хука
BG2 = (205, 232, 250)
BG3 = (236, 226, 250)
BG4 = (255, 240, 215)
BG5 = (214, 244, 228)

Y1 = 790   # первая строка тезиса
Y2 = 862   # вторая строка

DOT = (130, 320)           # красная точка (левый верх)
CLK = (400, 540, 170)      # часы: x, y, r (диаметр 340 = 47% ширины)


def thesis(cv, t, T, k, l1, l2=None, col=WHITE, sc_col=None):
    """Тезис предложения k: виден от T[k] до T[k+1]."""
    if not (T[k] <= t < T[k + 1]):
        return
    cx = cv.cfg.center_x
    sc = pop(t, T[k], 0.18)
    sz = fit_safe(cv, l1, 56)
    if l2:
        sz = min(sz, fit_safe(cv, l2, 56))
    text(cv, cx, Y1, l1, sz, col, stroke=6, scale=sc)
    if l2:
        text(cv, cx, Y2, l2, sz, sc_col or col, stroke=6, scale=sc)


def tick_ang(t, step=30.0):
    """Секундная стрелка: прыгает раз в секунду, лёгкий «дребезг» при щелчке."""
    n = int(max(0.0, t))
    f = t - n
    k = ph(f, 0.0, 0.09)
    over = 0.18 * max(0.0, math.sin(math.pi * seg(f, 0.09, 0.25))) * (1 if f > 0.09 else 0)
    return step * (n + k + over)


def clock_face(cv, x, y, r, t, glow=0.0, hand_col=RED):
    if glow > 0.02:
        ell(cv, x, y, r + 16 * glow, fill=None, w=10, col=mix(cv.bg, YEL, glow))
    ell(cv, x, y, r, fill=WHITE, w=7)
    for i in range(12):
        a = math.radians(i * 30 - 90)
        line(cv, [(x + math.cos(a) * r * 0.80, y + math.sin(a) * r * 0.80),
                  (x + math.cos(a) * r * 0.93, y + math.sin(a) * r * 0.93)], 6)
    a = math.radians(tick_ang(t) - 90)
    line(cv, [(x - math.cos(a) * r * 0.16, y - math.sin(a) * r * 0.16),
              (x + math.cos(a) * r * 0.80, y + math.sin(a) * r * 0.80)], 8, hand_col)
    ell(cv, x, y, 11, fill=INK, w=0)


def red_dot(cv, t, k=1.0):
    pr = 1 + 0.12 * math.sin(t * 9)
    ell(cv, DOT[0], DOT[1], 40 * pr * k, fill=RED, w=6)
    ell(cv, DOT[0] - 12 * k, DOT[1] - 12 * k, 10 * k, fill=(255, 150, 160), w=0)
    ripple(cv, t, 0.0, DOT[0], DOT[1], 80, 2, 1.0, RED, 4)


def hook_frame(cv, t, head=("STARE AT THE", "RED DOT"), dot=True):
    """Кадр-хук (и кадр-петля): всё на 100% с t=0, активная микро-анимация."""
    cx = cv.cfg.center_x
    tx_label(cv, cx, 135, "EYE TEST", 40, YEL, INK, rot=-3, k=1.0)
    if dot:
        red_dot(cv, t)
    clock_face(cv, CLK[0], CLK[1], CLK[2], t)
    jit = 3 * math.sin(t * 22)
    text(cv, cx + jit, Y1, head[0], fit_safe(cv, head[0], 58), WHITE, stroke=6)
    text(cv, cx - jit, Y2, head[1], fit_safe(cv, head[1], 62), RED if "RED" in head[1] else YEL, stroke=6)


def s01(cv, t, T):
    # 0 stare at the red dot (hook) | 1 snap eyes to clock | 2 first tick longer?
    cx = cv.cfg.center_x
    if t < T[1]:
        hook_frame(cv, t)
        return
    tx_label(cv, cx, 135, "EYE TEST", 40, YEL, INK, rot=-3)
    glow = fa(t, T[1] + 0.1, 0.3)
    clock_face(cv, CLK[0], CLK[1], CLK[2], t, glow=glow)
    if t < T[1] + 0.7:
        burst(cv, t, T[1], DOT[0], DOT[1], 70, 10, RED, 0.5)
    k = rg(t, T[1] + 0.05, T[1] + 0.5)
    if k > 0.02 and t < T[2]:
        arrow(cv, DOT[0] + 50, DOT[1] + 40, CLK[0] - 105, CLK[1] - 125, 10, YEL, k)
    if t >= T[2]:
        q = pop(t, T[2] + 0.2)
        text(cv, CLK[0] + 20, CLK[1] - CLK[2] - 50, "?", 90, YEL, stroke=6, scale=q)
        emphasis(cv, t, CLK[0], CLK[1], CLK[2] + 10, 9, YEL, 6, 24, 8, 200)
    thesis(cv, t, T, 1, "SNAP YOUR EYES", "TO THE CLOCK", sc_col=YEL)
    thesis(cv, t, T, 2, "FIRST TICK", "LONGER?", sc_col=YEL)


def s02(cv, t, T):
    # 0 not imagining | 1 scientists call it chronostasis | 2 time standing still
    cx = cv.cfg.center_x
    if t < T[1]:
        k = pop(t, T[0] + 0.1)
        cloud_shape(cv, cx, 420, 400 * max(k, 0.01), WHITE, 6)
        text(cv, cx, 425, "imagination", fit_safe(cv, "imagination", 40), INK, scale=k)
        crossmark(cv, cx, 425, 150, RED, 16, rg(t, T[0] + 0.7, T[0] + 1.3))
    elif t < T[2]:
        k = pop(t, T[1] + 0.1)
        rrect(cv, cx - 200 * k, 330 - 150 * k, cx + 200 * k, 330 + 150 * k, 22, WHITE, 6)
        text(cv, cx, 270, "NATURE", 46, RED, scale=k)
        text(cv, cx, 340, "2001", 70, INK, scale=k)
        text(cv, cx, 405, "Yarrow et al.", 34, (90, 90, 110), scale=k)
        tx_label(cv, cx, 560, "chronostasis", fit_safe(cv, "chronostasis", 54), YEL, INK, rot=-3,
                 k=pop(t, T[1] + 0.5))
    else:
        k = pop(t, T[2] + 0.1)
        clock(cv, cx - 150, 400, 95, 300, 60, k)
        text(cv, cx - 150, 540, "chronos", 40, INK, scale=k)
        text(cv, cx - 150, 585, "= time", 36, (90, 90, 110), scale=k)
        k2 = pop(t, T[2] + 0.9)
        ell(cv, cx + 150, 400, 95 * max(k2, 0.01), fill=BLUE, w=6)
        rrect(cv, cx + 120, 365, cx + 143, 435, 6, WHITE, 0)
        rrect(cv, cx + 157, 365, cx + 180, 435, 6, WHITE, 0)
        text(cv, cx + 150, 540, "stasis", 40, INK, scale=k2)
        text(cv, cx + 150, 585, "= standing", 36, (90, 90, 110), scale=k2)
    thesis(cv, t, T, 0, "NOT", "IMAGINATION", col=WHITE, sc_col=YEL)
    thesis(cv, t, T, 1, "CHRONOSTASIS", None)
    thesis(cv, t, T, 2, "TIME STANDING", "STILL", sc_col=YEL)


def eye(cv, cx, cy, px, k=1.0, shut=0.0):
    if k <= 0.03:
        return
    h = 120 * k * (1 - 0.92 * shut)
    pts = [(cx - 190 * k, cy), (cx - 95 * k, cy - h), (cx + 95 * k, cy - h), (cx + 190 * k, cy),
           (cx + 95 * k, cy + h), (cx - 95 * k, cy + h)]
    poly(cv, pts, WHITE, 7)
    if shut < 0.8:
        ell(cv, cx + px * k, cy, 62 * k, fill=(90, 150, 240), w=5)
        ell(cv, cx + px * k, cy, 28 * k, fill=INK, w=0)


def s03(cv, t, T):
    # 0 eyes jump several times | 1 vision mostly shuts off | 2 never notice blackout
    cx = cv.cfg.center_x
    fx = (-95, 95, -30, 95)
    if t < T[1]:
        n = int(max(0.0, (t - T[0] - 0.2) / 0.55))
        px = fx[n % 4]
        px0 = fx[(n - 1) % 4] if n > 0 else px
        f = ph((t - T[0] - 0.2) % 0.55, 0.0, 0.08)
        eye(cv, cx, 400, px0 + (px - px0) * f, pop(t, T[0] + 0.0))
        for i, d in enumerate((-95, 95, -30)):
            ell(cv, cx + d, 590, 10 * pop(t, T[0] + 0.3 + i * 0.3), fill=RED, w=0)
        if n > 0:
            motion_trail(cv, cx + px0 * 0.8, 400, cx + px * 0.8, 400, 3, INK, 5, 16)
    else:
        sh = fa(t, T[1] + 0.1, 0.25) * (1 - 0.0 * fa(t, T[2], 0.2))
        eye(cv, cx, 330, 0, 1.0, shut=0.9 * sh if t < T[2] else 0.9)
        # лента зрения: светлое — видим, тёмное — «глухие» провалы при скачках
        x0, y0 = cx - 250, 560
        for i in range(5):
            dark = i % 2 == 1
            w = 70 if dark else 60
            xs = x0 + i * 100
            kk = pop(t, T[1] + 0.2 + i * 0.12, 0.25)
            rrect(cv, xs, y0 - 45 * kk, xs + w * kk, y0 + 45 * kk, 8,
                  (30, 30, 50) if dark else (255, 236, 150), 5)
        if t >= T[2]:
            for i in (1, 3):
                text(cv, x0 + i * 100 + 35, y0 + 4, "?", 52, YEL, stroke=3, scale=pop(t, T[2] + 0.1 * i))
    thesis(cv, t, T, 0, "EYES JUMP", "SEVERAL TIMES/SEC", sc_col=YEL)
    thesis(cv, t, T, 1, "VISION MOSTLY", "SHUTS OFF", sc_col=YEL)
    thesis(cv, t, T, 2, "YOU NEVER", "NOTICE", sc_col=YEL)


def s04(cv, t, T):
    # 0 brain fills the gap | 1 stretches new image backward | 2 first second drags
    cx = cv.cfg.center_x
    y0 = 520
    gap_a, gap_b = cx - 60, cx + 60
    new_a = gap_b
    if t >= T[1]:
        new_a = gap_b - (gap_b - gap_a) * rg(t, T[1] + 0.2, T[1] + 1.4)
    rrect(cv, 70, y0 - 50, gap_a, y0 + 50, 10, (150, 190, 255), 5)
    text(cv, (70 + gap_a) / 2, y0 + 90, "old", 34, INK)
    if t < T[1]:
        rrect(cv, gap_a, y0 - 50, gap_b, y0 + 50, 10, (30, 30, 50), 5)
        text(cv, cx, y0, "?", 56, YEL, stroke=3, scale=pop(t, T[0] + 0.3))
    rrect(cv, new_a, y0 - 50, 600, y0 + 50, 10, (255, 214, 90), 5)
    text(cv, (new_a + 600) / 2 + 20, y0 + 90, "new image", fit_safe(cv, "new image", 34), INK)
    brain(cv, cx, 255, 0.9, 1.0 + 0.04 * math.sin(t * 8) if t >= T[0] else 1.0)
    k = pop(t, T[0] + 0.1)
    if t >= T[1]:
        arrow(cv, 560, y0 - 90, 330, y0 - 90, 8, RED, rg(t, T[1] + 0.2, T[1] + 1.2))
        text(cv, cx + 30, y0 - 125, "backward in time", fit_safe(cv, "backward in time", 36), RED,
             alpha=fa(t, T[1] + 0.3))
    if t >= T[2]:
        rrect(cv, 90, 655, 90 + 190 * pop(t, T[2] + 0.1), 693, 10, (255, 214, 90), 5)
        text(cv, 90 + 100, 674, "real 1 s", 28, INK, alpha=fa(t, T[2] + 0.2))
        rrect(cv, 90, 708, 90 + 330 * pop(t, T[2] + 0.5), 746, 10, (255, 150, 90), 5)
        text(cv, 90 + 170, 727, "felt: longer", 28, INK, alpha=fa(t, T[2] + 0.6))
    thesis(cv, t, T, 0, "BRAIN FILLS", "THE GAP", sc_col=YEL)
    thesis(cv, t, T, 1, "STRETCHES IT", "BACKWARD", sc_col=YEL)
    thesis(cv, t, T, 2, "FIRST SECOND", "DRAGS", sc_col=YEL)


def s05(cv, t, T):
    # 0 happens every glance | 1 catch it with a clock | 2 loop: возврат к первому кадру
    cx = cv.cfg.center_x
    dk = fa(t, T[2], 0.25)
    rrect(cv, -20, -20, 740, 1300, 1, mix(BG5, VIO, dk), 0)
    if t >= T[2]:
        late = t > T[3] - 0.7
        head = ("STARE AT THE", "RED DOT") if late else ("DID YOURS", "FREEZE?")
        hook_frame(cv, t, head)
        return
    if t < T[1]:
        pts = [(cx - 150, 400), (cx + 150, 400), (cx, 600)]
        for i, (px, py) in enumerate(pts):
            ell(cv, px, py, 36 * pop(t, T[0] + 0.1 + i * 0.3), fill=(90, 150, 240), w=6)
        for i in range(3):
            a, b = pts[i], pts[(i + 1) % 3]
            arrow(cv, a[0], a[1], b[0], b[1], 7, INK, rg(t, T[0] + 0.5 + i * 0.4, T[0] + 0.9 + i * 0.4))
    else:
        clock_face(cv, cx, 520, 160 * pop(t, T[1] + 0.1), t, glow=fa(t, T[1] + 0.5, 0.3))
    thesis(cv, t, T, 0, "EVERY TIME", "YOU LOOK AROUND", sc_col=YEL)
    thesis(cv, t, T, 1, "YOU NEED", "A CLOCK TO CATCH IT", sc_col=YEL)


TRANSITIONS = {}

_FN = {"s01": s01, "s02": s02, "s03": s03, "s04": s04, "s05": s05}
_BG = {"s01": VIO, "s02": BG2, "s03": BG3, "s04": BG4, "s05": BG5}
ORDER = ["s01", "s02", "s03", "s04", "s05"]
SCENES = [(_BG[k], _FN[k]) for k in ORDER]
