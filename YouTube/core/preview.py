"""
uTeam-Studio
core/transitions.py — переходы между сценами.

В scenes.py:
    TRANSITIONS = {1: "iris", 2: "zoom", 4: "whip:0.5", 6: "flash"}   # ключ = индекс сцены, куда переходим
Формат значения: "имя" или "имя:длительность_сек". Без записи работает привычный "slide".
Доступно: slide, slide_right, slide_up, slide_down, fade, zoom, iris, wipe, blinds, flash, whip, pixel, cut
"""

import math
from typing import Tuple, Optional

import numpy as np
from PIL import Image, ImageDraw

from .primitives import E

NAMES = ("slide", "slide_right", "slide_up", "slide_down", "fade", "zoom", "iris", "wipe",
         "blinds", "flash", "whip", "pixel", "cut")


def parse(spec, default_dur: float) -> Tuple[str, float]:
    if spec is None:
        return "slide", default_dur
    name, _, dur = str(spec).partition(":")
    name = name.strip().lower()
    if name not in NAMES:
        raise ValueError(f"Неизвестный переход {name!r}. Доступно: {', '.join(NAMES)}")
    return name, (float(dur) if dur else default_dur)


def _zoom(im: Image.Image, z: float) -> Image.Image:
    W, H = im.size
    if z <= 1.001:
        return im
    big = im.resize((int(W * z), int(H * z)), Image.BILINEAR)
    x0, y0 = (big.width - W) // 2, (big.height - H) // 2
    return big.crop((x0, y0, x0 + W, y0 + H))


def _hblur(im: Image.Image, length: int) -> Image.Image:
    if length < 2:
        return im
    arr = np.asarray(im).astype(np.float32)
    acc = np.zeros_like(arr)
    n = min(9, length)
    for i in range(n):
        acc += np.roll(arr, int((i - n / 2) * length / n), axis=1)
    return Image.fromarray((acc / n).astype(np.uint8))


def apply(name: str, prev: Image.Image, nxt: Image.Image, p: float) -> Image.Image:
    """p — линейный прогресс 0..1. Возвращает кадр перехода."""
    W, H = nxt.size
    e = E(max(0.0, min(1.0, p)))
    if name == "cut":
        return nxt if p > 0.5 else prev
    if name in ("slide", "slide_right", "slide_up", "slide_down"):
        out = Image.new("RGB", (W, H))
        if name == "slide":
            dx = int(W * e); out.paste(prev, (-dx, 0)); out.paste(nxt, (W - dx, 0))
        elif name == "slide_right":
            dx = int(W * e); out.paste(prev, (dx, 0)); out.paste(nxt, (dx - W, 0))
        elif name == "slide_up":
            dy = int(H * e); out.paste(prev, (0, -dy)); out.paste(nxt, (0, H - dy))
        else:
            dy = int(H * e); out.paste(prev, (0, dy)); out.paste(nxt, (0, dy - H))
        return out
    if name == "fade":
        return Image.blend(prev, nxt, e)
    if name == "zoom":
        a = _zoom(prev, 1 + 0.6 * e)
        b = _zoom(nxt, 1.6 - 0.6 * e)
        return Image.blend(a, b, E(max(0.0, (e - 0.25) / 0.75)))
    if name == "iris":
        r = math.hypot(W, H) / 2 * e
        m = Image.new("L", (W, H), 0)
        ImageDraw.Draw(m).ellipse([W / 2 - r, H / 2 - r, W / 2 + r, H / 2 + r], fill=255)
        return Image.composite(nxt, prev, m)
    if name == "wipe":
        yy, xx = np.mgrid[0:H, 0:W]
        d = (xx / W + yy / H) / 2
        m = Image.fromarray((d < e * 1.04 - 0.02).astype(np.uint8) * 255, "L")
        return Image.composite(nxt, prev, m)
    if name == "blinds":
        n = 8
        m = Image.new("L", (W, H), 0)
        md = ImageDraw.Draw(m)
        bw = W / n
        for i in range(n):
            md.rectangle([i * bw, 0, i * bw + bw * e, H], fill=255)
        return Image.composite(nxt, prev, m)
    if name == "flash":
        white = Image.new("RGB", (W, H), (255, 255, 255))
        return Image.blend(prev, white, p * 2) if p < 0.5 else Image.blend(white, nxt, (p - 0.5) * 2)
    if name == "whip":
        out = Image.new("RGB", (W, H))
        dx = int(W * e)
        out.paste(prev, (-dx, 0)); out.paste(nxt, (W - dx, 0))
        return _hblur(out, int(W * 0.10 * math.sin(math.pi * e)))
    if name == "pixel":
        k = math.sin(math.pi * e)
        base = Image.blend(prev, nxt, e)
        f = max(1, int(1 + 38 * k))
        small = base.resize((max(1, W // f), max(1, H // f)), Image.NEAREST)
        return small.resize((W, H), Image.NEAREST)
    return nxt
