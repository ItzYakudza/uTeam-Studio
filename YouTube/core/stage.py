"""
uTeam-Studio
core/stage.py — камера, группы (трансформации), параллакс-слои, HUD, клиппинг.

Типичное использование в сцене:

    def s03(cv, t, T):
        cam(cv, zoom=tween(t, T[1], 0.8, 1.0, 1.5), at=(360, 500), t=t)
        with layer(cv, 0.3):            # дальний фон — движется меньше камеры
            ... облака, горы ...
        ...персонажи и объекты (в мире)...
        with hud(cv):                   # то, что не зависит от камеры
            cap(cv, t, T[1], T[2], "BIG TEXT")
"""

import math
from contextlib import contextmanager
from typing import Optional, Tuple, Sequence

from PIL import Image, ImageDraw

from .anim import wiggle, keyframes, EASES, lerp
from .primitives import Canvas


# ============================================================
# Матрицы
# ============================================================

def m_translate(x, y):
    return (1.0, 0.0, 0.0, 1.0, x, y)


def m_rotate(deg):
    r = math.radians(deg)
    c, s = math.cos(r), math.sin(r)
    return (c, s, -s, c, 0.0, 0.0)


def m_scale(sx, sy=None):
    sy = sx if sy is None else sy
    return (sx, 0.0, 0.0, sy, 0.0, 0.0)


def m_mul(m1, m2):
    a1, b1, c1, d1, e1, f1 = m1
    a2, b2, c2, d2, e2, f2 = m2
    return (a1 * a2 + c1 * b2, b1 * a2 + d1 * b2,
            a1 * c2 + c1 * d2, b1 * c2 + d1 * d2,
            a1 * e2 + c1 * f2 + e1, b1 * e2 + d1 * f2 + f1)


# ============================================================
# Группы: локальная система координат
# ============================================================

@contextmanager
def group(cv: Canvas, x: float = 0, y: float = 0, rot: float = 0, sc: float = 1.0,
          sx: float = None, sy: float = None, flip: bool = False,
          alpha: float = 1.0, box: Optional[Tuple[float, float, float, float]] = None):
    """
    Локальная система координат: точка (0,0) внутри блока = (x, y) на сцене.
      rot   — поворот в градусах (по часовой)
      sc    — равномерный масштаб; sx/sy — отдельные масштабы (сквош и стретч!)
      flip  — зеркало по горизонтали
      alpha — прозрачность всей группы целиком (0..1); box — область слоя (ускоряет)
    Внутри блока рисуй любыми примитивами в локальных координатах вокруг (0,0).
    """
    kx = (sc if sx is None else sx) * (-1 if flip else 1)
    ky = sc if sy is None else sy
    cv.push(m_mul(m_translate(x, y), m_mul(m_rotate(rot), m_scale(kx, ky))))
    layered = alpha < 0.999
    hidden = alpha <= 0.01
    if hidden:
        cv.muted += 1
    elif layered:
        cv.begin_layer(box)
    try:
        yield
    finally:
        if hidden:
            cv.muted -= 1
        elif layered:
            cv.end_layer(alpha)
        cv.pop()


@contextmanager
def fade(cv: Canvas, alpha: float, box=None):
    """Прозрачность группы без смены системы координат."""
    with group(cv, alpha=alpha, box=box):
        yield


# ============================================================
# Камера
# ============================================================

def _cam_M(cv: Canvas, zoom, at, anchor, rot, dx, dy):
    cfg = cv.cfg
    cs = (cfg.center_x, cfg.height / 2)
    fx, fy = at if at is not None else cs
    ax, ay = anchor if anchor is not None else cs
    r = math.radians(rot)
    c, s = math.cos(r) * zoom, math.sin(r) * zoom
    a, b, cc, d = c, s, -s, c
    e = ax + dx - (a * fx + cc * fy)
    f = ay + dy - (b * fx + d * fy)
    S = cv.S
    return (S * a, S * b, S * cc, S * d, S * e, S * f)


def cam(cv: Canvas, zoom: float = 1.0, at: Tuple[float, float] = None,
        anchor: Tuple[float, float] = None, rot: float = 0.0,
        shake: float = 0.0, t: float = 0.0, shake_freq: float = 22.0, seed: int = 0):
    """
    Включить камеру для всего, что рисуется ДАЛЬШЕ (вызывай в начале сцены).
      zoom   — 1.0 = как есть, 1.5 = приближение в 1.5 раза
      at     — точка мира, на которую смотрит камера (по умолчанию cfg.center_x, центр композиции)
      anchor — куда на экране ставится точка `at` (по умолчанию cfg.center_x).
               zoom «на месте»: at=P, anchor=P
      rot    — крен камеры, градусы
      shake  — амплитуда тряски в логических пикселях (нужен t)
    """
    dx = dy = 0.0
    if shake:
        dx = wiggle(t, shake, shake_freq, seed)
        dy = wiggle(t, shake, shake_freq, seed + 1)
        rot = rot + wiggle(t, shake * 0.06, shake_freq, seed + 2)
    cv.camera = dict(zoom=zoom, at=at, anchor=anchor, rot=rot, dx=dx, dy=dy)
    cv.set_world(_cam_M(cv, zoom, at, anchor, rot, dx, dy))


def cam_keys(cv: Canvas, t: float, keys: Sequence[Tuple[float, dict]],
             kind: str = "inout", shake: float = 0.0, **extra):
    """
    Камера по кейфреймам: keys = [(время, dict(zoom=.., at=(x,y), anchor=(x,y), rot=..)), ...].
    Зум интерполируется геометрически (ощущается равномерным), точки — линейно.
    Пример:
        cam_keys(cv, t, [(T[0], dict(zoom=1)), (T[1], dict(zoom=1.6, at=(300, 420)))], t=t)
    """
    cfg = cv.cfg
    cs = (cfg.center_x, cfg.height / 2)
    ks = list(keys)
    if t <= ks[0][0]:
        p = dict(ks[0][1])
    elif t >= ks[-1][0]:
        p = dict(ks[-1][1])
    else:
        p = {}
        for (t0, p0), (t1, p1) in zip(ks, ks[1:]):
            if t0 <= t <= t1:
                k = EASES[kind]((t - t0) / (t1 - t0))
                z0, z1 = p0.get("zoom", 1.0), p1.get("zoom", 1.0)
                p["zoom"] = z0 * (z1 / z0) ** k
                for name in ("at", "anchor"):
                    a0, a1 = p0.get(name) or cs, p1.get(name) or cs
                    if p0.get(name) is None and p1.get(name) is None:
                        p[name] = None
                    else:
                        p[name] = lerp(a0, a1, k)
                p["rot"] = lerp(p0.get("rot", 0.0), p1.get("rot", 0.0), k)
                break
    cam(cv, zoom=p.get("zoom", 1.0), at=p.get("at"), anchor=p.get("anchor"),
        rot=p.get("rot", 0.0), shake=shake, t=t, **extra)


@contextmanager
def layer(cv: Canvas, depth: float = 1.0):
    """
    Параллакс-слой. depth=1 — как мир (полностью следует камере), 0 — приклеен к экрану,
    0.3 — далёкий фон (двигается/зумится слабее), 1.4 — передний план (сильнее).
    """
    c = cv.camera
    if c is None:
        yield
        return
    cfg = cv.cfg
    cs = (cfg.center_x, cfg.height / 2)
    at = c["at"] if c["at"] is not None else cs
    an = c["anchor"] if c["anchor"] is not None else cs
    k = depth
    at_k = (cs[0] + (at[0] - cs[0]) * k, cs[1] + (at[1] - cs[1]) * k)
    an_k = (cs[0] + (an[0] - cs[0]) * k, cs[1] + (an[1] - cs[1]) * k)
    cv.push_abs(_cam_M(cv, c["zoom"] ** k, at_k, an_k, c["rot"] * k, c["dx"] * k, c["dy"] * k))
    try:
        yield
    finally:
        cv.pop()


@contextmanager
def hud(cv: Canvas):
    """Экранное пространство: игнорирует камеру (субтитры, заголовки, рамки)."""
    cv.push_abs(cv.screen_M)
    try:
        yield
    finally:
        cv.pop()


def world_to_screen(cv: Canvas, x: float, y: float) -> Tuple[float, float]:
    """Где на экране (в логических координатах) окажется точка мира (x, y) при текущей камере."""
    px, py = cv.pt(x, y)
    return ((px + cv.ox) / cv.S, (py + cv.oy) / cv.S)


# ============================================================
# Клиппинг
# ============================================================

@contextmanager
def clip(cv: Canvas, shape: tuple, box=None):
    """
    Всё, что нарисовано внутри блока, видно только внутри формы:
      ("rect", x0, y0, x1, y1)  |  ("circle", cx, cy, r)  |  ("poly", [(x, y), ...])
    Координаты — в текущей системе (с учётом камеры/группы).
    """
    cv.begin_layer(box)
    layer_w, layer_h = cv.im.size
    ox, oy = cv.ox, cv.oy
    try:
        yield
    finally:
        mask = Image.new("L", (layer_w, layer_h), 0)
        md = ImageDraw.Draw(mask)
        kind = shape[0]
        if kind == "rect":
            _, x0, y0, x1, y1 = shape
            pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
            md.polygon([cv.pt(x, y) for x, y in pts], fill=255)
        elif kind == "circle":
            _, cx, cy, r = shape
            n = 72
            pts = [(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n))
                   for i in range(n)]
            md.polygon([cv.pt(x, y) for x, y in pts], fill=255)
        elif kind == "poly":
            md.polygon([cv.pt(x, y) for x, y in shape[1]], fill=255)
        cv.end_layer(1.0, mask=mask)
