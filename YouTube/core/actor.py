"""
uTeam-Studio
core/actor.py — живые персонажи: глаза (взгляд, моргание), рот (речь), брови, актёр со скелетом
(IK-руки, наклон, походка, сквош) и универсальный зверёк critter.
Стиль тот же, что у person(): белая круглая голова, толстый контур.
"""

import math
from typing import Tuple, Optional

from .config import INK, WHITE
from .primitives import Canvas, line, poly, ell, rrect, mix
from .stage import group
from .kit import PAL, ik2, tube, capsule, darken, lighten
from .anim import blink as _blink


# ============================================================
# Части лица
# ============================================================

def eyes(cv: Canvas, cx: float, cy: float, gap: float, r: float, look: Tuple[float, float] = (0, 0),
         open_k: float = 1.0, mood: str = "smile", lw: float = 4.0):
    """
    Пара глаз с центром (cx, cy). gap — смещение каждого глаза от центра, r — радиус.
    look=(-1..1, -1..1) — куда смотрят зрачки; open_k 0..1 — моргание (blink() из anim).
    """
    for sgn in (-1, 1):
        ex = cx + sgn * gap
        if mood == "sleep" or open_k < 0.12:
            line(cv, [(ex - r * 1.1, cy), (ex, cy + r * 0.6), (ex + r * 1.1, cy)], lw)
        elif mood == "shock":
            ell(cv, ex, cy, r * 1.75, fill=WHITE, w=lw * 0.8)
            ell(cv, ex + look[0] * r * 0.7, cy + look[1] * r * 0.7, r * 0.7, fill=INK, w=0)
        elif mood == "laugh":
            line(cv, [(ex - r * 1.0, cy + 2), (ex, cy - r * 0.8), (ex + r * 1.0, cy + 2)], lw)
        else:
            rx = r * (1.0 if mood != "tired" else 0.9)
            ell(cv, ex + look[0] * r * 0.8, cy + look[1] * r * 0.8, rx, rx * max(0.12, open_k), fill=INK, w=0)
            if mood == "tired":
                line(cv, [(ex - r * 1.2, cy + r * 1.35), (ex, cy + r * 1.8), (ex + r * 1.2, cy + r * 1.35)],
                     lw * 0.7, (140, 120, 170))


def brows(cv: Canvas, cx: float, cy: float, gap: float, r: float, mood: str = "smile", raise_k: float = 0.0,
          lw: float = 4.0):
    """Брови: angry (внутренние концы вниз), sad (внутренние концы вверх), shock/raise_k (дуга вверх)."""
    y = cy - r * 2.2 - raise_k * r * 1.2
    for sg in (-1, 1):
        ex = cx + sg * gap
        inner = -sg          # знак направления к центру лица
        x_in, x_out = ex + inner * r * 1.2, ex - inner * r * 1.3
        if mood == "angry":
            line(cv, [(x_out, y - 4), (x_in, y + 5)], lw)
        elif mood == "sad":
            line(cv, [(x_out, y + 3), (x_in, y - 5)], lw)
        elif mood in ("shock", "wow") or raise_k > 0.05:
            line(cv, [(ex - r * 1.2, y + 2), (ex, y - 4), (ex + r * 1.2, y + 2)], lw)


def mouth(cv: Canvas, cx: float, cy: float, w: float, mood: str = "smile", open_k: float = 0.0, lw: float = 4.2):
    """
    Рот шириной w. open_k 0..1 — открытость (речь/смех). Настроения: smile, smirk, laugh, shock,
    sad, angry, flat, tired, sleep, wow.
    """
    if open_k > 0.08 and mood not in ("laugh", "shock", "wow"):
        ell(cv, cx, cy + w * 0.1, w * 0.42, w * (0.12 + 0.34 * open_k), (200, 90, 100), lw * 0.8)
        return
    if mood == "smile":
        line(cv, [(cx - w, cy), (cx, cy + w * 0.5), (cx + w, cy)], lw)
    elif mood == "smirk":
        line(cv, [(cx - w * 0.7, cy + 2), (cx + w * 0.2, cy + w * 0.2), (cx + w, cy - w * 0.3)], lw)
    elif mood == "laugh":
        ell(cv, cx, cy + w * 0.15, w * 0.68, w * (0.45 + 0.2 * open_k), (200, 90, 100), lw * 0.8)
    elif mood in ("shock", "wow"):
        ell(cv, cx, cy + 3, w * 0.38, w * 0.52, None, lw * 0.8)
    elif mood == "sad":
        line(cv, [(cx - w * 0.9, cy + w * 0.3), (cx - w * 0.25, cy), (cx + w * 0.25, cy), (cx + w * 0.9, cy + w * 0.3)], lw)
    elif mood == "angry":
        line(cv, [(cx - w * 0.85, cy + w * 0.2), (cx, cy - w * 0.15), (cx + w * 0.85, cy + w * 0.2)], lw)
    else:  # flat / tired / sleep
        line(cv, [(cx - w * 0.7, cy), (cx + w * 0.7, cy)], lw)


# ============================================================
# Актёр
# ============================================================

def actor(cv: Canvas, x: float, y: float, s: float = 1.0, mood: str = "smile",
          look: Tuple[float, float] = (0, 0), blink_k: float = 1.0, talk_k: float = 0.0,
          shirt=WHITE, hair=None, lean: float = 0.0, tilt: float = 0.0,
          hand_l: Optional[Tuple[float, float]] = None, hand_r: Optional[Tuple[float, float]] = None,
          walk: Optional[float] = None, squash: float = 1.0, flip: bool = False,
          brow_raise: float = 0.0, bob_k: float = 0.0, lw: float = 5.8) -> dict:
    """
    Персонаж со скелетом. (x, y) — точка между ступнями.
      mood      — smile, laugh, shock, sad, angry, flat, tired, sleep, smirk
      look      — взгляд (-1..1, -1..1); blink_k — из anim.blink(t); talk_k — из anim.talk(t, a, b)
      lean      — наклон корпуса вперёд/назад (градусы, вокруг таза); tilt — наклон головы
      hand_l/r  — куда тянутся кисти: (dx, dy) от ступней в пикселях СЦЕНЫ (dy<0 — выше ног).
                  Рука сама сгибается в локте (IK). None — расслабленно / машет при walk.
      walk      — фаза походки в радианах (передавай t * 6); squash — сжатие по высоте (приземление)
      flip      — смотреть влево
    Возвращает dict(head=(x, y), hand_l=(x, y), hand_r=(x, y)) в координатах сцены — привязывай предметы.
    """
    leg_l, tor, hr = 95.0, 88.0, 42.0
    sgn_f = -1 if flip else 1
    hip = (0.0, -leg_l)
    sh_y = -leg_l - tor
    bob = abs(math.sin(walk)) * 4 if walk is not None else bob_k
    out = {}

    def to_world(lx, ly):
        return (x + sgn_f * lx * s, y + ly * s * squash)

    with group(cv, x, y - bob * s, sc=s, sy=s * squash, flip=flip):
        # --- ноги
        for sg in (-1, 1):
            if walk is not None:
                a = math.sin(walk + (0 if sg < 0 else math.pi)) * 0.45
            else:
                a = sg * 0.10
            fx = sg * 11 + math.sin(a) * leg_l * 0.95
            fy = -leg_l + math.cos(a) * leg_l * 0.97
            line(cv, [(sg * 10, -leg_l), (fx, fy), (fx + 12, fy)], lw)

        # --- верх тела (вокруг таза)
        with group(cv, hip[0], hip[1], rot=lean):
            ty = sh_y - hip[1]  # плечи в локальных координатах верхней части
            # руки
            for sg, tgt, name in ((-1, hand_l, "hand_l"), (1, hand_r, "hand_r")):
                sx0, sy0 = sg * 24, ty + 8
                if tgt is not None:
                    lx, ly = (tgt[0] * sgn_f) / s, tgt[1] / (s * squash)
                    # из координат «от ступней» в локальные верхней части: сместить на таз и обратно довернуть
                    px, py = lx - hip[0], ly - hip[1]
                    r = math.radians(-lean)
                    gx = px * math.cos(r) - py * math.sin(r)
                    gy = px * math.sin(r) + py * math.cos(r)
                    joint, end = ik2((sx0, sy0), (gx, gy), 50, 52, bend=-sg * sgn_f * -1 if False else (1 if sg > 0 else -1))
                elif walk is not None:
                    sw = math.sin(walk + (math.pi if sg < 0 else 0)) * 0.5
                    end = (sx0 + math.sin(sw) * 100 * 0.9, sy0 + math.cos(sw) * 100 * 0.9)
                    joint = ((sx0 + end[0]) / 2 + sg * 5, (sy0 + end[1]) / 2 + 6)
                else:
                    end = (sx0 + sg * 40, sy0 + 55)
                    joint = ((sx0 + end[0]) / 2 + sg * 5, (sy0 + end[1]) / 2 + 6)
                line(cv, [(sx0, sy0), joint, end], lw)
                # мировые координаты кисти
                r2 = math.radians(lean)
                hx = end[0] * math.cos(r2) - end[1] * math.sin(r2) + hip[0]
                hy = end[0] * math.sin(r2) + end[1] * math.cos(r2) + hip[1]
                out[name] = to_world(hx, hy)
            # тело
            rrect(cv, -26, ty, 26, 4, 20, shirt, 5.5)
            # голова
            hcx, hcy = 0.0, ty - hr * 1.15
            with group(cv, hcx, hcy + hr * 0.9, rot=tilt):
                cy = -hr * 0.9
                if hair:
                    for k in range(-2, 3):
                        line(cv, [(k * 8, cy - hr + 1), (k * 11, cy - hr - 12)], 4.5, hair)
                ell(cv, 0, cy, hr, hr, WHITE, 5.5)
                eg, er = hr * 0.38, hr * 0.13
                eyes(cv, 0, cy - hr * 0.12, eg, er, look, blink_k, mood)
                brows(cv, 0, cy - hr * 0.12, eg, er, mood, brow_raise)
                mouth(cv, 0, cy + hr * 0.32, hr * 0.42, mood, talk_k)
            r3 = math.radians(lean)
            ex_, ey_ = hcx, hcy
            out["head"] = to_world(ex_ * math.cos(r3) - ey_ * math.sin(r3) + hip[0],
                                   ex_ * math.sin(r3) + ey_ * math.cos(r3) + hip[1])
    return out


# ============================================================
# Зверёк
# ============================================================

def critter(cv: Canvas, x: float, y: float, r: float = 60, col=PAL["orange"], belly=None,
            mood: str = "smile", look=(0, 0), blink_k: float = 1.0, talk_k: float = 0.0,
            ears: str = "round", tail: str = "none", feet: bool = True, cheeks: bool = False,
            whiskers: bool = False, nose=PAL["pink"], tilt: float = 0.0, squash: float = 1.0,
            flip: bool = False, bob_k: float = 0.0) -> dict:
    """
    Универсальный зверёк-«картошка». (x, y) — центр тела.
      ears: round (медведь/мышь), pointy (кот/лиса), long (кролик), none
      tail: none / curl / fluffy / thin
    Меняя col, ears, tail, belly и щёки, получаешь кота, лису, медведя, зайца, мышь, ёжика...
    """
    with group(cv, x, y - bob_k, rot=tilt, sy=squash, sx=1.0, flip=flip):
        # хвост
        if tail == "fluffy":
            ell(cv, r * 1.05, r * 0.2, r * 0.42, r * 0.62, col, 5)
        elif tail == "curl":
            tube(cv, [(r * 0.8, r * 0.5), (r * 1.3, r * 0.3), (r * 1.4, -r * 0.2), (r * 1.1, -r * 0.45)],
                 r * 0.16, col, ow=4)
        elif tail == "thin":
            line(cv, [(r * 0.85, r * 0.55), (r * 1.4, r * 0.7), (r * 1.7, r * 0.3)], 5)
        # уши
        if ears == "round":
            for sg in (-1, 1):
                ell(cv, sg * r * 0.62, -r * 0.82, r * 0.26, fill=col, w=5.5)
                ell(cv, sg * r * 0.62, -r * 0.82, r * 0.13, fill=PAL["pink"], w=0)
        elif ears == "pointy":
            for sg in (-1, 1):
                poly(cv, [(sg * r * 0.25, -r * 0.8), (sg * r * 0.62, -r * 1.35), (sg * r * 0.85, -r * 0.55)], col, 5.5)
                poly(cv, [(sg * r * 0.42, -r * 0.82), (sg * r * 0.62, -r * 1.1), (sg * r * 0.72, -r * 0.68)],
                     PAL["pink"], 0)
        elif ears == "long":
            for sg in (-1, 1):
                ell(cv, sg * r * 0.35, -r * 1.35, r * 0.2, r * 0.62, col, 5.5)
                ell(cv, sg * r * 0.35, -r * 1.35, r * 0.09, r * 0.45, PAL["pink"], 0)
        # ножки
        if feet:
            for sg in (-1, 1):
                ell(cv, sg * r * 0.45, r * 0.88, r * 0.3, r * 0.2, col, 5.5)
        # тело
        ell(cv, 0, 0, r, r * 0.92, col, 6)
        if belly:
            ell(cv, 0, r * 0.28, r * 0.62, r * 0.55, belly, 0)
        # лицо
        er = r * 0.095
        eyes(cv, 0, -r * 0.12, r * 0.36, er, look, blink_k, mood, lw=max(3.0, r * 0.06))
        brows(cv, 0, -r * 0.12, r * 0.36, er, mood)
        ell(cv, 0, r * 0.1, r * 0.1, r * 0.075, nose, 3.5)
        mouth(cv, 0, r * 0.2, r * 0.28, mood, talk_k, lw=max(3.0, r * 0.055))
        if cheeks:
            for sg in (-1, 1):
                ell(cv, sg * r * 0.62, r * 0.18, r * 0.13, r * 0.09, (250, 150, 160), 0)
        if whiskers:
            for sg in (-1, 1):
                for dy in (-0.02, 0.1):
                    line(cv, [(sg * r * 0.3, r * (0.15 + dy)), (sg * r * 0.95, r * (0.08 + dy * 2))], 3)
    return {"top": (x, y - r), "center": (x, y)}
