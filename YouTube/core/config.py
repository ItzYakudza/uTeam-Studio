"""
uTeam-Studio
core/config.py — форматы, safe-zones, цвета.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class FormatConfig:
    name: str
    width: int
    height: int
    fps: int
    out_width: int
    out_height: int
    supersample: int
    lead: float
    tail: float
    slide: float
    min_pause: float
    gap: float
    safe_left: int
    safe_right: int
    safe_top: int
    safe_bottom: int
    center_x: int


SHORTS = FormatConfig(
    name="shorts",
    width=720, height=1280, fps=60,
    out_width=1080, out_height=1920, supersample=2,
    lead=0.30, tail=0.50, slide=0.35,
    min_pause=0.25, gap=0.14,
    safe_left=40, safe_right=610, safe_top=80, safe_bottom=1000, center_x=340,
)

LONG = FormatConfig(
    name="long",
    width=1280, height=720, fps=30,
    out_width=1920, out_height=1080, supersample=2,
    lead=0.50, tail=3.00, slide=0.35,
    min_pause=0.25, gap=0.14,
    safe_left=80, safe_right=1200, safe_top=60, safe_bottom=660, center_x=640,
)


def make_preview(cfg: FormatConfig) -> FormatConfig:
    scale = 0.5
    return FormatConfig(
        name=cfg.name + "_preview",
        width=cfg.width, height=cfg.height,
        fps=30 if cfg.name == "shorts" else 24,
        out_width=int(cfg.out_width * scale),
        out_height=int(cfg.out_height * scale),
        supersample=1,
        lead=cfg.lead, tail=cfg.tail, slide=cfg.slide,
        min_pause=cfg.min_pause, gap=cfg.gap,
        safe_left=cfg.safe_left, safe_right=cfg.safe_right,
        safe_top=cfg.safe_top, safe_bottom=cfg.safe_bottom,
        center_x=cfg.center_x,
    )


def get_format(mode: str, preview: bool = False) -> FormatConfig:
    mode = mode.lower().strip()
    if mode in ("shorts", "short", "vertical"):
        base = SHORTS
    elif mode in ("long", "horizontal", "16:9"):
        base = LONG
    else:
        raise ValueError(f"Unknown mode: {mode}. Use 'shorts' or 'long'.")
    return make_preview(base) if preview else base


INK = (28, 28, 34)
WHITE = (255, 255, 255)
ACCENT_RED = (210, 60, 60)
ACCENT_BLUE = (60, 90, 190)
ACCENT_YELLOW = (250, 200, 40)
ACCENT_GREEN = (60, 150, 80)