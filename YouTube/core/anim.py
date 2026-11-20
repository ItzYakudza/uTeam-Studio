"""
uTeam-Studio
core/validator.py — авто-ОТК: safe-zone, хронометраж, хук.
"""

from typing import List
from .config import FormatConfig


class ValidationError(Exception):
    """Критическая ошибка валидации — рендер останавливается."""
    pass


def validate_scenes(
    scenes: list,
    texts: List[str],
    cfg: FormatConfig,
    starts: List[float],
    durs: List[float],
    total: float,
    mode: str = "shorts",
    verbose: bool = False,
) -> None:
    """
    Проверяет сцены до рендера.
    Бросает ValidationError при критических проблемах.
    """
    errors = []
    warnings = []

    if len(scenes) != len(texts):
        errors.append(
            f"Сцен ({len(scenes)}) != TEXTS ({len(texts)}). "
            "Каждая фраза в TEXTS должна иметь свою сцену."
        )

    if mode == "shorts":
        if total < 25:
            warnings.append(f"Shorts короткий: {total:.1f}s (рекомендуется 28–55s)")
        if total > 58:
            errors.append(f"Shorts длинный: {total:.1f}s (макс ≤ 57s)")

    for i, d in enumerate(durs):
        if d > 7.5:
            warnings.append(f"Сцена {i} длинная: {d:.1f}s (лучше < 7.2s)")

    if starts and starts[0] > 0.15:
        warnings.append(f"Первая сцена с {starts[0]:.2f}s — хук может быть слабым")

    # safe-zone только в verbose, чтобы не спамить каждый рендер
    if verbose and mode == "shorts":
        warnings.append(
            f"Safe-zone: x∈[{cfg.safe_left}..{cfg.safe_right}], "
            f"y∈[{cfg.safe_top}..{cfg.safe_bottom}]; "
            f"центр X={cfg.center_x}, блок ≤ {cfg.safe_w():.0f}px"
        )

    for w in warnings:
        print(f"[validator] ! {w}")
    if errors:
        msg = "\n".join(f"  • {e}" for e in errors)
        raise ValidationError(f"Валидация не пройдена:\n{msg}")

    print("[validator] OK")
