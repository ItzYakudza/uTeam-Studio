"""
uTeam-Studio
core/renderer.py — сборка кадров, свайпы, сведение звука, экспорт MP4.
"""

import os
from typing import List

import numpy as np
from PIL import Image

from .config import FormatConfig
from .primitives import Canvas, E
from .audio_sync import SyncResult, make_background_audio


def render_episode(
    scenes: list,
    sync: SyncResult,
    cfg: FormatConfig,
    out_path: str,
    channel_name: str = "uTeam",
    work_dir: str = ".",
) -> str:
    """
    work_dir = папка source/ — туда пишутся music_sfx.wav и прочий мусор.
    out_path = финальный mp4 в корне эпизода.
    """
    try:
        from moviepy import VideoClip, AudioFileClip, CompositeAudioClip
    except ImportError:
        from moviepy.editor import VideoClip, AudioFileClip, CompositeAudioClip

    def call(obj, new, old, *args):
        return getattr(obj, new)(*args) if hasattr(obj, new) else getattr(obj, old)(*args)

    starts = sync.starts
    durs = sync.durs
    T_list = sync.T
    total = sync.total

    os.makedirs(work_dir, exist_ok=True)

    # --- этап: музыка + SFX ---
    print("[2/4] Генерация фоновой музыки и SFX...")
    music_path = os.path.join(work_dir, "music_sfx.wav")
    make_background_audio(music_path, total, starts, T_list)
    print(f"      → {music_path}")

    def render_frame(i: int, t: float, T: list) -> Image.Image:
        bg, fn = scenes[i]
        cv = Canvas(cfg, bg)
        T = list(T) + [T[-1]] * max(0, 14 - len(T))
        fn(cv, t, T)
        # watermark отключён по запросу
        return cv.final_image()

    def make_frame(Tm: float):
        i = max(j for j, s in enumerate(starts) if s <= Tm + 1e-6)
        t = Tm - starts[i]
        im = render_frame(i, t, T_list[i])

        if i > 0 and t < cfg.slide:
            o = E(t / cfg.slide)
            prev = render_frame(i - 1, durs[i - 1] + t, T_list[i - 1])
            canvas = Image.new("RGB", (cfg.out_width, cfg.out_height))
            dx = int(cfg.out_width * o)
            canvas.paste(prev, (-dx, 0))
            canvas.paste(im, (cfg.out_width - dx, 0))
            im = canvas

        if cfg.name.startswith("long") and Tm > total - 1.0:
            black = Image.new("RGB", im.size, (0, 0, 0))
            im = Image.blend(im, black, E((Tm - (total - 1.0)) / 1.0))

        return np.array(im)

    # --- этап: сведение аудио ---
    print("[3/4] Сведение голоса и музыки...")
    voice = call(AudioFileClip(sync.voice_path_tight), "with_start", "set_start", cfg.lead)
    audio = CompositeAudioClip([AudioFileClip(music_path), voice])

    clip = call(VideoClip(make_frame, duration=total), "with_audio", "set_audio", audio)

    # --- этап: кодирование ---
    print(f"[4/4] Кодирование видео ({cfg.out_width}x{cfg.out_height} @{cfg.fps}fps, {total:.1f}s)...")

    clip.write_videofile(
        out_path,
        fps=cfg.fps,
        codec="libx264",
        audio_codec="aac",
        audio_bitrate="192k",
        preset="medium",
        ffmpeg_params=["-crf", "17", "-pix_fmt", "yuv420p", "-movflags", "+faststart"],
        logger="bar",  # прогресс-бар moviepy
    )
    print(f"[renderer] saved → {out_path}")
    return out_path
