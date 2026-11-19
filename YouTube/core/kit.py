"""
uTeam-Studio
core/kit.py — конструктор: формы, кривые/пути (в т.ч. SVG), трубки и IK-конечности,
фоны-паттерны, графики. Из этих «кирпичиков» собирается всё, чего нет в primitives.
Всё рисуется карандашным стилем (толстый контур + wobble) и учитывает камеру/группы.
"""

import math
import re
from typing import List, Tuple, Optional, Sequence

from .config import INK, WHITE, ACCENT_RED, ACCENT_BLUE, ACCENT_YELLOW, ACCENT_GREEN
from .primitives import (Canvas, line, poly, ell, rrect, text, twidth, fit, mix, seg, E, back,
                         pop, fa, ph)
from .stage import group, clip
from .anim import rnd, lerp, EASES

Pt = Tuple[float, float]

# ============================================================
# Палитра (пастель + контур)
# ============================================================

PAL = dict(
    red=(235, 90, 80), orange=(250, 150, 60), yellow=(250, 205, 50), green=(110, 200, 110),
    teal=(80, 200, 190), blue=(90, 150, 240), purple=(165, 125, 225), pink=(248, 160, 190),
    skin=(255, 224, 196), white=(255, 255, 255), cream=(255, 248, 225), gray=(190, 190, 198),
    dark=(60, 60, 72), brown=(150, 100, 65), sky=(180, 225, 255), mint=(190, 240, 215),
    sand=(240, 215, 160), night=(30, 34, 70), lemon=(255, 240, 150), wood=(190, 140, 90),
)


def lighten(col, k=0.3):
    return mix(col, (255, 255, 255), k)


def darken(col, k=0.25):
    return mix(col, (20, 20, 30), k)


# ============================================================
# Простые формы
# ============================================================

def rectangle(cv, x0, y0, x1, y1, fill=None, w=6, col=INK):
    """Прямоугольник с острыми углами (rrect — со скруглением)."""
    poly(cv, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], fill, w, col)


def rect_c(cv, cx, cy, w, h, r=0, fill=None, lw=6, col=INK):
    """Прямоугольник по центру; r — скругление."""
    if r > 0:
        rrect(cv, cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, r, fill, lw, col)
    else:
        rectangle(cv, cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, fill, lw, col)


def regpoly(cv, cx, cy, r, n=5, rot=-90, fill=None, w=6, col=INK):
    pts = [(cx + r * math.cos(math.radians(rot + 360 * i / n)),
            cy + r * math.sin(math.radians(rot + 360 * i / n))) for i in range(n)]
    poly(cv, pts, fill, w, col)


def star_poly(cv, cx, cy, r_out, r_in=None, n=5, rot=-90, fill=None, w=5, col=INK):
    r_in = r_out * 0.45 if r_in is None else r_in
    pts = []
    for i in range(n * 2):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(rot + 180 * i / n)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    poly(cv, pts, fill, w, col)


def heart_shape(cv, cx, cy, r, fill=PAL["red"], w=5, col=INK):
    pts = []
    for i in range(48):
        a = 2 * math.pi * i / 48
        x = 16 * math.sin(a) ** 3
        y = 13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a)
        pts.append((cx + x * r / 17, cy - y * r / 17 - r * 0.05))
    poly(cv, pts, fill, w, col)


def gear_shape(cv, cx, cy, r, teeth=8, rot=0, fill=PAL["gray"], w=5, col=INK, hole=0.28):
    pts = []
    for i in range(teeth):
        base = 360 * i / teeth + rot
        for da, rr in ((-0.20, 0.80), (-0.12, 1.0), (0.12, 1.0), (0.20, 0.80)):
            a = math.radians(base + da * 360 / teeth)
            pts.append((cx + r * rr * math.cos(a), cy + r * rr * math.sin(a)))
    poly(cv, pts, fill, w, col)
    if hole > 0:
        ell(cv, cx, cy, r * hole, fill=INK if fill is None else cv.bg, w=w * 0.8, col=col)


def cloud_shape(cv, cx, cy, w=220, fill=WHITE, lw=5, col=INK):
    r = w / 6.0
    parts = [(-2.0 * r, 0.35 * r, 0.9 * r), (-0.9 * r, -0.35 * r, 1.25 * r),
             (0.7 * r, -0.2 * r, 1.4 * r), (2.0 * r, 0.35 * r, 0.95 * r), (0.0, 0.5 * r, 1.0 * r)]
    for dx, dy, rr in parts:
        ell(cv, cx + dx, cy + dy, rr + lw * 0.6, fill=col, w=0)
    for dx, dy, rr in parts:
        ell(cv, cx + dx, cy + dy, rr - lw * 0.4, fill=fill, w=0)


def blob_pts(cx, cy, r, seed=0, irr=0.18, n=9, rot=0, ry=None) -> List[Pt]:
    ry = r if ry is None else ry
    base = []
    for i in range(n):
        a = math.radians(rot + 360 * i / n)
        k = 1 + irr * (rnd(seed * 31 + i) * 2 - 1)
        base.append((cx + r * k * math.cos(a), cy + ry * k * math.sin(a)))
    return catmull(base, closed=True)


def blob_shape(cv, cx, cy, r, seed=0, irr=0.18, n=9, rot=0, ry=None, fill=None, w=6, col=INK):
    poly(cv, blob_pts(cx, cy, r, seed, irr, n, rot, ry)[:-1], fill, w, col)


def capsule(cv, p0: Pt, p1: Pt, r, fill=None, w=5, col=INK):
    """Стадион (толстая линия с круглыми концами) — для частей тела, труб, таблеток."""
    ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
    pts = []
    for i in range(13):
        a = ang - math.pi / 2 + math.pi * i / 12
        pts.append((p1[0] + r * math.cos(a), p1[1] + r * math.sin(a)))
    for i in range(13):
        a = ang + math.pi / 2 + math.pi * i / 12
        pts.append((p0[0] + r * math.cos(a), p0[1] + r * math.sin(a)))
    poly(cv, pts, fill, w, col)


def checkmark(cv, cx, cy, s=40, col=PAL["green"], w=12, k=1.0):
    pts = [(cx - s * 0.6, cy), (cx - s * 0.15, cy + s * 0.5), (cx + s * 0.7, cy - s * 0.5)]
    curve(cv, pts, w, col, k=k, smooth=False)


def crossmark(cv, cx, cy, s=40, col=PAL["red"], w=12, k=1.0):
    h = s * 0.55
    curve(cv, [(cx - h, cy - h), (cx + h, cy + h)], w, col, k=min(1, k * 2), smooth=False)
    if k > 0.5:
        curve(cv, [(cx + h, cy - h), (cx - h, cy + h)], w, col, k=min(1, (k - 0.5) * 2), smooth=False)


def spiral(cv, cx, cy, r, turns=3, k=1.0, w=6, col=INK):
    n = 90
    pts = [(cx + r * (i / n) * math.cos(turns * 2 * math.pi * i / n),
            cy + r * (i / n) * math.sin(turns * 2 * math.pi * i / n)) for i in range(n + 1)]
    curve(cv, pts, w, col, k=k, smooth=False)


def wavy_line(cv, x0, y0, x1, y1, amp=8, waves=6, w=5, col=INK, k=1.0, phase=0.0):
    n = 60
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy) or 1
    nx, ny = -dy / L, dx / L
    pts = []
    for i in range(n + 1):
        u = i / n
        o = amp * math.sin(2 * math.pi * (waves * u + phase))
        pts.append((x0 + dx * u + nx * o, y0 + dy * u + ny * o))
    curve(cv, pts, w, col, k=k, smooth=False)


# ============================================================
# Кривые и пути
# ============================================================

def catmull(pts: Sequence[Pt], closed=False, n=10) -> List[Pt]:
    """Гладкий сплайн Catmull-Rom через заданные точки."""
    P = list(pts)
    if len(P) < 3:
        return P
    if closed:
        P = [P[-1]] + P + [P[0], P[1]]
    else:
        P = [P[0]] + P + [P[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for j in range(n):
            u = j / n
            u2, u3 = u * u, u * u * u
            out.append(tuple(
                0.5 * ((2 * p1[c]) + (-p0[c] + p2[c]) * u +
                       (2 * p0[c] - 5 * p1[c] + 4 * p2[c] - p3[c]) * u2 +
                       (-p0[c] + 3 * p1[c] - 3 * p2[c] + p3[c]) * u3) for c in (0, 1)))
    out.append(P[-2])
    return out


def trim(pts: Sequence[Pt], k: float) -> List[Pt]:
    """Начало ломаной длиной k (0..1) от полной длины — основа анимации «рисуется на глазах»."""
    if k >= 0.999:
        return list(pts)
    if k <= 0 or len(pts) < 2:
        return []
    L = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:])]
    goal = sum(L) * k
    out = [pts[0]]
    run = 0.0
    for (a, b), l in zip(zip(pts, pts[1:]), L):
        if run + l >= goal:
            u = (goal - run) / l if l else 0
            out.append((a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u))
            return out
        run += l
        out.append(b)
    return out


def curve(cv: Canvas, pts: Sequence[Pt], w=6, col=INK, k=1.0, smooth=True, closed=False):
    """Линия по точкам. smooth — сплайн; k — прогресс «дорисовки» 0..1."""
    P = catmull(pts, closed) if smooth else list(pts)
    P = trim(P, k)
    if len(P) >= 2:
        line(cv, P, w, col)


def curve_fill(cv: Canvas, pts: Sequence[Pt], fill=None, w=6, col=INK):
    """Закрытая гладкая фигура через точки."""
    P = catmull(pts, closed=True)
    poly(cv, P[:-1], fill, w, col)


_TOK = re.compile(r"[MmLlHhVvCcSsQqTtZz]|[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?")


def parse_path(d: str, steps: int = 14) -> List[Tuple[List[Pt], bool]]:
    """SVG path (M L H V C S Q T Z, абсолютные и относительные) -> [(точки, замкнут)]."""
    toks = _TOK.findall(d)
    i = 0
    subs, cur, closed = [], [], False
    x = y = sx = sy = 0.0
    cmd = None
    lastc = None  # последняя контрольная точка (для S/T)

    def num():
        nonlocal i
        v = float(toks[i]); i += 1
        return v

    def flush():
        nonlocal cur, closed
        if len(cur) >= 2:
            subs.append((cur, closed))
        cur, closed = [], False

    while i < len(toks):
        if re.match(r"[A-Za-z]", toks[i]):
            cmd = toks[i]; i += 1
            if cmd in "Zz":
                closed = True
                x, y = sx, sy
                flush()
                continue
        rel = cmd.islower()
        c = cmd.upper()
        if c == "M":
            nx, ny = num(), num()
            if rel: nx, ny = x + nx, y + ny
            flush()
            x, y, sx, sy = nx, ny, nx, ny
            cur = [(x, y)]
            cmd = "l" if rel else "L"
            lastc = None
        elif c == "L":
            nx, ny = num(), num()
            if rel: nx, ny = x + nx, y + ny
            cur.append((nx, ny)); x, y = nx, ny; lastc = None
        elif c == "H":
            nx = num(); nx = x + nx if rel else nx
            cur.append((nx, y)); x = nx; lastc = None
        elif c == "V":
            ny = num(); ny = y + ny if rel else ny
            cur.append((x, ny)); y = ny; lastc = None
        elif c in "CS":
            if c == "C":
                x1, y1 = num(), num()
                if rel: x1, y1 = x + x1, y + y1
            else:
                x1, y1 = (2 * x - lastc[0], 2 * y - lastc[1]) if lastc else (x, y)
            x2, y2, nx, ny = num(), num(), num(), num()
            if rel: x2, y2, nx, ny = x + x2, y + y2, x + nx, y + ny
            for j in range(1, steps + 1):
                u = j / steps; v = 1 - u
                cur.append((v**3 * x + 3 * v * v * u * x1 + 3 * v * u * u * x2 + u**3 * nx,
                            v**3 * y + 3 * v * v * u * y1 + 3 * v * u * u * y2 + u**3 * ny))
            lastc = (x2, y2); x, y = nx, ny
        elif c in "QT":
            if c == "Q":
                x1, y1 = num(), num()
                if rel: x1, y1 = x + x1, y + y1
            else:
                x1, y1 = (2 * x - lastc[0], 2 * y - lastc[1]) if lastc else (x, y)
            nx, ny = num(), num()
            if rel: nx, ny = x + nx, y + ny
            for j in range(1, steps + 1):
                u = j / steps; v = 1 - u
                cur.append((v * v * x + 2 * v * u * x1 + u * u * nx, v * v * y + 2 * v * u * y1 + u * u * ny))
            lastc = (x1, y1); x, y = nx, ny
        else:
            raise ValueError(f"svgpath: команда {cmd!r} не поддерживается (A — дуги — замените на C)")
    flush()
    return subs


def svgpath(cv: Canvas, d: str, x=0, y=0, sc=1.0, rot=0, fill=None, w=6, col=INK, k=1.0,
            flip=False, center: Pt = (0, 0)):
    """
    Нарисовать SVG-путь (атрибут d) в точке (x, y). center — какая точка пути станет (x, y).
    k — «дорисовка» 0..1 (контур рисуется на глазах, заливка появляется в конце).
    Толщина w не зависит от sc. Можно брать пути из любых иконок/логотипов.
    """
    subs = parse_path(d)
    total = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for pts, _ in subs for a, b in zip(pts, pts[1:])) or 1
    done = 0.0
    with group(cv, x, y, rot=rot, sc=sc, flip=flip):
        for pts, closed in subs:
            pts = [(px - center[0], py - center[1]) for px, py in pts]
            L = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:]))
            kk = (k * total - done) / L if L else 1
            done += L
            if kk <= 0:
                continue
            kk = min(1.0, kk)
            if closed and kk >= 0.999:
                poly(cv, pts[:-1] if pts[0] == pts[-1] else pts, fill, w / sc, col)
            else:
                P = trim(pts + ([pts[0]] if closed else []), kk)
                if len(P) >= 2:
                    line(cv, P, w / sc, col)


# ============================================================
# Трубки и IK
# ============================================================

def tube(cv: Canvas, pts: Sequence[Pt], w=14, fill=PAL["skin"], outline=INK, ow=4, smooth=True):
    """Толстая линия с контуром (рука, нога, труба, провод, хвост)."""
    P = catmull(pts) if smooth and len(pts) > 2 else list(pts)
    line(cv, P, w + 2 * ow, outline)
    line(cv, P, w, fill)


def ik2(p0: Pt, target: Pt, l1: float, l2: float, bend: int = 1):
    """Двухзвенная IK: возвращает (сустав, конец). bend=±1 — в какую сторону согнут сустав."""
    dx, dy = target[0] - p0[0], target[1] - p0[1]
    dist = math.hypot(dx, dy) or 1e-6
    dd = min(max(dist, abs(l1 - l2) + 1e-3), l1 + l2 - 1e-3)
    a = (l1 * l1 - l2 * l2 + dd * dd) / (2 * dd)
    h = math.sqrt(max(l1 * l1 - a * a, 0))
    ux, uy = dx / dist, dy / dist
    mx, my = p0[0] + ux * a, p0[1] + uy * a
    joint = (mx - uy * h * bend, my + ux * h * bend)
    end = (p0[0] + ux * dd, p0[1] + uy * dd)
    return joint, end


def limb(cv: Canvas, p0: Pt, target: Pt, l1: float, l2: float, bend: int = 1, w=12,
         fill=PAL["skin"], outline=INK, ow=4, hand_r: float = 0):
    """Рука/нога из двух звеньев, тянущаяся к точке target. Возвращает конечную точку."""
    joint, end = ik2(p0, target, l1, l2, bend)
    tube(cv, [p0, joint, end], w, fill, outline, ow, smooth=False)
    if hand_r > 0:
        ell(cv, end[0], end[1], hand_r, fill=fill, w=ow)
    return end


# ============================================================
# Фоны-паттерны (анимированные)
# ============================================================

def bg_dots(cv: Canvas, t: float, spacing=64, r=6, col=(255, 255, 255), speed=(14, 10), alpha=0.5):
    """Горошек, плавно уезжающий. Рисуется в экранных координатах (до камеры или в hud)."""
    cfg = cv.cfg
    c = mix(cv.bg, col, alpha)
    ox, oy = (t * speed[0]) % spacing, (t * speed[1]) % spacing
    nx, ny = int(cfg.width / spacing) + 3, int(cfg.height / spacing) + 3
    for j in range(-1, ny):
        for i in range(-1, nx):
            x = i * spacing + ox + (spacing / 2 if j % 2 else 0)
            y = j * spacing + oy
            px, py = cv.pt(x, y)
            rr = r * cv.sc
            cv.d.ellipse([px - rr, py - rr, px + rr, py + rr], fill=c)


def bg_grid(cv: Canvas, t: float, spacing=80, w=2, col=(255, 255, 255), speed=(0, 20), alpha=0.5):
    cfg = cv.cfg
    c = mix(cv.bg, col, alpha)
    ox, oy = (t * speed[0]) % spacing, (t * speed[1]) % spacing
    for i in range(-1, int(cfg.width / spacing) + 2):
        a, b = cv.pt(i * spacing + ox, 0), cv.pt(i * spacing + ox, cfg.height)
        cv.d.line([a, b], fill=c, width=max(1, int(w * cv.sc)))
    for j in range(-1, int(cfg.height / spacing) + 2):
        a, b = cv.pt(0, j * spacing + oy), cv.pt(cfg.width, j * spacing + oy)
        cv.d.line([a, b], fill=c, width=max(1, int(w * cv.sc)))


def bg_stripes(cv: Canvas, t: float, width=70, col=(255, 255, 255), speed=30, alpha=0.35, angle=-30):
    cfg = cv.cfg
    c = mix(cv.bg, col, alpha)
    diag = math.hypot(cfg.width, cfg.height)
    ca, sa = math.cos(math.radians(angle)), math.sin(math.radians(angle))
    n = int(diag / width) + 2
    off = (t * speed) % (2 * width)
    cx, cy = cfg.width / 2, cfg.height / 2
    for i in range(-n, n):
        s0 = i * 2 * width + off
        quad = []
        for u, v in ((s0, -diag), (s0 + width, -diag), (s0 + width, diag), (s0, diag)):
            quad.append(cv.pt(cx + u * ca - v * sa, cy + u * sa + v * ca))
        cv.d.polygon(quad, fill=c)


def bg_rays(cv: Canvas, t: float, cx=None, cy=None, n=16, col=(255, 255, 255), alpha=0.35, speed=8):
    """Вращающиеся лучи-«sunburst» (ретро-плакат, акцент на объекте)."""
    cfg = cv.cfg
    cx = cfg.center_x if cx is None else cx
    cy = cfg.height / 2 if cy is None else cy
    c = mix(cv.bg, col, alpha)
    R = math.hypot(cfg.width, cfg.height)
    for i in range(n):
        a0 = math.radians(360 * i / n + t * speed)
        a1 = math.radians(360 * i / n + 180 / n + t * speed)
        tri = [cv.pt(cx, cy), cv.pt(cx + R * math.cos(a0), cy + R * math.sin(a0)),
               cv.pt(cx + R * math.cos(a1), cy + R * math.sin(a1))]
        cv.d.polygon(tri, fill=c)


def bg_gradient(cv: Canvas, top, bottom, bands: int = 160):
    """Вертикальный градиент на весь холст (вызывать первым, до камеры/слоёв). Быстрый: рисуется полосами."""
    W, H = cv.im.size
    for i in range(bands):
        y0, y1 = int(H * i / bands), int(H * (i + 1) / bands) + 1
        cv.d.rectangle([0, y0, W, y1], fill=mix(top, bottom, i / (bands - 1)))


def ground(cv: Canvas, y, col=PAL["green"], h=400, w=6, bumps=0, x0=-200, x1=None):
    """Земля/пол с контуром; bumps — холмистость."""
    x1 = cv.cfg.width + 200 if x1 is None else x1
    pts = [(x0, y)]
    n = 24
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / n
        pts.append((x, y - bumps * math.sin(i * 0.9)))
    pts += [(x1, y + h), (x0, y + h)]
    poly(cv, pts, col, w)


# ============================================================
# Графики (анимированные)
# ============================================================

def bars(cv: Canvas, t: float, a: float, x: float, y: float, w: float, h: float,
         values: Sequence[float], labels: Sequence[str] = None, colors=None, vmax: float = None,
         gap: float = 0.28, d: float = 0.7, stag: float = 0.12, label_size: float = 24,
         value_fmt: str = "{:g}", kind: str = "out", show_values=True):
    """Столбчатая диаграмма. (x, y) — левый НИЖНИЙ угол оси, w×h — размер области. Столбцы растут по очереди."""
    n = len(values)
    vmax = vmax or max(values)
    slot = w / n
    bw = slot * (1 - gap)
    colors = colors or [PAL["blue"], PAL["orange"], PAL["green"], PAL["pink"], PAL["purple"], PAL["yellow"]]
    line(cv, [(x - 8, y), (x + w + 8, y)], 5)
    for i, v in enumerate(values):
        k = EASES[kind](max(0.0, min(1.0, (t - a - i * stag) / d)))
        hh = h * (v / vmax) * k
        bx = x + slot * i + (slot - bw) / 2
        if hh > 2:
            rrect(cv, bx, y - hh, bx + bw, y, min(10, bw / 3), colors[i % len(colors)], 5)
            if show_values and k > 0.6:
                text(cv, bx + bw / 2, y - hh - label_size * 0.8, value_fmt.format(v), label_size,
                     alpha=(k - 0.6) / 0.4)
        if labels:
            text(cv, bx + bw / 2, y + label_size * 0.95, labels[i], fit(labels[i], label_size, slot * 0.95),
                 alpha=min(1.0, (t - a) / 0.3))


def line_chart(cv: Canvas, t: float, a: float, x: float, y: float, w: float, h: float,
               values: Sequence[float], col=PAL["red"], d: float = 1.4, vmin: float = None,
               vmax: float = None, dots: bool = True, lw: float = 7, axes: bool = True, kind="inout"):
    """Линейный график, рисуется слева направо. (x, y) — левый НИЖНИЙ угол."""
    n = len(values)
    vmin = min(values) if vmin is None else vmin
    vmax = max(values) if vmax is None else vmax
    span = (vmax - vmin) or 1
    pts = [(x + w * i / (n - 1), y - h * (v - vmin) / span) for i, v in enumerate(values)]
    if axes:
        line(cv, [(x, y - h - 10), (x, y), (x + w + 10, y)], 5)
    k = EASES[kind](max(0.0, min(1.0, (t - a) / d)))
    curve(cv, pts, lw, col, k=k)
    if dots:
        for i, p in enumerate(pts):
            if i / (n - 1) <= k + 1e-6:
                ell(cv, p[0], p[1], 9, fill=WHITE, w=4, col=col)


def donut(cv: Canvas, t: float, a: float, cx: float, cy: float, r: float,
          parts: Sequence[Tuple[float, Tuple[int, int, int]]], d: float = 1.0, thickness: float = 0.38,
          start: float = -90, kind="inout"):
    """Кольцевая диаграмма: parts = [(значение, цвет), ...]. Заполняется по кругу."""
    total = sum(v for v, _ in parts) or 1
    k = EASES[kind](max(0.0, min(1.0, (t - a) / d)))
    limit = 360 * k
    ang = 0.0
    ri = r * (1 - thickness)
    for v, c in parts:
        sweep = 360 * v / total
        s = min(sweep, max(0.0, limit - ang))
        if s > 0.5:
            steps = max(3, int(s / 6))
            outer = [(cx + r * math.cos(math.radians(start + ang + s * i / steps)),
                      cy + r * math.sin(math.radians(start + ang + s * i / steps))) for i in range(steps + 1)]
            inner = [(cx + ri * math.cos(math.radians(start + ang + s * i / steps)),
                      cy + ri * math.sin(math.radians(start + ang + s * i / steps))) for i in range(steps, -1, -1)]
            poly(cv, outer + inner, c, 5)
        ang += sweep


def progress_ring(cv: Canvas, cx, cy, r, k, col=PAL["green"], w=18, track=(225, 225, 230)):
    ell(cv, cx, cy, r, w=w, col=track)
    if k > 0.01:
        ell(cv, cx, cy, r, w=w, col=col, a0=-90, a1=-90 + 359 * min(1.0, k))
