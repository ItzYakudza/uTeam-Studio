"""
uTeam-Studio
core/textfx.py — выразительный текст: слова по очереди, печать, волна, «удар», маркер, обведение,
счётчик, стикеры, облачка речи, субтитры-тезисы. Префикс tx_ у всех функций.
"""

import math
from typing import List, Sequence, Tuple

from .config import INK, WHITE, ACCENT_YELLOW, ACCENT_RED
from .primitives import (Canvas, text, twidth, fit, fit_safe, line, poly, ell, rrect, mix, pop, fa, ph, E,
                         get_font)
from .stage import group, clip
from .anim import EASES, decay, wiggle, jitter, rnd, clamp, tween


def tx_wrap(s: str, size: float, maxw: float) -> List[str]:
    """Перенос строки по словам под ширину maxw (логические пиксели)."""
    words, lines, cur = s.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if twidth(trial, size) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def tx_block(cv: Canvas, x: float, y: float, s: str, size: float = 48, maxw: float = 520,
             col=INK, stroke: float = 0, line_gap: float = 1.18, align: str = "m", stroke_col=INK):
    """Многострочный абзац с автопереносом. y — центр блока. Возвращает (верх, низ)."""
    lines = tx_wrap(s, size, maxw)
    h = size * line_gap
    top = y - h * (len(lines) - 1) / 2
    for i, ln in enumerate(lines):
        anchor = {"l": "lm", "m": "mm", "r": "rm"}[align]
        text(cv, x, top + i * h, ln, size, col, anchor, stroke, stroke_col=stroke_col)
    return top - h / 2, top + h * (len(lines) - 0.5)


def _layout_words(s: str, size: float, maxw: float, x: float, y: float, line_gap: float):
    lines = tx_wrap(s, size, maxw)
    h = size * line_gap
    top = y - h * (len(lines) - 1) / 2
    sp = twidth(" ", size)
    items = []
    for li, ln in enumerate(lines):
        ws = ln.split()
        widths = [twidth(w, size) for w in ws]
        tot = sum(widths) + sp * (len(ws) - 1)
        cx = x - tot / 2
        for w, wd in zip(ws, widths):
            items.append((w, cx + wd / 2, top + li * h))
            cx += wd + sp
    return items


def tx_words(cv: Canvas, t: float, a: float, s: str, x: float, y: float, size: float = 52, maxw: float = 540,
             gap: float = 0.14, d: float = 0.35, style: str = "pop", col=INK, stroke: float = 0,
             line_gap: float = 1.18, hi: dict = None, stroke_col=INK):
    """
    Слова появляются по очереди. style: "pop" (с овершутом), "rise" (всплывают снизу),
    "drop" (падают сверху), "fade". hi = {"слово": цвет} — подсветка отдельных слов.
    Возвращает время, когда появится последнее слово.
    """
    items = _layout_words(s, size, maxw, x, y, line_gap)
    hi = hi or {}
    for i, (w, wx, wy) in enumerate(items):
        u = (t - a - i * gap) / d
        if u <= 0:
            continue
        c = hi.get(w.strip(".,!?").lower(), hi.get(w, col))
        if style == "pop":
            text(cv, wx, wy, w, size, c, stroke=stroke, scale=EASES["back"](u), stroke_col=stroke_col)
        elif style == "rise":
            k = EASES["out"](u)
            text(cv, wx, wy + (1 - k) * size * 0.8, w, size, c, stroke=stroke, alpha=k, stroke_col=stroke_col)
        elif style == "drop":
            k = EASES["bounce"](u)
            text(cv, wx, wy - (1 - k) * size * 1.6, w, size, c, stroke=stroke, alpha=min(1, u * 4),
                 stroke_col=stroke_col)
        else:
            text(cv, wx, wy, w, size, c, stroke=stroke, alpha=clamp(u), stroke_col=stroke_col)
    return a + (len(items) - 1) * gap + d


def tx_typewriter(cv: Canvas, t: float, a: float, s: str, x: float, y: float, size: float = 44,
                  cps: float = 22, col=INK, cursor: bool = True, align: str = "lm", stroke: float = 0):
    """Печать по буквам. align: "lm" — слева (x = левый край), "mm" — по центру."""
    n = int(max(0.0, (t - a)) * cps)
    shown = s[:n]
    anchor = align
    if align == "mm":
        full_w = twidth(s, size)
        text(cv, x - full_w / 2, y, shown, size, col, "lm", stroke)
        cx = x - full_w / 2 + twidth(shown, size)
    else:
        text(cv, x, y, shown, size, col, "lm", stroke)
        cx = x + twidth(shown, size)
    if cursor and t >= a and (n < len(s) or int(t * 2) % 2 == 0):
        line(cv, [(cx + 4, y - size * 0.55), (cx + 4, y + size * 0.55)], 4, col)


def tx_wave(cv: Canvas, t: float, s: str, x: float, y: float, size: float = 56, amp: float = 10,
            speed: float = 3.0, col=INK, stroke: float = 0, hue: bool = False, stroke_col=INK):
    """Буквы бегут волной. hue=True — радужная раскраска."""
    total = twidth(s, size)
    cx = x - total / 2
    for i, ch in enumerate(s):
        wd = twidth(ch, size)
        if ch != " ":
            c = col
            if hue:
                c = tuple(int(127 + 120 * math.sin(i * 0.5 + t * 2 + off)) for off in (0, 2.1, 4.2))
            text(cv, cx + wd / 2, y + amp * math.sin(t * speed * 2 + i * 0.6), ch, size, c, stroke=stroke,
                 stroke_col=stroke_col)
        cx += wd


def tx_shake(cv: Canvas, t: float, s: str, x: float, y: float, size: float = 56, amp: float = 3,
             fps: float = 14, col=INK, stroke: float = 0, stroke_col=INK):
    """«Дрожащий» нервный текст (рисованный jitter)."""
    text(cv, x + jitter(t, amp, fps, 1), y + jitter(t, amp, fps, 2), s, size, col, stroke=stroke,
         rot=jitter(t, amp * 0.8, fps, 3), stroke_col=stroke_col)


def tx_slam(cv: Canvas, t: float, a: float, s: str, x: float, y: float, size: float = 72, col=INK,
            stroke: float = 0, rot: float = -4, from_scale: float = 2.6, d: float = 0.22,
            stroke_col=INK) -> float:
    """
    Текст «впечатывается» в экран: огромный -> нормальный за d секунд, лёгкий наклон.
    Возвращает силу удара (1 -> 0 после приземления) — подставь в cam(..., shake=...) для тряски.
    """
    u = (t - a) / d
    if u <= 0:
        return 0.0
    k = EASES["out4"](u)
    sc = from_scale + (1 - from_scale) * k
    text(cv, x, y, s, size, col, stroke=stroke, scale=sc, alpha=clamp(u * 3), rot=rot * k,
         stroke_col=stroke_col)
    return decay(t, a + d, 0.18) * 14


def tx_marker(cv: Canvas, t: float, a: float, s: str, x: float, y: float, size: float = 52, col=INK,
              hl=ACCENT_YELLOW, d: float = 0.45, pad: float = 10, stroke: float = 0):
    """Текст с подчёркивающей «маркерной» плашкой, которая проводится слева направо."""
    w = twidth(s, size)
    k = EASES["out"]((t - a) / d)
    if k > 0:
        x0 = x - w / 2 - pad
        poly(cv, [(x0, y - size * 0.38), (x0 + (w + 2 * pad) * k, y - size * 0.42),
                  (x0 + (w + 2 * pad) * k, y + size * 0.48), (x0, y + size * 0.52)], hl, 0)
    if t >= a:
        text(cv, x, y, s, size, col, stroke=stroke, alpha=clamp((t - a) / 0.15))


def tx_circle(cv: Canvas, t: float, a: float, x: float, y: float, w: float, h: float,
              col=ACCENT_RED, lw: float = 6, d: float = 0.5):
    """Рисованный от руки овал вокруг слова/объекта (слегка неряшливый, с нахлёстом)."""
    k = EASES["inout"]((t - a) / d)
    if k <= 0:
        return
    n = 40
    pts = []
    for i in range(int(n * 1.12 * k) + 1):
        ang = math.radians(-100 + 360 * 1.12 * i / n / 1.12 * 1.0)
        rr = 1 + 0.04 * (i / n)
        pts.append((x + w / 2 * rr * math.cos(ang), y + h / 2 * rr * math.sin(ang)))
    if len(pts) >= 2:
        line(cv, pts, lw, col)


def tx_underline(cv: Canvas, t: float, a: float, x: float, y: float, w: float, col=ACCENT_RED,
                 lw: float = 6, d: float = 0.4, wavy: bool = False):
    k = EASES["out"]((t - a) / d)
    if k <= 0:
        return
    if wavy:
        pts = [(x - w / 2 + w * i / 30 * k, y + 5 * math.sin(i * 0.9)) for i in range(31)]
    else:
        pts = [(x - w / 2, y), (x - w / 2 + w * k * 0.5, y + 2), (x - w / 2 + w * k, y)]
    line(cv, pts, lw, col)


def tx_strike(cv: Canvas, t: float, a: float, x: float, y: float, w: float, col=ACCENT_RED,
              lw: float = 8, d: float = 0.25):
    """Зачёркивание слова."""
    k = EASES["out"]((t - a) / d)
    if k > 0:
        line(cv, [(x - w / 2 - 6, y + 4), (x - w / 2 - 6 + (w + 12) * k, y - 4)], lw, col)


def tx_count(cv: Canvas, t: float, a: float, d: float, v0: float, v1: float, x: float, y: float,
             size: float = 90, col=INK, fmt: str = "{:,.0f}", prefix: str = "", suffix: str = "",
             stroke: float = 0, stroke_col=INK):
    """Число, которое «накручивается» от v0 до v1; в конце — маленький отскок."""
    k = EASES["out"]((t - a) / d)
    v = v0 + (v1 - v0) * k
    bump = 1 + 0.12 * decay(t, a + d, 0.12) if t >= a + d else 1.0
    if t >= a:
        text(cv, x, y, prefix + fmt.format(v) + suffix, size, col, stroke=stroke, scale=bump,
             stroke_col=stroke_col)


def tx_label(cv: Canvas, x: float, y: float, s: str, size: float = 34, fill=ACCENT_YELLOW, col=INK,
             rot: float = -3, k: float = 1.0, lw: float = 5):
    """Стикер-плашка с текстом (подпись к объекту). k — появление (pop)."""
    if k <= 0.03:
        return
    w, h = twidth(s, size) + size * 0.9, size * 1.5
    with group(cv, x, y, rot=rot, sc=k):
        rrect(cv, -w / 2, -h / 2, w / 2, h / 2, h * 0.28, fill, lw)
        text(cv, 0, 1, s, size, col)


def tx_bubble(cv: Canvas, x: float, y: float, s: str, size: float = 34, tail: Tuple[float, float] = None,
              maxw: float = 360, fill=WHITE, k: float = 1.0, thought: bool = False, lw: float = 5, col=INK):
    """
    Облачко речи с текстом по центру (x, y). tail=(tx, ty) — куда указывает хвостик.
    thought=True — облачко мысли (цепочка кружков вместо хвоста).
    """
    if k <= 0.03:
        return
    lines = tx_wrap(s, size, maxw)
    w = max(twidth(ln, size) for ln in lines) + size * 1.2
    h = size * 1.25 * len(lines) + size * 0.8
    with group(cv, x, y, sc=k):
        if thought:
            rrect(cv, -w / 2, -h / 2, w / 2, h / 2, min(h / 2, 40), fill, lw, col)
            if tail:
                tx_, ty_ = (tail[0] - x) / k, (tail[1] - y) / k
                for i, rr in enumerate((11, 8, 5)):
                    u = 0.35 + 0.28 * i
                    ell(cv, tx_ * u, h / 2 + (ty_ - h / 2) * u, rr, fill=fill, w=lw * 0.8, col=col)
        else:
            pts = [(-w / 2 + 20, -h / 2), (w / 2 - 20, -h / 2), (w / 2, -h / 2 + 20), (w / 2, h / 2 - 20),
                   (w / 2 - 20, h / 2), (-w / 2 + 20, h / 2), (-w / 2, h / 2 - 20), (-w / 2, -h / 2 + 20)]
            rrect(cv, -w / 2, -h / 2, w / 2, h / 2, 26, fill, lw, col)
            if tail:
                tx_, ty_ = (tail[0] - x) / k, (tail[1] - y) / k
                bx = max(-w / 2 + 36, min(w / 2 - 36, tx_ * 0.4))
                poly(cv, [(bx - 16, h / 2 - 3), (tx_, ty_), (bx + 16, h / 2 - 3)], fill, 0)
                line(cv, [(bx - 16, h / 2), (tx_, ty_), (bx + 16, h / 2)], lw, col)
        top = -h / 2 + size * 0.4 + size * 0.625
        for i, ln in enumerate(lines):
            text(cv, 0, top + i * size * 1.25 - size * 0.05, ln, size, col)


def tx_reveal(cv: Canvas, t: float, a: float, s: str, x: float, y: float, size: float = 52, d: float = 0.8,
              col=INK, stroke: float = 0, stroke_col=INK):
    """Текст проявляется слева направо, как будто пишется (маска-шторка)."""
    w = twidth(s, size) + 30
    k = EASES["inout"]((t - a) / d)
    if k <= 0:
        return
    box = (x - w / 2, y - size, x + w / 2, y + size)
    with clip(cv, ("rect", x - w / 2, y - size, x - w / 2 + w * k, y + size), box=box):
        text(cv, x, y, s, size, col, stroke=stroke, stroke_col=stroke_col)


def tx_cap(cv: Canvas, t: float, a: float, b: float, s: str, y: float = 620, size: float = 54,
           col=WHITE, stroke: float = 6, cx: float = None, maxw: float = None, pop_d: float = 0.18):
    """
    Субтитр-тезис «по протоколу хука»: появляется на a с быстрым поп-эффектом, исчезает на b.
    Крупный светлый текст с тёмной обводкой по центру safe-zone. Одна строка автоуменьшается под maxw.
    """
    if not (a <= t < b):
        return
    cx = cv.cfg.center_x if cx is None else cx
    sz = fit_safe(cv, s, size, cx) if maxw is None else fit(s, size, maxw)
    text(cv, cx, y, s, sz, col, stroke=stroke, scale=pop(t, a, pop_d))
