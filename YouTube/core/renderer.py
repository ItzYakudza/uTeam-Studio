"""
uTeam-Studio
core/renderer.py — сборка кадров, свайпы, сведение звука, экспорт MP4.

Улучшения:
  • тихий режим (без спама moviepy)
  • понятные ошибки с номером сцены и временем
"""

import os
from typing import List, Optional, Callable

import numpy as np
from PIL import Image

from .config import FormatConfig
from .primitives import Canvas, E
from .audio_sync import SyncResult, make_background_audio
from . import transitions as _tr


class RenderError(Exception):
    """Ошибка рендера с контекстом."""
    def __init__(self, message: str, scene_index: int = None, t: float = None):
        self.scene_index = scene_index
        self.t = t
        parts = [message]
        if scene_index is not None:
            parts.append(f"сцена #{scene_index}")
        if t is not None:
            parts.append(f"t={t:.3f}s")
        super().__init__(" | ".join(parts))


def _silence_moviepy_logs():
    """Глушим болтливые логгеры moviepy / imageio / proglog."""
    import logging
    for name in ("moviepy", "moviepy.video.io.ffmpeg_writer", "moviepy.audio.io.readers",
                 "imageio", "imageio_ffmpeg", "proglog"):
        log = logging.getLogger(name)
        log.setLevel(logging.ERROR)
        log.propagate = False


def render_episode(
    scenes: list,
    sync: SyncResult,
    cfg: FormatConfig,
    out_path: str,
    channel_name: str = "uTeam",
    work_dir: str = ".",
    transitions=None,
    quiet: bool = True,
    progress_cb: Optional[Callable[[str], None]] = None,
) -> str:
    """
    transitions — dict {индекс_сцены: "iris" | "zoom:0.5" | ...} из scenes.py (TRANSITIONS).
    work_dir = папка source/
    quiet=True — без спама moviepy в консоль.
    """
    def log(msg: str):
        if progress_cb:
            progress_cb(msg)
        else:
            print(msg)

    try:
        from moviepy import VideoClip, AudioFileClip, CompositeAudioClip
    except ImportError:
        try:
            from moviepy.editor import VideoClip, AudioFileClip, CompositeAudioClip
        except ImportError as e:
            raise RenderError(
                "Не установлен moviepy. Выполни: pip install moviepy"
            ) from e

    if quiet:
        _silence_moviepy_logs()

    def call(obj, new, old, *args):
        return getattr(obj, new)(*args) if hasattr(obj, new) else getattr(obj, old)(*args)

    trans = dict(transitions or {})
    starts = sync.starts
    durs = sync.durs
    T_list = sync.T
    total = sync.total

    os.makedirs(work_dir, exist_ok=True)

    log("[2/4] Фоновая музыка и SFX...")
    music_path = os.path.join(work_dir, "music_sfx.wav")
    try:
        make_background_audio(music_path, total, starts, T_list)
    except Exception as e:
        raise RenderError(f"Ошибка генерации фонового аудио: {type(e).__name__}: {e}") from e

    def render_frame(i: int, t: float, T: list) -> Image.Image:
        try:
            bg, fn = scenes[i]
            cv = Canvas(cfg, bg)
            T = list(T) + [T[-1]] * max(0, 14 - len(T))
            fn(cv, t, T)
            return cv.final_image()
        except Exception as e:
            raise RenderError(
                f"Ошибка в функции сцены: {type(e).__name__}: {e}",
                scene_index=i,
                t=t,
            ) from e

    def make_frame(Tm: float):
        try:
            i = max(j for j, s in enumerate(starts) if s <= Tm + 1e-6)
        except ValueError:
            i = 0
        t = Tm - starts[i]
        try:
            im = render_frame(i, t, T_list[i])
        except RenderError:
            raise
        except Exception as e:
            raise RenderError(
                f"Ошибка рендера кадра: {type(e).__name__}: {e}",
                scene_index=i,
                t=t,
            ) from e

        if i > 0:
            try:
                tname, tdur = _tr.parse(trans.get(i), cfg.slide)
                if t < tdur:
                    prev = render_frame(i - 1, durs[i - 1] + t, T_list[i - 1])
                    im = _tr.apply(tname, prev, im, t / tdur)
            except Exception as e:
                raise RenderError(
                    f"Ошибка перехода: {type(e).__name__}: {e}",
                    scene_index=i,
                    t=t,
                ) from e

        if cfg.name.startswith("long") and Tm > total - 1.0:
            black = Image.new("RGB", im.size, (0, 0, 0))
            im = Image.blend(im, black, E((Tm - (total - 1.0)) / 1.0))

        return np.array(im)

    log("[3/4] Сведение аудио...")
    try:
        voice = call(AudioFileClip(sync.voice_path_tight), "with_start", "set_start", cfg.lead)
        audio = CompositeAudioClip([AudioFileClip(music_path), voice])
        clip = call(VideoClip(make_frame, duration=total), "with_audio", "set_audio", audio)
    except Exception as e:
        raise RenderError(f"Ошибка сведения аудио: {type(e).__name__}: {e}") from e

    log(f"[4/4] Кодирование {cfg.out_width}x{cfg.out_height} @{cfg.fps}fps, {total:.1f}s...")

    write_kwargs = dict(
        fps=cfg.fps,
        codec="libx264",
        audio_codec="aac",
        audio_bitrate="192k",
        preset="medium",
        ffmpeg_params=["-crf", "17", "-pix_fmt", "yuv420p", "-movflags", "+faststart"],
        logger=None if quiet else "bar",
    )

    try:
        clip.write_videofile(out_path, **write_kwargs)
    except TypeError:
        write_kwargs.pop("logger", None)
        if quiet:
            import contextlib
            import io
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                clip.write_videofile(out_path, **write_kwargs)
        else:
            clip.write_videofile(out_path, **write_kwargs)
    except Exception as e:
        raise RenderError(
            f"Ошибка кодирования MP4: {type(e).__name__}: {e}. "
            "Проверь, что ffmpeg установлен и доступен в PATH."
        ) from e

    log(f"OK saved: {out_path}")
    return out_path
