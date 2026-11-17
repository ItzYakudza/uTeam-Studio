"""
uTeam-Studio
core/primitives.py — карандашный движок, персонажи, объекты.
"""

import math
from typing import List, Tuple, Optional

from PIL import Image, ImageDraw, ImageFont

from .config import FormatConfig, INK, WHITE

# ============================================================
# Easing
# ============================================================

def seg(t: float, a: float, b: float) -> float:
    return min(1.0, max(0.0, (t - a) / (b - a) if b != a else 1.0))

def E(x: float) -> float:
    return x * x * (3 - 2 * x)

def ph(p: float, a: float, b: float) -> float:
    return E(seg(p, a, b))

def back(x: float) -> float:
    x = seg(x, 0, 1)
    c = 1.70158
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2

def mix(a: Tuple[int, int, int], b: Tuple[int, int, int], k: float) -> Tuple[int, int, int]:
    k = max(0.0, min(1.0, k))
    return tuple(int(a[i] + (b[i] - a[i]) * k) for i in range(3))

def pop(t: float, a: float, d: float = 0.45) -> float:
    return back((t - a) / d) if d > 0 else 1.0

def fa(t: float, a: float, d: float = 0.4) -> float:
    return ph(t, a, a + d)

def rg(t: float, a: float, b: float) -> float:
    return ph(t, a, max(b, a + 0.3))


# ============================================================
# Canvas
# ============================================================

class Canvas:
    def __init__(self, cfg: FormatConfig, bg: Tuple[int, int, int]):
        self.cfg = cfg
        self.bg = bg
        self.S = cfg.out_width / cfg.width * cfg.supersample
        self.im = Image.new("RGB", (int(cfg.width * self.S), int(cfg.height * self.S)), bg)
        self.d = ImageDraw.Draw(self.im)

    def final_image(self) -> Image.Image:
        if self.cfg.supersample > 1:
            return self.im.reduce(self.cfg.supersample)
        return self.im


# ============================================================
# Fonts
# ============================================================

_font_cache = {}

def get_font(size: int):
    size = max(8, int(size))
    if size not in _font_cache:
        for name in ("comicbd.ttf", "comic.ttf", "segoepr.ttf", "arialbd.ttf",
                     "DejaVuSans-Bold.ttf", "Arial.ttf"):
            try:
                _font_cache[size] = ImageFont.truetype(name, size)
                break
            except Exception:
                continue
        else:
            _font_cache[size] = ImageFont.load_default()
    return _font_cache[size]


# ============================================================
# Geometry + pencil wobble
# ============================================================

def _subdivide(pts: List[Tuple[float, float]], step: float = 22) -> List[Tuple[float, float]]:
    out = [pts[0]]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        dist = math.hypot(x1 - x0, y1 - y0)
        n = max(1, int(dist // step))
        for i in range(1, n + 1):
            out.append((x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n))
    return out


def wob(pts: List[Tuple[float, float]], amp: float = 0.9) -> List[Tuple[float, float]]:
    P = _subdivide(pts)
    x0, y0 = P[0]
    return [
        (x + amp * math.sin(0.05 * (x - x0) + 0.07 * (y - y0)),
         y + amp * math.cos(0.06 * (x - x0) - 0.04 * (y - y0)))
        for x, y in P
    ]


def line(cv: Canvas, pts: List[Tuple[float, float]], w: float = 6, col=INK):
    P = [(x * cv.S, y * cv.S) for x, y in wob(pts)]
    cv.d.line(P, fill=col, width=max(1, int(w * cv.S)), joint="curve")
    r = w * cv.S / 2
    for x, y in (P[0], P[-1]):
        cv.d.ellipse([x - r, y - r, x + r, y + r], fill=col)


def poly(cv: Canvas, pts: List[Tuple[float, float]], fill=None, w: float = 6, col=INK):
    P = [(x * cv.S, y * cv.S) for x, y in wob(list(pts) + [pts[0]])]
    if fill:
        cv.d.polygon(P, fill=fill)
    if w:
        cv.d.line(P, fill=col, width=max(1, int(w * cv.S)), joint="curve")


def ell(cv: Canvas, cx: float, cy: float, rx: float, ry: float = None,
        fill=None, w: float = 6, col=INK, a0: float = 0, a1: float = 360):
    ry = rx if ry is None else ry
    n = 40
    pts = [
        (cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
         cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / n)))
        for i in range(n + 1)
    ]
    if a1 - a0 >= 360:
        poly(cv, pts[:-1], fill, w, col)
    else:
        if fill:
            poly(cv, pts, fill, 0)
        if w:
            line(cv, pts, w, col)


def rrect(cv: Canvas, x0: float, y0: float, x1: float, y1: float, r: float,
          fill=None, w: float = 6, col=INK):
    r = max(0.5, min(r, (x1 - x0) / 2, (y1 - y0) / 2))
    pts = []
    for cx, cy, a in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0),
                      (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
        for i in range(7):
            ang = math.radians(a + 90 * i / 6)
            pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    poly(cv, pts, fill, w, col)


# ============================================================
# Text
# ============================================================

def text(cv: Canvas, x: float, y: float, s: str, size: float,
         col=INK, anchor: str = "mm", stroke: float = 0,
         alpha: float = 1.0, scale: float = 1.0):
    if alpha <= 0.02 or scale <= 0.02:
        return
    font = get_font(int(size * cv.S * scale))
    fill = mix(cv.bg, col, min(1.0, alpha))
    cv.d.text(
        (x * cv.S, y * cv.S), s,
        font=font, fill=fill, anchor=anchor,
        stroke_width=int(stroke * cv.S), stroke_fill=INK
    )


def twidth(s: str, size: float) -> float:
    return get_font(int(size)).getlength(s)


def fit(s: str, size: float, maxw: float = 520) -> float:
    w = twidth(s, size)
    return size if w <= maxw else size * maxw / w


def title(cv: Canvas, t: float, s: str, size: float = 54, y: float = 70,
          col=INK, a: float = 0.1, ul=(235, 90, 70), cx: float = None):
    if cx is None:
        cx = cv.cfg.center_x
    text(cv, cx, y, s, size, col, scale=pop(t, a), stroke=(2 if col[0] > 200 else 0))
    u = ph(t, a + 0.3, a + 1.0)
    if u > 0:
        w = twidth(s, size) * 1.02
        x0 = cx - w / 2
        yy = y + size * 0.62
        xe = x0 + w * u
        line(cv, [(x0, yy), (x0 + (xe - x0) * 0.5, yy + 2), (xe, yy)], 5, ul)
        line(cv, [(xe + 4, yy - 3), (xe + 34, yy - 25)], 10, (250, 200, 40))
        poly(cv, [(xe - 2, yy + 2), (xe + 6, yy - 8), (xe + 12, yy - 2)], INK, 0)


def big(cv: Canvas, t: float, a: float, s: str, y: float, size: float = 64,
        col=INK, out: float = None, stroke: float = 0, x: float = None):
    if x is None:
        x = cv.cfg.center_x
    al = 1.0 if out is None else 1 - fa(t, out, 0.25)
    text(cv, x, y, s, fit(s, size), col, scale=pop(t, a), alpha=al, stroke=stroke)


# ============================================================
# Improved Face + Person
# ============================================================

def face(cv: Canvas, cx: float, cy: float, hr: float, s: float = 1.0, mood: str = "smile"):
    """
    Более стабильное и живое лицо.
    hr — радиус головы, s — общий scale персонажа.
    """
    # голова
    ell(cv, cx, cy, hr, hr, WHITE, max(4.5, 5.5 * s))

    # глаза
    eye_y = cy - hr * 0.12
    eye_dx = hr * 0.38
    eye_r = hr * 0.13

    if mood in ("sleep",):
        # закрытые глаза — дуги
        for sgn in (-1, 1):
            ex = cx + sgn * eye_dx
            line(cv, [
                (ex - eye_r * 1.1, eye_y),
                (ex, eye_y + eye_r * 0.6),
                (ex + eye_r * 1.1, eye_y)
            ], max(3.0, 3.8 * s))
    elif mood == "tired":
        for sgn in (-1, 1):
            ex = cx + sgn * eye_dx
            ell(cv, ex, eye_y, eye_r * 0.85, fill=INK, w=0)
            # мешки
            line(cv, [
                (ex - eye_r * 1.2, eye_y + eye_r * 1.3),
                (ex, eye_y + eye_r * 1.7),
                (ex + eye_r * 1.2, eye_y + eye_r * 1.3)
            ], max(2.5, 3.0 * s), (140, 120, 170))
    else:
        # обычные глаза (точки)
        for sgn in (-1, 1):
            ex = cx + sgn * eye_dx
            r = eye_r * (1.35 if mood == "shock" else 1.0)
            ell(cv, ex, eye_y, r, fill=INK, w=0)

    # брови / выражение
    brow_y = eye_y - hr * 0.28
    if mood == "angry":
        for sgn in (-1, 1):
            ex = cx + sgn * eye_dx
            line(cv, [
                (ex - eye_r * 1.3, brow_y - 2 * sgn),
                (ex + eye_r * 1.1, brow_y + 4 * sgn)
            ], max(3.2, 4.0 * s))
    elif mood == "sad":
        for sgn in (-1, 1):
            ex = cx + sgn * eye_dx
            line(cv, [
                (ex - eye_r * 1.2, brow_y + 3),
                (ex + eye_r * 1.1, brow_y - 2)
            ], max(3.0, 3.6 * s))

    # рот
    mouth_y = cy + hr * 0.32
    mw = hr * 0.42

    if mood == "smile":
        line(cv, [
            (cx - mw, mouth_y),
            (cx, mouth_y + hr * 0.22),
            (cx + mw, mouth_y)
        ], max(3.5, 4.2 * s))
    elif mood == "laugh":
        # открытый рот
        ell(cv, cx, mouth_y + hr * 0.06, hr * 0.28, hr * 0.22, (200, 90, 100), max(3.0, 3.5 * s))
        # прищуренные глаза сверху уже нарисованы как точки — добавим дуги
        for sgn in (-1, 1):
            ex = cx + sgn * eye_dx
            line(cv, [
                (ex - eye_r * 1.0, eye_y + 2),
                (ex, eye_y - eye_r * 0.7),
                (ex + eye_r * 1.0, eye_y + 2)
            ], max(2.8, 3.2 * s))
    elif mood == "shock":
        ell(cv, cx, mouth_y + 2, hr * 0.16, hr * 0.22, None, max(3.0, 3.5 * s))
    elif mood == "sad":
        line(cv, [
            (cx - mw * 0.9, mouth_y + hr * 0.12),
            (cx - mw * 0.25, mouth_y),
            (cx + mw * 0.25, mouth_y + hr * 0.12),
            (cx + mw * 0.9, mouth_y)
        ], max(3.2, 3.8 * s))
    elif mood == "angry":
        line(cv, [
            (cx - mw * 0.85, mouth_y + hr * 0.08),
            (cx, mouth_y - hr * 0.06),
            (cx + mw * 0.85, mouth_y + hr * 0.08)
        ], max(3.2, 3.8 * s))
    elif mood in ("flat", "tired", "sleep"):
        line(cv, [
            (cx - mw * 0.7, mouth_y),
            (cx + mw * 0.7, mouth_y)
        ], max(3.0, 3.5 * s))


def person(cv: Canvas, x: float, y: float, s: float = 1.0,
           shirt=(255, 255, 255), mood: str = "smile",
           L=(-40, 55), R=(40, 55), walk: float = None, hair=None):
    """
    Более стабильный стикмен.
    y — уровень ног (низ персонажа).
    """
    # пропорции
    leg = 95 * s
    tor = 88 * s
    hr = 42 * s

    hy = y - leg                    # таз
    sy = y - leg - tor              # плечи
    cx = x
    cy = sy - hr * 1.15             # центр головы

    # ноги
    for sgn in (-1, 1):
        if walk is not None:
            a = math.sin(walk + (0 if sgn < 0 else math.pi)) * 0.45
        else:
            a = sgn * 0.10
        fx = x + sgn * 11 * s + math.sin(a) * leg * 0.95
        fy = hy + math.cos(a) * leg * 0.97
        line(cv, [(x + sgn * 10 * s, hy), (fx, fy), (fx + 12 * s, fy)], max(5.0, 5.8 * s))

    # руки
    hands = []
    for sgn, (dx, dy) in ((-1, L), (1, R)):
        sx = x + sgn * 24 * s
        sy2 = sy + 8 * s
        hx = sx + dx * s
        hy2 = sy2 + dy * s
        mx = (sx + hx) / 2 + sgn * 5 * s
        my = (sy2 + hy2) / 2 + 6 * s
        line(cv, [(sx, sy2), (mx, my), (hx, hy2)], max(5.0, 5.8 * s))
        hands.append((hx, hy2))

    # тело (скруглённый прямоугольник)
    rrect(cv, x - 26 * s, sy, x + 26 * s, hy + 4 * s, 20 * s, shirt, max(5.0, 5.5 * s))

    # волосы (простые штрихи)
    if hair:
        for k in range(-2, 3):
            line(cv, [
                (cx + k * 8 * s, cy - hr + 1 * s),
                (cx + k * 11 * s, cy - hr - 12 * s)
            ], max(4.0, 4.5 * s), hair)

    face(cv, cx, cy, hr, s, mood)
    return cx, cy, hands[0], hands[1]


# ============================================================
# Objects
# ============================================================

BRAIN_PARTS = [(-110, 0, 85), (-40, -55, 95), (60, -50, 95), (120, 10, 80),
               (-60, 50, 85), (40, 60, 90), (-130, 45, 60), (125, 60, 60)]

def brain(cv: Canvas, cx: float, cy: float, k: float = 1.0, sc: float = 1.0):
    for dx, dy, r in BRAIN_PARTS:
        ell(cv, cx + dx * k * sc, cy + dy * k * sc, (r + 4) * k * sc, fill=INK, w=0)
    for dx, dy, r in BRAIN_PARTS:
        ell(cv, cx + dx * k * sc, cy + dy * k * sc, (r - 4) * k * sc, fill=(248, 176, 190), w=0)
    for pts in ([(-90, -20), (-60, -45), (-30, -15)],
               [(20, -70), (50, -40), (80, -75)],
               [(-30, 40), (0, 20), (40, 45), (70, 25)],
               [(80, 10), (110, 30)]):
        line(cv, [(cx + a * k * sc, cy + b * k * sc) for a, b in pts], 4 * sc, (210, 120, 140))


def arrow(cv: Canvas, x0: float, y0: float, x1: float, y1: float,
          w: float = 6, col=INK, k: float = 1.0):
    xe = x0 + (x1 - x0) * k
    ye = y0 + (y1 - y0) * k
    line(cv, [(x0, y0), (xe, ye)], w, col)
    if k > 0.85:
        a = math.atan2(y1 - y0, x1 - x0)
        for da in (2.6, -2.6):
            line(cv, [(xe, ye), (xe + math.cos(a + da) * 20, ye + math.sin(a + da) * 20)], w, col)


def zzz(cv: Canvas, x: float, y: float, t: float, col=WHITE, size: float = 34):
    for k in range(3):
        f = (t * 0.4 + k / 3) % 1
        text(cv, x + f * 60 + k * 6, y - f * 120, "Z",
             size * (0.6 + f * 0.8), col, alpha=math.sin(math.pi * f))


def clock(cv: Canvas, x: float, y: float, r: float, hh: float, mm: float, k: float = 1.0):
    ell(cv, x, y, r * k, fill=WHITE, w=6)
    for i in range(12):
        a = math.radians(i * 30 - 90)
        line(cv, [(x + math.cos(a) * r * 0.82 * k, y + math.sin(a) * r * 0.82 * k),
                  (x + math.cos(a) * r * 0.92 * k, y + math.sin(a) * r * 0.92 * k)], 4)
    for ang, ln, ww in ((hh, 0.5, 7), (mm, 0.78, 5)):
        a = math.radians(ang - 90)
        line(cv, [(x, y), (x + math.cos(a) * r * ln * k, y + math.sin(a) * r * ln * k)], ww)


def meter(cv: Canvas, t: float, y: float, lv: float, col, label: str, a: float,
          x0: float = 105, x1: float = 505, cx: float = None):
    if cx is None:
        cx = cv.cfg.center_x
    text(cv, cx, y - 60, label, 36, alpha=fa(t, a))
    if fa(t, a, 0.3) <= 0.02:
        return
    rrect(cv, x0, y - 20, x1, y + 20, 12, (245, 245, 240), 5)
    if lv > 0.02:
        rrect(cv, x0 + 3, y - 17, x0 + 3 + (x1 - x0 - 6) * lv, y + 17, 9, col, 0)
    rrect(cv, x0, y - 20, x1, y + 20, 12, None, 5)
    text(cv, cx, y + 2, f"{int(lv * 100)}%", 28)


def watermark(cv: Canvas, name: str = "uTeam", y: float = 62, size: float = 28, col=(150, 150, 160)):
    text(cv, cv.cfg.center_x, y, name, size, col)
