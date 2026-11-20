#!/usr/bin/env python3
"""
uTeam-Studio — build.py

Управление каналами и сборка роликов.
Запуск без аргументов → интерактивное меню.

QoL:
  • тихий рендер (без спама moviepy)
  • статус эпизодов (S/V/B/M)
  • open / info / clean / doctor
  • last — последний эпизод
  • batch render
  • проверка зависимостей
"""

import os
import sys
from pathlib import Path
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


# Repo root (parent of YouTube/) so `import core` works after core/ moved to root
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
YT_ROOT = Path(__file__).resolve().parent
if str(YT_ROOT) not in sys.path:
    sys.path.insert(0, str(YT_ROOT))
import shutil
import argparse
import importlib.util
import traceback
import platform
import subprocess
from datetime import datetime

ROOT = Path(__file__).resolve().parent
CHANNELS = ROOT / "channels"
LAST_FILE = ROOT / ".last_episode"


# ============================================================
# Output helpers
# ============================================================


def _safe_print(*args, **kwargs):
    """Print that never crashes on Windows legacy code pages."""
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        text = " ".join(str(a) for a in args)
        enc = getattr(sys.stdout, "encoding", None) or "utf-8"
        sys.stdout.buffer.write((text + "\n").encode(enc, errors="replace"))

class StudioError(Exception):
    def __init__(self, message: str, hint: str = None):
        self.message = message
        self.hint = hint
        super().__init__(message)

    def __str__(self):
        s = f"[ERR] {self.message}"
        if self.hint:
            s += f"\n       -> {self.hint}"
        return s


def err(msg: str, hint: str = None):
    print(f"[ERR] {msg}")
    if hint:
        print(f"      -> {hint}")


def ok(msg: str):
    print(f"[OK]  {msg}")


def warn(msg: str):
    print(f"[!]   {msg}")


def info(msg: str):
    print(f"      {msg}")


# ============================================================
# Channel / episode helpers
# ============================================================

def list_channels(silent=False):
    if not CHANNELS.exists():
        if not silent:
            _safe_print("Нет каналов.")
        return []
    chans = sorted([p.name for p in CHANNELS.iterdir() if p.is_dir()])
    if not silent:
        if not chans:
            _safe_print("Нет каналов.")
        else:
            _safe_print("Каналы:")
            for i, name in enumerate(chans, 1):
                shorts = list((CHANNELS / name / "videos" / "shorts").glob("*")) if (CHANNELS / name / "videos" / "shorts").exists() else []
                longs = list((CHANNELS / name / "videos" / "longs").glob("*")) if (CHANNELS / name / "videos" / "longs").exists() else []
                print(f"  {i}. {name}  (shorts: {len(shorts)}, longs: {len(longs)})")
    return chans


def pick_channel():
    chans = list_channels()
    if not chans:
        return None
    if len(chans) == 1:
        _safe_print(f"Канал: {chans[0]}")
        return chans[0]
    raw = input("Номер или имя канала: ").strip()
    if raw.isdigit():
        idx = int(raw) - 1
        if 0 <= idx < len(chans):
            return chans[idx]
    if raw in chans:
        return raw
    err("Канал не найден.")
    return None


def list_episodes(channel: str, kind: str = None):
    base = CHANNELS / channel / "videos"
    result = []
    kinds = [kind] if kind else ["shorts", "longs"]
    for k in kinds:
        folder = base / k
        if not folder.exists():
            continue
        for p in sorted(folder.iterdir()):
            if p.is_dir():
                result.append((k, p))
    return result


def episode_status(ep_path: Path) -> dict:
    return {
        "scenes": (ep_path / "scenes.py").exists(),
        "script": (ep_path / "script.txt").exists(),
        "voice": (ep_path / "voiceover.mp3").exists(),
        "build": (ep_path / "build").exists() and any((ep_path / "build").glob("*.mp4")),
        "source": (ep_path / "source").exists(),
        "meta": (ep_path / "build" / "youtube_metadata.txt").exists() if (ep_path / "build").exists() else False,
        "sheet": (ep_path / "build" / "contact_sheet.png").exists() if (ep_path / "build").exists() else False,
    }


def status_icons(st: dict) -> str:
    return (
        ("S" if st["scenes"] else ".") +
        ("V" if st["voice"] else ".") +
        ("B" if st["build"] else ".") +
        ("M" if st["meta"] else ".")
    )


def pick_episode(channel: str):
    eps = list_episodes(channel)
    if not eps:
        _safe_print("Нет эпизодов.")
        return None
    _safe_print("Эпизоды:  (S=scenes  V=voice  B=build  M=meta)")
    for i, (k, p) in enumerate(eps, 1):
        st = episode_status(p)
        print(f"  {i}. [{k}] [{status_icons(st)}] {p.name}")
    raw = input("Номер эпизода: ").strip()
    if raw.isdigit():
        idx = int(raw) - 1
        if 0 <= idx < len(eps):
            return eps[idx][1]
    err("Эпизод не найден.")
    return None


def save_last(ep_path: Path):
    try:
        LAST_FILE.write_text(str(ep_path.resolve()), encoding="utf-8")
    except Exception:
        pass


def load_last() -> Path | None:
    if not LAST_FILE.exists():
        return None
    try:
        p = Path(LAST_FILE.read_text(encoding="utf-8").strip())
        return p if p.exists() else None
    except Exception:
        return None


def create_channel(name: str):
    name = name.strip().lower().replace(" ", "_")
    path = CHANNELS / name
    if path.exists():
        err(f"Канал уже существует: {name}")
        return
    (path / "videos" / "shorts").mkdir(parents=True, exist_ok=True)
    (path / "videos" / "longs").mkdir(parents=True, exist_ok=True)
    ok(f"Канал создан: {path}")


def delete_channel(name: str):
    path = CHANNELS / name
    if not path.exists():
        err(f"Канал не найден: {name}")
        return
    confirm = input(f"Удалить канал '{name}' со всеми видео? [y/N]: ").strip().lower()
    if confirm == "y":
        shutil.rmtree(path)
        ok(f"Канал удалён: {name}")
    else:
        _safe_print("Отменено.")


def delete_episode(ep_path: Path):
    if not ep_path.exists():
        err("Эпизод не найден.")
        return
    confirm = input(f"Удалить эпизод '{ep_path.name}'? [y/N]: ").strip().lower()
    if confirm == "y":
        shutil.rmtree(ep_path)
        ok(f"Эпизод удалён: {ep_path.name}")
    else:
        _safe_print("Отменено.")


def next_index(folder: Path) -> int:
    existing = [p.name for p in folder.iterdir() if p.is_dir()]
    nums = []
    for name in existing:
        try:
            nums.append(int(name.split("_")[0]))
        except Exception:
            pass
    return max(nums, default=0) + 1


def create_episode(channel: str, kind: str, short_name: str):
    kind = kind.lower()
    if kind in ("long", "longs"):
        kind = "longs"
    elif kind in ("short", "shorts"):
        kind = "shorts"
    else:
        err("Тип: shorts или long")
        return None

    ch_path = CHANNELS / channel
    if not ch_path.exists():
        err(f"Канал не найден: {channel}")
        return None

    folder = ch_path / "videos" / kind
    folder.mkdir(parents=True, exist_ok=True)

    idx = next_index(folder)
    date = datetime.now().strftime("%Y-%m-%d")
    time = datetime.now().strftime("%H%M")
    safe = short_name.strip().lower().replace(" ", "_")
    ep_name = f"{idx:03d}_{safe}_{date}_{time}"
    ep_path = folder / ep_name
    ep_path.mkdir(parents=True, exist_ok=True)
    mode = "shorts" if kind == "shorts" else "long"
    (ep_path / "script.txt").write_text("# Текст озвучки\n\n", encoding="utf-8")

    scenes_template = f'''"""
Episode: {ep_name}
Channel: {channel}
"""

from core.toolkit import *

MODE = "{mode}"
CHANNEL_NAME = "{channel}"

TEXTS = [
    "First sentence goes here.",
    "Second sentence goes here.",
]

CHAPTERS = [
    "Hook",
    "Main point",
]

TITLE = "Your Title Here"
DESC = """Description.

SOURCES
- ...
"""
TAGS = "tag1, tag2"

def s01(cv, t, T):
    title(cv, t, "Title", 56, 140)

def s02(cv, t, T):
    title(cv, t, "Second scene", 52, 140)

TRANSITIONS = {{}}   # например {{1: "iris", 2: "zoom:0.5"}}

_FN = {{"s01": s01, "s02": s02}}
_BG = {{"s01": (255, 248, 225), "s02": (232, 240, 255)}}
ORDER = ["s01", "s02"]
SCENES = [(_BG[k], _FN[k]) for k in ORDER]
'''
    (ep_path / "scenes.py").write_text(scenes_template, encoding="utf-8")
    ok(f"Эпизод создан: {ep_path}")
    save_last(ep_path)
    return ep_path


# ============================================================
# File QoL
# ============================================================

def reveal_in_explorer(path: Path):
    path = path.resolve()
    if not path.exists():
        err(f"Путь не существует: {path}")
        return
    system = platform.system()
    try:
        if system == "Windows":
            if path.is_file():
                subprocess.run(["explorer", "/select,", str(path)], check=False)
            else:
                subprocess.run(["explorer", str(path)], check=False)
        elif system == "Darwin":
            subprocess.run(["open", "-R" if path.is_file() else str(path), str(path)], check=False)
        else:
            folder = path if path.is_dir() else path.parent
            subprocess.run(["xdg-open", str(folder)], check=False)
        ok(f"Открыто: {path}")
    except Exception as e:
        err(f"Не удалось открыть проводник: {e}")


def open_in_editor(path: Path):
    """Открыть файл в редакторе по умолчанию / $EDITOR."""
    path = path.resolve()
    if not path.exists():
        err(f"Файл не найден: {path}")
        return
    editor = os.environ.get("EDITOR") or os.environ.get("VISUAL")
    system = platform.system()
    try:
        if editor:
            subprocess.Popen([editor, str(path)])
        elif system == "Windows":
            os.startfile(str(path))  # type: ignore
        elif system == "Darwin":
            subprocess.Popen(["open", str(path)])
        else:
            subprocess.Popen(["xdg-open", str(path)])
        ok(f"Редактор: {path.name}")
    except Exception as e:
        err(f"Не удалось открыть редактор: {e}")


def show_episode_info(ep_path: Path):
    if not ep_path or not ep_path.exists():
        err("Эпизод не найден.")
        return
    st = episode_status(ep_path)
    print()
    print(f"=== {ep_path.name} ===")
    _safe_print(f"Путь:      {ep_path}")
    print(f"scenes.py: {'yes' if st['scenes'] else 'NO'}")
    print(f"script.txt:{'yes' if st['script'] else 'NO'}")
    _safe_print(f"voiceover: {'yes' if st['voice'] else 'NO  <- озвучь script.txt'}")
    print(f"build mp4: {'yes' if st['build'] else 'NO'}")
    print(f"meta:      {'yes' if st['meta'] else 'NO'}")
    print(f"sheet:     {'yes' if st['sheet'] else 'NO'}")
    if st["scenes"]:
        try:
            ep = load_module(str(ep_path / "scenes.py"))
            print(f"MODE:      {getattr(ep, 'MODE', '?')}")
            print(f"TITLE:     {getattr(ep, 'TITLE', '?')}")
            _safe_print(f"Сцен:      {len(getattr(ep, 'SCENES', []))}")
            _safe_print(f"Текстов:   {len(getattr(ep, 'TEXTS', []))}")
        except Exception as e:
            warn(f"Не удалось прочитать scenes.py: {e}")
    print()


def clean_episode(ep_path: Path, keep_build: bool = False):
    """Удалить source/ и опционально build/."""
    if not ep_path or not ep_path.exists():
        err("Эпизод не найден.")
        return
    removed = []
    src = ep_path / "source"
    if src.exists():
        shutil.rmtree(src)
        removed.append("source/")
    if not keep_build:
        bld = ep_path / "build"
        if bld.exists():
            shutil.rmtree(bld)
            removed.append("build/")
    pyc = ep_path / "__pycache__"
    if pyc.exists():
        shutil.rmtree(pyc)
        removed.append("__pycache__/")
    if removed:
        ok(f"Очищено: {', '.join(removed)}")
    else:
        _safe_print("Нечего чистить.")


def doctor():
    """Проверка окружения."""
    print("=== doctor ===")
    issues = 0

    # python
    print(f"Python:  {sys.version.split()[0]}")

    # moviepy
    try:
        import moviepy
        ver = getattr(moviepy, "__version__", "?")
        ok(f"moviepy {ver}")
    except ImportError:
        err("moviepy не установлен", "pip install moviepy")
        issues += 1

    # PIL
    try:
        from PIL import Image
        ok("Pillow OK")
    except ImportError:
        err("Pillow не установлен", "pip install pillow")
        issues += 1

    # numpy
    try:
        import numpy
        ok(f"numpy {numpy.__version__}")
    except ImportError:
        err("numpy не установлен", "pip install numpy")
        issues += 1

    # ffmpeg
    ff = shutil.which("ffmpeg")
    if ff:
        ok(f"ffmpeg: {ff}")
    else:
        try:
            import imageio_ffmpeg
            exe = imageio_ffmpeg.get_ffmpeg_exe()
            ok(f"ffmpeg (imageio): {exe}")
        except Exception:
            err("ffmpeg не найден", "Установи ffmpeg или: pip install imageio-ffmpeg")
            issues += 1

    # core
    try:
        from core.config import get_format
        from core.toolkit import title
        ok("core modules OK")
    except Exception as e:
        err(f"core: {e}", "Запускай из папки YouTube/")
        issues += 1

    # channels
    if CHANNELS.exists():
        n = len(list_channels(silent=True))
        ok(f"channels/: {n} канал(ов)")
    else:
        warn("channels/ ещё нет — создай канал")

    print()
    if issues == 0:
        ok("Всё готово к работе")
    else:
        warn(f"Проблем: {issues}")
    return issues == 0


# ============================================================
# Render
# ============================================================

def load_module(path: str, name: str = "episode"):
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        if spec is None or spec.loader is None:
            raise StudioError(f"Не удалось загрузить: {path}")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    except SyntaxError as e:
        raise StudioError(
            f"Синтаксическая ошибка в {Path(path).name}",
            f"Строка {e.lineno}: {e.msg}"
        ) from e
    except Exception as e:
        raise StudioError(
            f"Ошибка загрузки {Path(path).name}: {type(e).__name__}: {e}"
        ) from e


def render(ep_dir, preview: bool = False, channel_override: str = None, quiet: bool = True, verbose: bool = False):
    ep_dir = Path(ep_dir).resolve()
    if not ep_dir.is_dir():
        err(f"Папка не найдена: {ep_dir}")
        return False

    scenes_path = ep_dir / "scenes.py"
    voice_path = ep_dir / "voiceover.mp3"

    if not scenes_path.exists():
        err(f"scenes.py не найден в {ep_dir.name}", "Создай эпизод заново")
        return False
    if not voice_path.exists():
        err(
            f"voiceover.mp3 не найден в {ep_dir.name}",
            "Озвучь script.txt → voiceover.mp3"
        )
        return False

    import sys as _sys
    _old_bc = _sys.dont_write_bytecode
    _sys.dont_write_bytecode = True
    try:
        ep = load_module(str(scenes_path))
    except StudioError as e:
        print(e)
        return False
    except Exception as e:
        err(f"Не удалось загрузить scenes.py: {e}")
        if verbose:
            traceback.print_exc()
        return False
    finally:
        _sys.dont_write_bytecode = _old_bc

    pyc = ep_dir / "__pycache__"
    if pyc.exists():
        shutil.rmtree(pyc, ignore_errors=True)

    mode = getattr(ep, "MODE", "shorts").lower()
    channel = channel_override or getattr(ep, "CHANNEL_NAME", "uTeam")
    texts = getattr(ep, "TEXTS", None)
    chapters = getattr(ep, "CHAPTERS", [])

    if not hasattr(ep, "SCENES") or texts is None:
        err("scenes.py должен определять TEXTS и SCENES")
        return False

    scenes = ep.SCENES

    try:
        from core.config import get_format
        from core.audio_sync import prepare_voice
        from core.validator import validate_scenes, ValidationError
        from core.renderer import render_episode, RenderError
    except ImportError as e:
        err(f"Не удалось импортировать core: {e}", "Запускай из папки YouTube/")
        return False

    try:
        cfg = get_format(mode, preview=preview)
    except ValueError as e:
        err(str(e))
        return False

    print("=" * 50)
    print(f"  uTeam-Studio  |  {cfg.name}  {cfg.out_width}x{cfg.out_height} @{cfg.fps}fps")
    print(f"  preview={preview}  channel={channel}")
    _safe_print(f"  эпизод: {ep_dir.name}")
    print("=" * 50)

    source_dir = ep_dir / "source"
    build_dir = ep_dir / "build"
    source_dir.mkdir(exist_ok=True)
    build_dir.mkdir(exist_ok=True)

    try:
        _safe_print("[1/4] Подготовка голоса...")
        sync = prepare_voice(str(voice_path), texts, cfg, work_dir=str(source_dir))
    except Exception as e:
        err(f"Ошибка подготовки голоса: {type(e).__name__}: {e}", "Проверь voiceover.mp3 и TEXTS")
        if verbose:
            traceback.print_exc()
        return False

    _safe_print("[1b] Валидация...")
    try:
        validate_scenes(scenes, texts, cfg, sync.starts, sync.durs, sync.total, mode=mode)
    except ValidationError as e:
        err("Валидация не пройдена")
        print(e)
        return False
    except Exception as e:
        err(f"Ошибка валидатора: {e}")
        if verbose:
            traceback.print_exc()
        return False

    meta_path = build_dir / "youtube_metadata.txt"
    try:
        write_metadata(str(meta_path), ep, sync.starts, chapters)
    except Exception as e:
        warn(f"Метаданные: {e}")

    out_path = build_dir / f"final_{ep_dir.name}.mp4"
    try:
        render_episode(
            scenes, sync, cfg, str(out_path),
            channel_name=channel,
            work_dir=str(source_dir),
            transitions=getattr(ep, "TRANSITIONS", None),
            quiet=quiet and not verbose,
        )
    except Exception as e:
        # RenderError or anything else
        err(f"Ошибка рендера: {type(e).__name__}: {e}")
        if verbose:
            traceback.print_exc()
        return False

    save_last(ep_dir)
    print()
    print("=" * 50)
    print(f"  DONE")
    _safe_print(f"  Видео:   {out_path}")
    print(f"  Meta:    {meta_path}")
    _safe_print(f"  Длит.:   {sync.total:.1f}s")
    print("=" * 50)
    return True


def sheet(ep_dir, cols: int = 6):
    ep_dir = Path(ep_dir).resolve()
    scenes_path, voice_path = ep_dir / "scenes.py", ep_dir / "voiceover.mp3"
    if not scenes_path.exists() or not voice_path.exists():
        err("Нужны scenes.py и voiceover.mp3", f"Папка: {ep_dir}")
        return
    import sys as _sys
    _old = _sys.dont_write_bytecode
    _sys.dont_write_bytecode = True
    try:
        ep = load_module(str(scenes_path))
    except StudioError as e:
        print(e)
        return
    finally:
        _sys.dont_write_bytecode = _old

    try:
        from core.config import get_format
        from core.audio_sync import prepare_voice
        from core.preview import contact_sheet
        mode = getattr(ep, "MODE", "shorts").lower()
        cfg = get_format(mode, preview=True)
        source_dir = ep_dir / "source"
        source_dir.mkdir(exist_ok=True)
        sync = prepare_voice(str(voice_path), ep.TEXTS, cfg, work_dir=str(source_dir))
        out = ep_dir / "build"
        out.mkdir(exist_ok=True)
        path = contact_sheet(ep.SCENES, sync.T, cfg, str(out / "contact_sheet.png"), cols=cols)
        ok(f"Контактный лист: {path}")
        save_last(ep_dir)
    except Exception as e:
        err(f"Contact sheet: {e}")
        traceback.print_exc()


def write_metadata(path: str, ep, starts: list, chapters: list):
    title = getattr(ep, "TITLE", "Untitled")
    desc = getattr(ep, "DESC", "")
    tags = getattr(ep, "TAGS", "")

    def fmt(sec):
        return f"{int(sec // 60)}:{int(sec % 60):02d}"

    ch_lines = "\n".join(f"{fmt(s)} {n}" for s, n in zip(starts, chapters)) if chapters else ""
    body = (
        f"TITLE\n{title}\n\n"
        f"DESCRIPTION\n{desc.format(chapters=ch_lines) if '{chapters}' in str(desc) else desc}\n\n"
        f"TAGS\n{tags}\n"
    )
    with open(path, "w", encoding="utf-8") as f:
        f.write(body)
    print(f"[meta] {path}")


def resolve_episode_path(raw: str) -> Path | None:
    """Найти эпизод по пути или имени."""
    p = Path(raw)
    if p.is_dir() and (p / "scenes.py").exists():
        return p.resolve()
    # поиск по имени
    if CHANNELS.exists():
        hits = list(CHANNELS.rglob(raw))
        hits = [h for h in hits if h.is_dir() and (h / "scenes.py").exists()]
        if len(hits) == 1:
            return hits[0]
        if len(hits) > 1:
            err(f"Несколько совпадений для '{raw}':")
            for h in hits:
                info(str(h))
            return None
    if p.exists():
        return p.resolve()
    return None


# ============================================================
# Interactive menu
# ============================================================

def interactive():
    while True:
        last = load_last()
        print("\n=== uTeam-Studio ===")
        if last:
            print(f"  last: {last.name}")
        _safe_print("1. Список каналов")
        _safe_print("2. Создать канал")
        _safe_print("3. Удалить канал")
        _safe_print("4. Создать эпизод")
        _safe_print("5. Удалить эпизод")
        _safe_print("6. Рендер")
        print("7. Contact sheet")
        _safe_print("8. Инфо об эпизоде")
        _safe_print("9. Открыть папку эпизода")
        _safe_print("10. Открыть scenes.py в редакторе")
        _safe_print("11. Очистить source/build")
        _safe_print("12. Рендер последнего (last)")
        _safe_print("13. doctor (проверка окружения)")
        _safe_print("0. Выход")
        choice = input("> ").strip()

        if choice == "1":
            list_channels()

        elif choice == "2":
            name = input("Имя канала: ").strip()
            if name:
                create_channel(name)

        elif choice == "3":
            ch = pick_channel()
            if ch:
                delete_channel(ch)

        elif choice == "4":
            ch = pick_channel()
            if not ch:
                continue
            kind = input("Тип (shorts / long): ").strip()
            short = input("Короткое имя: ").strip()
            if kind and short:
                create_episode(ch, kind, short)

        elif choice == "5":
            ch = pick_channel()
            if not ch:
                continue
            ep = pick_episode(ch)
            if ep:
                delete_episode(ep)

        elif choice == "6":
            ch = pick_channel()
            if not ch:
                continue
            ep = pick_episode(ch)
            if ep:
                preview = input("Preview? [y/N]: ").strip().lower() == "y"
                render(ep, preview=preview)

        elif choice == "7":
            ch = pick_channel()
            if not ch:
                continue
            ep = pick_episode(ch)
            if ep:
                sheet(ep)

        elif choice == "8":
            ch = pick_channel()
            if not ch:
                continue
            ep = pick_episode(ch)
            if ep:
                show_episode_info(ep)

        elif choice == "9":
            ch = pick_channel()
            if not ch:
                continue
            ep = pick_episode(ch)
            if ep:
                reveal_in_explorer(ep)

        elif choice == "10":
            ch = pick_channel()
            if not ch:
                continue
            ep = pick_episode(ch)
            if ep:
                open_in_editor(ep / "scenes.py")

        elif choice == "11":
            ch = pick_channel()
            if not ch:
                continue
            ep = pick_episode(ch)
            if ep:
                keep = input("Оставить build/? [y/N]: ").strip().lower() == "y"
                clean_episode(ep, keep_build=keep)

        elif choice == "12":
            last = load_last()
            if not last:
                err("Нет последнего эпизода")
                continue
            print(f"Last: {last}")
            preview = input("Preview? [y/N]: ").strip().lower() == "y"
            render(last, preview=preview)

        elif choice == "13":
            doctor()

        elif choice == "0":
            _safe_print("Выход.")
            break

        else:
            _safe_print("Неизвестная команда.")


def main():
    parser = argparse.ArgumentParser(
        description="uTeam-Studio — сборка YouTube-роликов",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  python build.py                          # меню
  python build.py render <path> --preview
  python build.py render last
  python build.py info <path>
  python build.py open <path>
  python build.py edit <path>              # scenes.py
  python build.py clean <path>
  python build.py doctor
  python build.py list
        """,
    )
    parser.add_argument("command", nargs="?", help="render|sheet|info|open|edit|clean|doctor|list|last")
    parser.add_argument("path", nargs="?", help="Путь/имя эпизода или 'last'")
    parser.add_argument("--preview", action="store_true", help="Preview-режим")
    parser.add_argument("--channel", help="Переопределить CHANNEL_NAME")
    parser.add_argument("--verbose", "-v", action="store_true", help="Подробный вывод + traceback")
    parser.add_argument("--no-quiet", action="store_true", help="Показать прогресс moviepy")
    args = parser.parse_args()

    if not args.command:
        interactive()
        return

    cmd = args.command.lower()

    if cmd == "doctor":
        sys.exit(0 if doctor() else 1)

    if cmd == "list":
        list_channels()
        return

    if cmd == "last":
        last = load_last()
        if not last:
            err("Нет последнего эпизода")
            sys.exit(1)
        print(last)
        return

    if cmd in ("render", "sheet", "info", "open", "edit", "clean"):
        raw = args.path
        if not raw:
            err(f"Укажи путь: python build.py {cmd} <path|last>")
            sys.exit(1)

        if raw.lower() == "last":
            ep = load_last()
            if not ep:
                err("Нет последнего эпизода")
                sys.exit(1)
        else:
            ep = resolve_episode_path(raw)
            if not ep:
                err(f"Эпизод не найден: {raw}")
                sys.exit(1)

        if cmd == "render":
            ok_flag = render(
                ep,
                preview=args.preview,
                channel_override=args.channel,
                quiet=not args.no_quiet,
                verbose=args.verbose,
            )
            sys.exit(0 if ok_flag else 1)
        elif cmd == "sheet":
            sheet(ep)
        elif cmd == "info":
            show_episode_info(ep)
        elif cmd == "open":
            reveal_in_explorer(ep)
        elif cmd == "edit":
            open_in_editor(ep / "scenes.py")
        elif cmd == "clean":
            clean_episode(ep, keep_build=False)
        return

    err(f"Неизвестная команда: {args.command}")
    _safe_print("Доступно: render sheet info open edit clean doctor list last")
    sys.exit(1)


if __name__ == "__main__":
    main()
