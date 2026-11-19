"""
uTeam-Studio
core/preview.py — контактный лист: ключевые кадры всех сцен на одном PNG (секунды вместо минут рендера).
Для каждого предложения сцены берётся кадр в его середине + самый первый кадр сцены (t=0 — хук!).
На Shorts поверх рисуется красная рамка safe-zone.
"""

from typing import List, Sequence

from PIL import Image, ImageDraw, ImageFont

from .config import FormatConfig
from .primitives import Canvas


def _font(size):
    for name in ("arialbd.ttf", "DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            continue
    return ImageFont.load_default()


def contact_sheet(scenes: list, T_list: Sequence[Sequence[float]], cfg: FormatConfig, out_path: str,
                  cols: int = 6, thumb_w: int = 260, safe_zone: bool = True) -> str:
    frames = []
    for i, (bg, fn) in enumerate(scenes):
        T = list(T_list[i])
        Tx = T + [T[-1]] * max(0, 14 - len(T))
        times = [(T[0], "t=0")]
        for k in range(len(T) - 1):
            mid = T[k] + (T[k + 1] - T[k]) * 0.55
            times.append((mid, f"s{k}"))
        for tt, tag in times:
            cv = Canvas(cfg, bg)
            fn(cv, tt, Tx)
            im = cv.final_image().convert("RGB")
            frames.append((i, tag, tt, im))

    th = int(thumb_w * cfg.out_height / cfg.out_width)
    rows = (len(frames) + cols - 1) // cols
    pad, lab = 8, 22
    sheet = Image.new("RGB", (cols * (thumb_w + pad) + pad, rows * (th + lab + pad) + pad), (30, 30, 34))
    d = ImageDraw.Draw(sheet)
    f = _font(15)
    sx, sy = thumb_w / cfg.width, th / cfg.height
    for n, (i, tag, tt, im) in enumerate(frames):
        r, c = divmod(n, cols)
        x, y = pad + c * (thumb_w + pad), pad + r * (th + lab + pad)
        sheet.paste(im.resize((thumb_w, th), Image.LANCZOS), (x, y + lab))
        d.text((x + 2, y + 2), f"scene {i}  {tag}  {tt:.1f}s", font=f, fill=(235, 235, 235))
        if safe_zone and cfg.name.startswith("shorts"):
            # центр композиции (бирюзовый) и геометрический центр кадра (серый) — для контроля симметрии
            d.line([x + cfg.center_x * sx, y + lab, x + cfg.center_x * sx, y + lab + th], fill=(60, 200, 255), width=1)
            d.line([x + cfg.screen_cx * sx, y + lab, x + cfg.screen_cx * sx, y + lab + th], fill=(140, 140, 140), width=1)
            d.rectangle([x + cfg.safe_left * sx, y + lab + cfg.safe_top * sy,
                         x + cfg.safe_right * sx, y + lab + cfg.safe_bottom * sy],
                        outline=(255, 70, 70), width=1)
    sheet.save(out_path)
    return out_path


def fake_timeline(n_scenes: int, sentences: int = 3, per_sentence: float = 1.8):
    """Условные T для сцен без озвучки (для показа тулкита). Возвращает T_list."""
    out = []
    for _ in range(n_scenes):
        out.append([i * per_sentence for i in range(sentences + 1)])
    return out
