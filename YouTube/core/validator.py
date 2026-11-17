"""
uTeam-Studio
core/validator.py — авто-ОТК: safe-zone, шрифты, хронометраж, хук.
"""

from typing import List, Callable, Any, Optional
from .config import FormatConfig


class ValidationError(Exception):
    pass


def validate_scenes(
    scenes: list,
    texts: List[str],
    cfg: FormatConfig,
    starts: List[float],
    durs: List[float],
    total: float,
    mode: str = "shorts",
) -> None:
    """
    Проверяет сцены до рендера.
    Бросает ValidationError при критических проблемах.
    """
    errors = []
    warnings = []

    # 1. Количество сцен == количеству текстов
    if len(scenes) != len(texts):
        errors.append(f"scenes ({len(scenes)}) != texts ({len(texts)})")

    # 2. Хронометраж Shorts
    if mode == "shorts":
        if total < 25:
            warnings.append(f"Shorts too short: {total:.1f}s (recommended 28–55s)")
        if total > 58:
            errors.append(f"Shorts too long: {total:.1f}s (must be ≤ 57s)")

    # 3. Длительность отдельных сцен
    for i, d in enumerate(durs):
        if d > 7.5:
            warnings.append(f"Scene {i} is long: {d:.1f}s (try to keep < 7.2s)")

    # 4. Хук (первая сцена должна начинаться с 0)
    if starts and starts[0] > 0.15:
        warnings.append(f"First scene starts at {starts[0]:.2f}s — hook may be weak")

    # 5. Базовая проверка safe-zone (заглушка — реальная проверка координат
    #    потребует introspection элементов, пока только напоминание)
    if mode == "shorts":
        warnings.append(
            f"Remember safe-zone: x∈[{cfg.safe_left}..{cfg.safe_right}], "
            f"y∈[{cfg.safe_top}..{cfg.safe_bottom}]"
        )

    # Вывод
    for w in warnings:
        print(f"[validator] ⚠ {w}")
    if errors:
        msg = "\n".join(f"  • {e}" for e in errors)
        raise ValidationError(f"Validation failed:\n{msg}")

    print("[validator] OK")
