"""
uTeam-Studio
core/anim.py — твины, кейфреймы, easing-кривые, шум. Всё — чистые функции от времени t
(рендер может запрашивать кадры в любом порядке, состояния нет).
"""

import math
from typing import Sequence, Tuple, Union

from .primitives import seg, E, back, mix

Num = Union[float, int]


# ============================================================
# Easing-кривые: x in [0..1] -> [0..1] (некоторые выходят за 1 — овершут)
# ============================================================

def lerp(a, b, k):
    if isinstance(a, (tuple, list)):
        return tuple(lerp(x, y, k) for x, y in zip(a, b))
    return a + (b - a) * k


def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return lo if x < lo else hi if x > hi else x


def e_in(x):      x = clamp(x); return x * x * x
def e_out(x):     x = clamp(x); return 1 - (1 - x) ** 3
def e_inout(x):   return E(clamp(x))
def e_out4(x):    x = clamp(x); return 1 - (1 - x) ** 5
def e_expo(x):    x = clamp(x); return 1.0 if x >= 1 else 1 - 2 ** (-10 * x)
def e_back(x):    return back(x)


def e_elastic(x: float) -> float:
    x = clamp(x)
    if x in (0.0, 1.0):
        return x
    return 2 ** (-10 * x) * math.sin((x * 10 - 0.75) * (2 * math.pi) / 3) + 1


def e_bounce(x: float) -> float:
    x = clamp(x)
    n1, d1 = 7.5625, 2.75
    if x < 1 / d1:
        return n1 * x * x
    if x < 2 / d1:
        x -= 1.5 / d1
        return n1 * x * x + 0.75
    if x < 2.5 / d1:
        x -= 2.25 / d1
        return n1 * x * x + 0.9375
    x -= 2.625 / d1
    return n1 * x * x + 0.984375


def e_spring(x: float, damp: float = 6.0, freq: float = 3.0) -> float:
    """Затухающая пружина: перелетает цель и успокаивается."""
    x = clamp(x)
    return 1 - math.exp(-damp * x) * math.cos(freq * 2 * math.pi * x)


def e_snap(x: float) -> float:
    """Резкий старт и мягкая посадка (хорошо для ударов и «шлёпов»)."""
    x = clamp(x)
    return 1 - (1 - x) ** 6


def e_linear(x):  return clamp(x)


EASES = {
    "linear": e_linear, "in": e_in, "out": e_out, "inout": e_inout,
    "out4": e_out4, "expo": e_expo, "back": e_back,
    "elastic": e_elastic, "bounce": e_bounce, "spring": e_spring, "snap": e_snap,
}


def ez(x: float, kind: str = "inout") -> float:
    return EASES[kind](x)


# ============================================================
# Твины и кейфреймы
# ============================================================

def tween(t: float, a: float, d: float, v0=0.0, v1=1.0, kind: str = "inout"):
    """Значение от v0 к v1: старт в момент a, длительность d. v0/v1 могут быть кортежами (цвета, точки)."""
    k = EASES[kind]((t - a) / d) if d > 0 else (1.0 if t >= a else 0.0)
    return lerp(v0, v1, k)


def keyframes(t: float, keys: Sequence[Tuple[float, object]], kind: str = "inout"):
    """
    Кусочная интерполяция: keys = [(время, значение), ...] по возрастанию времени.
    Значения — числа или кортежи. kind применяется к каждому отрезку.
    """
    if t <= keys[0][0]:
        return keys[0][1]
    if t >= keys[-1][0]:
        return keys[-1][1]
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t0 <= t <= t1:
            return lerp(v0, v1, EASES[kind]((t - t0) / (t1 - t0)))
    return keys[-1][1]


def stagger(t: float, a: float, i: int, gap: float = 0.12, d: float = 0.4, kind: str = "back") -> float:
    """Появление i-го элемента списка со сдвигом gap секунд (0..1, с овершутом для 'back')."""
    return EASES[kind]((t - a - i * gap) / d)


def decay(t: float, a: float, tau: float = 0.25) -> float:
    """Экспоненциальное затухание после момента a: 1 в момент удара -> 0. До a = 0."""
    if t < a:
        return 0.0
    return math.exp(-(t - a) / tau)


# ============================================================
# Периодика и шум (детерминированные)
# ============================================================

def pulse(t: float, period: float = 1.0, amp: float = 0.06, phase: float = 0.0) -> float:
    """Масштабный «пульс»: около 1.0 ± amp."""
    return 1.0 + amp * math.sin(2 * math.pi * (t / period + phase))


def bob(t: float, amp: float = 8.0, period: float = 2.0, phase: float = 0.0) -> float:
    """Плавное покачивание вверх-вниз (в пикселях)."""
    return amp * math.sin(2 * math.pi * (t / period + phase))


def wiggle(t: float, amp: float = 1.0, freq: float = 3.0, seed: int = 0) -> float:
    """Гладкий псевдо-шум в диапазоне [-amp .. amp]."""
    s = seed * 12.9898
    v = (math.sin(t * freq * 6.283 + s) * 0.55
         + math.sin(t * freq * 2.31 * 6.283 + s * 1.7) * 0.30
         + math.sin(t * freq * 4.77 * 6.283 + s * 2.3) * 0.15)
    return amp * v


def jitter(t: float, amp: float = 2.0, fps: float = 12.0, seed: int = 0) -> float:
    """Ступенчатая «рисованная» дрожь: меняется fps раз в секунду (эффект boil у рисованных линий)."""
    k = math.floor(t * fps)
    return amp * (rnd(k * 7 + seed) * 2 - 1)


def rnd(n: float) -> float:
    """Детерминированный псевдо-random 0..1 по целому/дробному числу."""
    x = math.sin(n * 127.1 + 311.7) * 43758.5453
    return x - math.floor(x)


def blink(t: float, period: float = 3.4, dur: float = 0.14, phase: float = 0.0) -> float:
    """Открытость глаз: 1 — открыты, 0 — закрыты. Моргание раз в period секунд."""
    u = (t + phase * period) % period
    if u > period - dur:
        k = (u - (period - dur)) / dur
        return abs(2 * k - 1)
    return 1.0


def talk(t: float, a: float, b: float, speed: float = 9.0) -> float:
    """Открытость рта 0..1 при речи между a и b (ритмичное «бла-бла»)."""
    if not (a <= t <= b):
        return 0.0
    v = abs(math.sin(t * speed)) * (0.55 + 0.45 * math.sin(t * speed * 0.37 + 1.3) ** 2)
    return clamp(v)


def lerp_col(a, b, k):
    return mix(a, b, k)
