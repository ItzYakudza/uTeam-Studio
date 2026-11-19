"""
uTeam-Studio
core/fx.py — экранные эффекты (вспышка, виньетка, прожектор, глитч, letterbox)
и частицы (конфетти, искры, дождь, снег, пузыри, дым, взрыв). Без состояния: всё зависит только от t.
"""

import math
from typing import Sequence, Tuple

import numpy as np
from PIL import Image, ImageChops

from .config import INK, WHITE
from .primitives import Canvas, line, poly, ell, mix, ph, E
from .anim import rnd, decay, clamp, wiggle

_mask_cache = {}


# ============================================================
# Экранные эффекты (работают в пикселях всего холста, поверх нарисованного)
# ============================================================

def _overlay(cv: Canvas, col, mask: Image.Image):
    """Наложить цвет col через L-маску (размером с холст)."""
    cv.im.paste(col, (0, 0), mask)


def flash(cv: Canvas, t: float, a: float, d: float = 0.25, col=WHITE, peak: float = 0.9):
    """
    Белая (или цветная) вспышка в момент a, затухает за d секунд.
    Накладывается ПОВЕРХ всего кадра при его выдаче (быстро, порядок вызова не важен).
    """
    if not (a <= t <= a + d):
        return
    k = (1 - (t - a) / d) * peak
    cv.post.append(lambda im: Image.blend(im, Image.new("RGB", im.size, col), k))


def tint(cv: Canvas, col, alpha: float):
    """Залить весь кадр цветом с прозрачностью (затемнение, «красная тревога», ночь)."""
    if alpha > 0.01:
        _overlay(cv, col, Image.new("L", cv.im.size, int(255 * clamp(alpha))))


def _radial_mask(size, cx, cy, r_in, r_out, invert):
    """Мягкая радиальная маска, считается в низком разрешении и растягивается (быстро)."""
    W, H = size
    sc = 8
    w, h = max(2, W // sc), max(2, H // sc)
    yy, xx = np.mgrid[0:h, 0:w]
    dist = np.hypot((xx + 0.5) * sc - cx, (yy + 0.5) * sc - cy)
    k = np.clip((dist - r_in) / max(1.0, (r_out - r_in)), 0, 1)
    if not invert:
        k = 1 - k
    k = k * k * (3 - 2 * k)
    return Image.fromarray((k * 255).astype(np.uint8), "L").resize(size, Image.BILINEAR)


def vignette(cv: Canvas, strength: float = 0.45, col=(0, 0, 0)):
    """
    Затемнение по краям кадра — фокусирует взгляд на центре.
    Накладывается ПОВЕРХ всего кадра при выдаче (быстро; маска кэшируется).
    """
    def apply(im):
        W, H = im.size
        key = ("vig", W, H, round(strength, 2))
        if key not in _mask_cache:
            m = _radial_mask((W, H), W / 2, H / 2, min(W, H) * 0.45, math.hypot(W, H) * 0.55, invert=True)
            _mask_cache[key] = m.point(lambda v: int(v * strength))
        im = im.copy()
        im.paste(col, (0, 0), _mask_cache[key])
        return im
    cv.post.append(apply)


def spotlight(cv: Canvas, x: float, y: float, r: float, dark: float = 0.65, soft: float = 0.5,
              col=(0, 0, 0)):
    """
    «Прожектор»: всё затемнено, кроме круга радиуса r вокруг точки мира (x, y). Классический акцент в explainer.
    soft — мягкость края (доля радиуса).
    """
    px, py = cv.pt(x, y)
    pr = r * cv.sc
    m = _radial_mask(cv.im.size, px + cv.ox, py + cv.oy, pr, pr * (1 + soft), invert=True)
    _overlay(cv, col, m.point(lambda v: int(v * dark)))


def letterbox(cv: Canvas, k: float = 0.1, col=(0, 0, 0)):
    """Чёрные полосы сверху/снизу (k — доля высоты каждой). Кинематографичный акцент."""
    if k <= 0.001:
        return
    W, H = cv.im.size
    h = int(H * k)
    cv.d.rectangle([0, 0, W, h], fill=col)
    cv.d.rectangle([0, H - h, W, H], fill=col)


def glitch(cv: Canvas, t: float, a: float, d: float = 0.3, amount: float = 0.06, seed: int = 0):
    """RGB-сдвиг и горизонтальные «порванные» полосы в течение d секунд после a (шок-хук, ошибка, помехи)."""
    if not (a <= t <= a + d):
        return
    W, H = cv.im.size
    k = 1 - (t - a) / d
    fr = int(t * 30)
    im = cv.im
    r, g, b = im.split()
    sh = int(W * amount * k * (0.5 + rnd(fr + seed)))
    r = ImageChops.offset(r, sh, 0)
    b = ImageChops.offset(b, -sh, 0)
    im2 = Image.merge("RGB", (r, g, b))
    for i in range(int(3 + 7 * k)):
        y0 = int(rnd(fr * 13 + i * 5 + seed) * H)
        hh = int(H * (0.01 + 0.05 * rnd(fr * 7 + i + seed)))
        dx = int((rnd(fr * 3 + i * 11 + seed) - 0.5) * W * 0.25 * k)
        strip = im2.crop((0, y0, W, min(H, y0 + hh)))
        im2.paste(ImageChops.offset(strip, dx, 0), (0, y0))
    cv.im.paste(im2)


# ============================================================
# Частицы
# ============================================================

CONFETTI_COLS = [(235, 90, 80), (250, 205, 50), (90, 150, 240), (110, 200, 110), (248, 160, 190), (165, 125, 225)]


def confetti(cv: Canvas, t: float, a: float, cx: float, cy: float, n: int = 40, spread: float = 260,
             power: float = 520, gravity: float = 900, life: float = 1.8, size: float = 11, seed: int = 0,
             colors=CONFETTI_COLS):
    """Салют из конфетти: вылет из точки (cx, cy) в момент a."""
    u = t - a
    if u < 0 or u > life:
        return
    for i in range(n):
        ang = math.radians(-90 + (rnd(i * 3 + seed) - 0.5) * spread)
        v = power * (0.35 + 0.65 * rnd(i * 5 + 1 + seed))
        x = cx + math.cos(ang) * v * u * 0.55 + (rnd(i + 9) - 0.5) * 20
        y = cy + math.sin(ang) * v * u + 0.5 * gravity * u * u * 0.5
        rot = (rnd(i * 7 + seed) * 360 + u * 360 * (rnd(i) - 0.5) * 3)
        fade = 1.0 if u < life * 0.7 else 1 - (u - life * 0.7) / (life * 0.3)
        w, h = size * (0.7 + rnd(i + 2)), size * 0.45 * (0.6 + rnd(i + 4))
        c = colors[i % len(colors)]
        c = mix(cv.bg, c, fade)
        ca, sa = math.cos(math.radians(rot)), math.sin(math.radians(rot))
        pts = [cv.pt(x + (dx * ca - dy * sa), y + (dx * sa + dy * ca))
               for dx, dy in ((-w, -h), (w, -h), (w, h), (-w, h))]
        cv.d.polygon(pts, fill=c)


def sparkles(cv: Canvas, t: float, cx: float, cy: float, r: float = 120, n: int = 6, size: float = 16,
             col=(250, 205, 50), seed: int = 0, speed: float = 1.4):
    """Мерцающие четырёхлучевые звёздочки вокруг точки (бесконечно)."""
    for i in range(n):
        ph_ = (t * speed * (0.6 + 0.8 * rnd(i + seed)) + rnd(i * 3 + seed)) % 1.0
        k = math.sin(math.pi * ph_)
        if k < 0.05:
            continue
        ang = rnd(i * 5 + seed + ((t * speed) // 1)) * math.tau
        rr = r * (0.55 + 0.6 * rnd(i * 7 + seed))
        x, y = cx + rr * math.cos(ang), cy + rr * math.sin(ang)
        s = size * k
        poly(cv, [(x, y - s), (x + s * 0.28, y - s * 0.28), (x + s, y), (x + s * 0.28, y + s * 0.28),
                  (x, y + s), (x - s * 0.28, y + s * 0.28), (x - s, y), (x - s * 0.28, y - s * 0.28)],
             col, 3)


def rain(cv: Canvas, t: float, n: int = 60, col=(110, 160, 230), length: float = 38, speed: float = 900,
         seed: int = 0, slant: float = 0.18, w: float = 4):
    """Дождь на весь экран (логические координаты)."""
    cfg = cv.cfg
    for i in range(n):
        x0 = rnd(i * 3 + seed) * (cfg.width + 200) - 100
        ph_ = (t * speed / (cfg.height + 100) * (0.8 + 0.4 * rnd(i + seed)) + rnd(i * 7 + seed)) % 1.0
        y = -50 + ph_ * (cfg.height + 100)
        x = x0 + y * slant
        line(cv, [(x, y), (x + slant * length, y + length)], w, col)


def snow(cv: Canvas, t: float, n: int = 50, col=WHITE, speed: float = 90, seed: int = 0, size: float = 7):
    cfg = cv.cfg
    for i in range(n):
        sp = (0.5 + rnd(i * 5 + seed))
        ph_ = (t * speed * sp / (cfg.height + 60) + rnd(i * 7 + seed)) % 1.0
        y = -30 + ph_ * (cfg.height + 60)
        x = rnd(i * 3 + seed) * cfg.width + 25 * math.sin(t * 1.3 * sp + i)
        r = size * (0.5 + rnd(i + 3 + seed))
        px, py = cv.pt(x, y)
        rr = r * cv.sc
        cv.d.ellipse([px - rr, py - rr, px + rr, py + rr], fill=mix(cv.bg, col, 0.95))


def bubbles(cv: Canvas, t: float, x0: float, x1: float, y_from: float, y_to: float, n: int = 14,
            col=(255, 255, 255), seed: int = 0, size: float = 18):
    """Пузыри поднимаются от y_from к y_to в полосе x0..x1."""
    for i in range(n):
        sp = 0.12 + 0.12 * rnd(i + seed)
        ph_ = (t * sp + rnd(i * 5 + seed)) % 1.0
        y = y_from + (y_to - y_from) * ph_
        x = x0 + (x1 - x0) * rnd(i * 3 + seed) + 10 * math.sin(t * 2 + i)
        r = size * (0.4 + rnd(i + 8 + seed))
        a = math.sin(math.pi * ph_)
        ell(cv, x, y, r, fill=None, w=3, col=mix(cv.bg, col, a))
        ell(cv, x - r * 0.3, y - r * 0.3, r * 0.18, fill=mix(cv.bg, col, a), w=0)


def burst(cv: Canvas, t: float, a: float, cx: float, cy: float, r: float = 110, spikes: int = 12,
          fill=(250, 205, 50), d: float = 0.55, col=INK, w: float = 5):
    """Комикс-«бабах»: зубчатая звезда быстро растёт и гаснет."""
    u = t - a
    if u < 0 or u > d:
        return
    k = 1 - (1 - min(1.0, u / (d * 0.45))) ** 3
    fade = 1.0 if u < d * 0.6 else 1 - (u - d * 0.6) / (d * 0.4)
    pts = []
    for i in range(spikes * 2):
        rr = r * k * (1.0 if i % 2 == 0 else 0.62) * (0.9 + 0.2 * rnd(i + 3))
        ang = math.pi * i / spikes + 0.2
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    poly(cv, pts, mix(cv.bg, fill, fade), w, mix(cv.bg, col, fade))


def puff(cv: Canvas, t: float, a: float, x: float, y: float, r: float = 40, d: float = 0.9,
         col=(245, 245, 250), n: int = 5, rise: float = 40):
    """Клубок дыма/пыли: несколько кругов расходятся и тают."""
    u = t - a
    if u < 0 or u > d:
        return
    k = u / d
    for i in range(n):
        ang = math.tau * i / n + 0.4
        dist = r * 0.9 * E(k)
        rr = r * (0.55 + 0.5 * k) * (0.8 + 0.4 * rnd(i + 4))
        ell(cv, x + dist * math.cos(ang), y + dist * math.sin(ang) * 0.6 - rise * k, rr,
            fill=mix(cv.bg, col, 1 - k), w=3, col=mix(cv.bg, INK, (1 - k) * 0.7))


def ripple(cv: Canvas, t: float, a: float, x: float, y: float, r: float = 120, n: int = 3, d: float = 1.1,
           col=(90, 150, 240), w: float = 5, squash: float = 1.0):
    """Расходящиеся круги (волны, сигнал, удар об воду)."""
    for i in range(n):
        u = (t - a - i * d * 0.25) / d
        if 0 < u < 1:
            k = 1 - (1 - u) ** 2
            ell(cv, x, y, r * k, r * k * squash, w=w, col=mix(cv.bg, col, 1 - u))


def speed_lines(cv: Canvas, t: float, cx: float, cy: float, r0: float = 160, r1: float = 700, n: int = 26,
                col=INK, w: float = 4, seed: int = 0, fps: float = 18, alpha: float = 0.8):
    """Манга-линии скорости из точки (фон «рывка», удара, озарения). Мерцают на fps кадрах/с."""
    fr = math.floor(t * fps)
    c = mix(cv.bg, col, alpha)
    for i in range(n):
        ang = math.tau * (i + rnd(fr * 3 + i + seed) * 0.8) / n
        a0 = r0 * (1 + 0.4 * rnd(fr + i * 5 + seed))
        a1 = r1 * (0.7 + 0.5 * rnd(fr * 7 + i + seed))
        line(cv, [(cx + a0 * math.cos(ang), cy + a0 * math.sin(ang)),
                  (cx + a1 * math.cos(ang), cy + a1 * math.sin(ang))], w * (0.6 + rnd(i + seed)), c)


def emphasis(cv: Canvas, t: float, cx: float, cy: float, r: float = 70, n: int = 8, col=INK, w: float = 5,
             length: float = 22, fps: float = 10, span: float = 220):
    """Короткие лучики вокруг объекта («!», дрожь, удивление). span — угол дуги в градусах (360 = круг)."""
    pulse_k = 0.5 + 0.5 * math.sin(t * math.tau * fps / 2)
    for i in range(n):
        ang = math.radians(-90 - span / 2 + span * i / max(1, n - 1))
        r0, r1 = r + 8, r + 8 + length * (0.6 + 0.6 * pulse_k)
        line(cv, [(cx + r0 * math.cos(ang), cy + r0 * math.sin(ang)),
                  (cx + r1 * math.cos(ang), cy + r1 * math.sin(ang))], w, col)


def motion_trail(cv: Canvas, x0: float, y0: float, x1: float, y1: float, n: int = 3, col=INK, w: float = 4,
                 gap: float = 14):
    """Параллельные штрихи «за» движущимся объектом: от (x0,y0) к (x1,y1)."""
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy) or 1
    nx, ny = -dy / L, dx / L
    for i in range(n):
        o = (i - (n - 1) / 2) * gap
        line(cv, [(x0 + nx * o, y0 + ny * o), (x1 + nx * o, y1 + ny * o)], w, col)
