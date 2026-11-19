"""
uTeam-Studio
core/toolkit.py — единая точка импорта всего арсенала:

    from core.toolkit import *

Даёт: примитивы (line, poly, ell, rrect, text, person, brain...), камеру (cam, layer, hud, group, clip),
анимацию (tween, keyframes, wiggle...), конструктор (kit), эффекты (fx_*), текст (tx_*), актёров, предметы (prop_*).
"""

from .config import *            # INK, WHITE, ACCENT_*, get_format ...
from .primitives import *        # старое ядро — всё как раньше
from .stage import *
from .anim import *
from .kit import *
from .fx import *
from .textfx import *
from .actor import *
from .props import *
