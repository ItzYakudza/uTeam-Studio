"""
uTeam-Studio
core/props.py — библиотека предметов (prop_*), собранных из конструктора kit.
Общая сигнатура:  prop_xxx(cv, x, y, s=1.0, k=1.0, rot=0, flip=False, alpha=1.0, **особые)
  (x, y) — центр предмета, s — масштаб (100 ед. ≈ высота предмета), k — появление (pop(t, a) -> 0..1.2),
  rot — поворот. Любой предмет можно положить в group() / cam() / layer().
"""

import math
from functools import wraps

from .config import INK, WHITE
from .primitives import Canvas, line, poly, ell, rrect, text, mix
from .stage import group
from .kit import (PAL, rectangle, rect_c, star_poly, heart_shape, cloud_shape, blob_shape, capsule,
                  gear_shape, curve, tube, darken, lighten, regpoly)


def _prop(fn):
    @wraps(fn)
    def wrapper(cv, x, y, s=1.0, k=1.0, rot=0.0, flip=False, alpha=1.0, **kw):
        if k <= 0.03:
            return
        with group(cv, x, y, rot=rot, sc=s * k, flip=flip, alpha=alpha):
            fn(cv, **kw)
    return wrapper


@_prop
def prop_sun(cv, t=0.0, face=True):
    for i in range(12):
        a = math.radians(i * 30 + t * 18)
        line(cv, [(math.cos(a) * 56, math.sin(a) * 56), (math.cos(a) * (72 + 6 * math.sin(t * 3 + i)), math.sin(a) * (72 + 6 * math.sin(t * 3 + i)))], 7, PAL["orange"])
    ell(cv, 0, 0, 44, fill=PAL["yellow"], w=6)
    if face:
        for sg in (-1, 1):
            ell(cv, sg * 15, -6, 4.5, fill=INK, w=0)
        line(cv, [(-16, 12), (0, 22), (16, 12)], 4)


@_prop
def prop_moon(cv, face=True, fill=PAL["lemon"]):
    R, r, d = 46.0, 38.0, 24.0
    xi = (d * d + R * R - r * r) / (2 * d)
    yi = math.sqrt(max(R * R - xi * xi, 0))
    a0 = math.atan2(yi, xi)
    b0 = math.atan2(yi, xi - d)
    pts = [(R * math.cos(a0 + (2 * math.pi - 2 * a0) * i / 40), R * math.sin(a0 + (2 * math.pi - 2 * a0) * i / 40)) for i in range(41)]
    pts += [(d + r * math.cos(2 * math.pi - b0 - (2 * math.pi - 2 * b0) * i / 40),
             r * math.sin(2 * math.pi - b0 - (2 * math.pi - 2 * b0) * i / 40)) for i in range(41)]
    poly(cv, pts, fill, 6)
    if face:
        ell(cv, -26, -4, 3.5, fill=INK, w=0)
        line(cv, [(-34, 14), (-26, 20), (-18, 14)], 3.5)


@_prop
def prop_tree(cv, fruit=False):
    rrect(cv, -12, 10, 12, 70, 5, PAL["wood"], 6)
    for dx, dy, r in ((-30, -10, 36), (30, -10, 36), (0, -38, 40), (0, 4, 34)):
        ell(cv, dx, dy, r + 3, fill=INK, w=0)
    for dx, dy, r in ((-30, -10, 36), (30, -10, 36), (0, -38, 40), (0, 4, 34)):
        ell(cv, dx, dy, r - 3, fill=PAL["green"], w=0)
    if fruit:
        for dx, dy in ((-22, -18), (20, -30), (6, 2), (-4, -48)):
            ell(cv, dx, dy, 8, fill=PAL["red"], w=3.5)


@_prop
def prop_house(cv, smoke_t=None):
    rectangle(cv, -55, -5, 55, 62, PAL["sand"], 6)
    poly(cv, [(-70, -5), (0, -62), (70, -5)], PAL["red"], 6)
    rrect(cv, -12, 20, 14, 62, 4, PAL["wood"], 5)
    rectangle(cv, -42, 12, -20, 34, PAL["sky"], 5)
    rectangle(cv, 24, 12, 46, 34, PAL["sky"], 5)
    rectangle(cv, 28, -50, 44, -22, PAL["gray"], 5)
    if smoke_t is not None:
        for i in range(3):
            f = (smoke_t * 0.5 + i / 3) % 1
            ell(cv, 36 + f * 14, -58 - f * 46, 7 + f * 9, fill=mix((255, 255, 255), cv.bg, f * 0.7), w=3)


@_prop
def prop_car(cv, t=0.0, body=PAL["blue"]):
    poly(cv, [(-70, 20), (-70, -4), (-40, -10), (-24, -40), (30, -40), (50, -10), (72, -4), (72, 20)], body, 6)
    poly(cv, [(-30, -10), (-18, -33), (8, -33), (8, -10)], PAL["sky"], 5)
    poly(cv, [(16, -10), (16, -33), (28, -33), (42, -10)], PAL["sky"], 5)
    for wx in (-40, 40):
        ell(cv, wx, 24, 20, fill=PAL["dark"], w=6)
        ell(cv, wx, 24, 8, fill=PAL["gray"], w=3)
        a = t * 8
        line(cv, [(wx, 24), (wx + 8 * math.cos(a), 24 + 8 * math.sin(a))], 3, INK)


@_prop
def prop_book(cv, col=PAL["red"], open_book=False):
    if open_book:
        poly(cv, [(-70, -40), (0, -30), (0, 44), (-70, 34)], WHITE, 6)
        poly(cv, [(70, -40), (0, -30), (0, 44), (70, 34)], WHITE, 6)
        for i in range(4):
            line(cv, [(-58, -16 + i * 14), (-12, -10 + i * 14)], 3, PAL["gray"])
            line(cv, [(58, -16 + i * 14), (12, -10 + i * 14)], 3, PAL["gray"])
    else:
        rrect(cv, -40, -55, 40, 55, 8, col, 6)
        rrect(cv, -40, -55, -26, 55, 6, darken(col, 0.25), 5)
        rrect(cv, -14, -34, 28, -10, 5, lighten(col, 0.5), 4)


@_prop
def prop_bulb(cv, on=1.0, t=0.0):
    if on > 0.05:
        for i in range(10):
            a = math.radians(i * 36 + 18)
            line(cv, [(math.cos(a) * 62, -18 + math.sin(a) * 62), (math.cos(a) * (76 + 5 * math.sin(t * 6 + i)), -18 + math.sin(a) * (76 + 5 * math.sin(t * 6 + i)))], 5, mix(cv.bg, PAL["yellow"], on))
    ell(cv, 0, -18, 40, fill=mix(PAL["gray"], PAL["lemon"], on), w=6)
    poly(cv, [(-16, 14), (16, 14), (14, 34), (-14, 34)], mix(PAL["gray"], PAL["lemon"], on), 6)
    rrect(cv, -16, 34, 16, 52, 6, PAL["gray"], 5)
    line(cv, [(-9, -4), (-4, -22), (0, -4), (4, -22), (9, -4)], 3.5, mix(PAL["gray"], PAL["orange"], on))


@_prop
def prop_phone(cv, screen=PAL["sky"], glow=0.0):
    rrect(cv, -34, -62, 34, 62, 14, PAL["dark"], 6)
    rrect(cv, -27, -50, 27, 46, 6, mix(screen, WHITE, glow * 0.6), 4)
    ell(cv, 0, 54, 4, fill=PAL["gray"], w=0)


@_prop
def prop_laptop(cv, screen=PAL["mint"]):
    rrect(cv, -56, -52, 56, 18, 8, PAL["gray"], 6)
    rrect(cv, -48, -44, 48, 10, 4, screen, 4)
    poly(cv, [(-70, 18), (70, 18), (62, 36), (-62, 36)], PAL["gray"], 6)


@_prop
def prop_cup(cv, t=None, col=PAL["red"]):
    rrect(cv, -34, -30, 34, 40, 12, col, 6)
    ell(cv, 40, 6, 18, 16, fill=None, w=7, col=INK)
    if t is not None:
        for i in range(3):
            f = (t * 0.6 + i / 3) % 1
            curve(cv, [(-14 + i * 14, -40 - f * 10), (-8 + i * 14, -52 - f * 14), (-14 + i * 14, -64 - f * 18)], 4, mix(cv.bg, PAL["gray"], 1 - f), smooth=True)


@_prop
def prop_pill(cv, a=PAL["red"], b=WHITE):
    capsule(cv, (-30, 0), (30, 0), 22, b, 6)
    poly(cv, [(0, -22), (30, -22), (52, 0), (30, 22), (0, 22)] if False else [(0, -22), (28, -21), (45, -10), (45, 10), (28, 21), (0, 22)], a, 0)
    capsule(cv, (-30, 0), (30, 0), 22, None, 6)
    line(cv, [(0, -22), (0, 22)], 5)


@_prop
def prop_bottle(cv, label=PAL["mint"], liquid=PAL["orange"], cross=True):
    rrect(cv, -14, -66, 14, -46, 4, PAL["red"], 5)
    rrect(cv, -34, -46, 34, 64, 14, PAL["sand"] if False else (240, 230, 200), 6)
    rrect(cv, -28, 0, 28, 58, 10, liquid, 0)
    rrect(cv, -26, -26, 26, 30, 6, label, 4)
    if cross:
        line(cv, [(0, -14), (0, 18)], 7, PAL["red"])
        line(cv, [(-16, 2), (16, 2)], 7, PAL["red"])


@_prop
def prop_flask(cv, liquid=PAL["green"], t=None):
    poly(cv, [(-14, -64), (14, -64), (14, -24), (50, 48), (40, 62), (-40, 62), (-50, 48), (-14, -24)], (235, 245, 250), 6)
    poly(cv, [(-34, 24), (34, 24), (50, 48), (40, 62), (-40, 62), (-50, 48)], liquid, 5)
    rrect(cv, -18, -70, 18, -60, 4, PAL["gray"], 5)
    if t is not None:
        for i in range(3):
            f = (t * 0.7 + i / 3) % 1
            ell(cv, -14 + i * 14 + 5 * math.sin(t * 3 + i), 20 - f * 70, 5 + i, fill=None, w=3, col=INK)


@_prop
def prop_magnifier(cv, glass=(220, 240, 255)):
    line(cv, [(26, 26), (62, 62)], 16, PAL["wood"])
    ell(cv, -8, -8, 44, fill=glass, w=8)
    ell(cv, -22, -22, 10, 6, fill=WHITE, w=0)


@_prop
def prop_trophy(cv):
    poly(cv, [(-34, -50), (34, -50), (28, -2), (10, 14), (-10, 14), (-28, -2)], PAL["yellow"], 6)
    for sg in (-1, 1):
        ell(cv, sg * 40, -30, 16, 18, fill=None, w=6, col=INK)
    rect_c(cv, 0, 24, 14, 20, fill=PAL["yellow"], lw=5)
    rrect(cv, -30, 34, 30, 54, 6, PAL["wood"], 6)
    star_poly(cv, 0, -26, 14, fill=WHITE, w=3.5)


@_prop
def prop_coin(cv, sym="$"):
    ell(cv, 0, 0, 42, fill=PAL["yellow"], w=6)
    ell(cv, 0, 0, 32, fill=None, w=3.5, col=darken(PAL["yellow"], 0.35))
    text(cv, 0, 2, sym, 44, darken(PAL["yellow"], 0.5))


@_prop
def prop_bed(cv, blanket=PAL["blue"], sleeping=False):
    rrect(cv, -78, -40, -66, 56, 5, PAL["wood"], 5)
    rrect(cv, 66, -4, 78, 56, 5, PAL["wood"], 5)
    rrect(cv, -70, 8, 70, 40, 8, WHITE, 6)
    rrect(cv, -64, -2, -22, 20, 10, PAL["lemon"], 5)
    rrect(cv, -14, -2, 70, 40, 10, blanket, 6)
    if sleeping:
        for i, (dx, dy) in enumerate(((-40, -30), (-22, -52), (-2, -70))):
            text(cv, dx, dy, "Z", 24 + i * 8, INK)


@_prop
def prop_calendar(cv, day="19", head=PAL["red"]):
    rrect(cv, -50, -56, 50, 56, 10, WHITE, 6)
    rrect(cv, -50, -56, 50, -24, 10, head, 6)
    for sx in (-26, 26):
        line(cv, [(sx, -68), (sx, -46)], 8, INK)
    text(cv, 0, 14, day, 54)


@_prop
def prop_lock(cv, opened=0.0, col=PAL["yellow"]):
    lift = opened * 22
    pts = [(-22, -10 - lift), (-22, -36 - lift)] + [(22 * math.cos(math.radians(a)) * -1, -36 - lift - 22 * math.sin(math.radians(a))) for a in range(0, 181, 20)] + [(22, -36 - lift), (22, -10 - lift if opened < 0.5 else -26)]
    line(cv, [(-22, -10), (-22, -36), (-14, -56), (0, -62), (14, -56), (22, -36), (22, -10)] if opened < 0.05 else
         [(-22, -10 - lift), (-22, -36 - lift), (-14, -56 - lift), (0, -62 - lift), (14, -56 - lift), (22, -36 - lift), (22, -26)], 9, PAL["gray"])
    rrect(cv, -38, -12, 38, 50, 10, col, 6)
    ell(cv, 0, 16, 7, fill=INK, w=0)
    line(cv, [(0, 18), (0, 34)], 5)


@_prop
def prop_rocket(cv, t=0.0, flame=True):
    if flame:
        f = 1 + 0.25 * math.sin(t * 30)
        poly(cv, [(-14, 56), (0, 56 + 50 * f), (14, 56)], PAL["orange"], 4)
        poly(cv, [(-7, 56), (0, 56 + 28 * f), (7, 56)], PAL["yellow"], 0)
    for sg in (-1, 1):
        poly(cv, [(sg * 22, 18), (sg * 50, 62), (sg * 22, 52)], PAL["red"], 6)
    poly(cv, [(0, -72), (28, -30), (28, 56), (-28, 56), (-28, -30)], WHITE, 6)
    poly(cv, [(0, -72), (28, -30), (-28, -30)], PAL["red"], 6)
    ell(cv, 0, 0, 14, fill=PAL["sky"], w=5)
