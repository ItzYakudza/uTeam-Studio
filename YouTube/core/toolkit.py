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

# v2 optional visual/audio systems (additive; legacy exports above remain intact).
from .palettes import PALETTES, get_palette, list_palettes, luminance, contrast_ratio, safe_text_colors
from .typography import TEXT_STYLES, STYLE_FAMILIES, style as text_style, draw_text, draw_split, resolve_style
from .props_100 import PROPS as PROPS_100, PROP_NAMES, draw_prop, draw_props, get_prop as get_prop_100, list_props
from .motion import MOTION_NAMES, EASING_NAMES, ease as motion_ease, apply as motion_apply
from .sfx_gen import SFX_NAMES, SFX_PRESETS, SFX, render_sfx, render_to_file as render_sfx_file, trigger as sfx_trigger, clear_events as clear_sfx_events, render_events as render_sfx_events
from .music_gen import STYLES as MUSIC_STYLES, generate_music, duck_music, write_music
