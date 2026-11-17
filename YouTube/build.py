#!/usr/bin/env python3
"""
uTeam-Studio — build.py

Управление каналами и сборка роликов.
Запуск без аргументов → интерактивное меню.
"""

import os
import sys
import shutil
import argparse
import importlib.util
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CHANNELS = ROOT / "channels"


# ============================================================
# Helpers
# ============================================================

def list_channels(silent=False):
    if not CHANNELS.exists():
        if not silent:
            print("Нет каналов.")
        return []
    chans = sorted([p.name for p in CHANNELS.iterdir() if p.is_dir()])
    if not silent:
        if not chans:
            print("Нет каналов.")
        else:
            print("Каналы:")
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
        print(f"Выбран канал: {chans[0]}")
        return chans[0]
    raw = input("Номер или имя канала: ").strip()
    if raw.isdigit():
        idx = int(raw) - 1
        if 0 <= idx < len(chans):
            return chans[idx]
    if raw in chans:
        return raw
    print("Не найден.")
    return None


def list_episodes(channel: str, kind: str = None):
    """kind = 'shorts' | 'longs' | None (оба)"""
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


def pick_episode(channel: str):
    eps = list_episodes(channel)
    if not eps:
        print("Нет эпизодов.")
        return None
    print("Эпизоды:")
    for i, (k, p) in enumerate(eps, 1):
        print(f"  {i}. [{k}] {p.name}")
    raw = input("Номер эпизода: ").strip()
    if raw.isdigit():
        idx = int(raw) - 1
        if 0 <= idx < len(eps):
            return eps[idx][1]
    print("Не найден.")
    return None


def create_channel(name: str):
    name = name.strip().lower().replace(" ", "_")
    path = CHANNELS / name
    if path.exists():
        print(f"Канал уже существует: {name}")
        return
    (path / "videos" / "shorts").mkdir(parents=True, exist_ok=True)
    (path / "videos" / "longs").mkdir(parents=True, exist_ok=True)
    print(f"✓ Канал создан: {path}")


def delete_channel(name: str):
    path = CHANNELS / name
    if not path.exists():
        print(f"Канал не найден: {name}")
        return
    confirm = input(f"Удалить канал '{name}' вместе со всеми видео? [y/N]: ").strip().lower()
    if confirm == "y":
        shutil.rmtree(path)
        print(f"✓ Канал удалён: {name}")
    else:
        print("Отменено.")


def delete_episode(ep_path: Path):
    if not ep_path.exists():
        print("Эпизод не найден.")
        return
    confirm = input(f"Удалить эпизод '{ep_path.name}'? [y/N]: ").strip().lower()
    if confirm == "y":
        shutil.rmtree(ep_path)
        print(f"✓ Эпизод удалён: {ep_path.name}")
    else:
        print("Отменено.")


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
        print("Тип должен быть: shorts или long")
        return None

    ch_path = CHANNELS / channel
    if not ch_path.exists():
        print(f"Канал не найден: {channel}")
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

from core.primitives import *

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

_FN = {{"s01": s01, "s02": s02}}
_BG = {{"s01": (255, 248, 225), "s02": (232, 240, 255)}}
ORDER = ["s01", "s02"]
SCENES = [(_BG[k], _FN[k]) for k in ORDER]
'''
    (ep_path / "scenes.py").write_text(scenes_template, encoding="utf-8")
    print(f"✓ Эпизод создан: {ep_path}")
    return ep_path


# ============================================================
# Render
# ============================================================

def load_module(path: str, name: str = "episode"):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def render(ep_dir, preview: bool = False, channel_override: str = None):
    ep_dir = Path(ep_dir).resolve()
    if not ep_dir.is_dir():
        print(f"ERROR: folder not found: {ep_dir}")
        return

    scenes_path = ep_dir / "scenes.py"
    voice_path = ep_dir / "voiceover.mp3"

    if not scenes_path.exists():
        print(f"ERROR: scenes.py not found")
        return
    if not voice_path.exists():
        print(f"ERROR: voiceover.mp3 not found")
        print("→ Озвучь script.txt в ElevenLabs → voiceover.mp3")
        return

    # не оставлять __pycache__ в папке эпизода
    import sys as _sys
    _old_bc = _sys.dont_write_bytecode
    _sys.dont_write_bytecode = True
    try:
        ep = load_module(str(scenes_path))
    finally:
        _sys.dont_write_bytecode = _old_bc
    pyc = ep_dir / "__pycache__"
    if pyc.exists():
        import shutil as _sh
        _sh.rmtree(pyc, ignore_errors=True)

    mode = getattr(ep, "MODE", "shorts").lower()
    channel = channel_override or getattr(ep, "CHANNEL_NAME", "uTeam")
    texts = getattr(ep, "TEXTS", None)
    chapters = getattr(ep, "CHAPTERS", [])

    if not hasattr(ep, "SCENES") or texts is None:
        print("ERROR: scenes.py must define TEXTS and SCENES")
        return

    scenes = ep.SCENES

    from core.config import get_format
    from core.audio_sync import prepare_voice
    from core.validator import validate_scenes, ValidationError
    from core.renderer import render_episode

    cfg = get_format(mode, preview=preview)
    print("=" * 50)
    print(f"  uTeam-Studio  |  {cfg.name}  {cfg.out_width}x{cfg.out_height} @{cfg.fps}fps")
    print(f"  preview={preview}  channel={channel}")
    print("=" * 50)

    # source/ — промежуточный мусор; build/ — финальные файлы
    source_dir = ep_dir / "source"
    build_dir = ep_dir / "build"
    source_dir.mkdir(exist_ok=True)
    build_dir.mkdir(exist_ok=True)

    sync = prepare_voice(str(voice_path), texts, cfg, work_dir=str(source_dir))

    print("[1b/4] Проверка ОТК (safe-zone, хронометраж)...")
    try:
        validate_scenes(scenes, texts, cfg, sync.starts, sync.durs, sync.total, mode=mode)
    except ValidationError as e:
        print(e)
        return

    meta_path = build_dir / "youtube_metadata.txt"
    write_metadata(str(meta_path), ep, sync.starts, chapters)

    out_path = build_dir / f"final_{ep_dir.name}.mp4"
    render_episode(scenes, sync, cfg, str(out_path), channel_name=channel, work_dir=str(source_dir))
    print()
    print("=" * 50)
    print(f"  ✓ Готово")
    print(f"  Видео:      {out_path}")
    print(f"  Метаданные: {meta_path}")
    print(f"  Длительность: {sync.total:.1f}s")
    print(f"  source/:    {source_dir}")
    print("=" * 50)


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


# ============================================================
# Interactive menu
# ============================================================

def interactive():
    while True:
        print("\n=== uTeam-Studio ===")
        print("1. Список каналов")
        print("2. Создать канал")
        print("3. Удалить канал")
        print("4. Создать эпизод")
        print("5. Удалить эпизод")
        print("6. Собрать ролик (render)")
        print("0. Выход")
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
            short = input("Короткое имя (например tickle): ").strip()
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
            if not ep:
                continue
            prev = input("Preview? [y/N]: ").strip().lower() == "y"
            render(ep, preview=prev)

        elif choice == "0":
            break
        else:
            print("Неизвестный выбор")


# ============================================================
# CLI
# ============================================================

def main():
    sys.path.insert(0, str(ROOT))

    parser = argparse.ArgumentParser(description="uTeam-Studio")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("list", help="Список каналов")

    p_create = sub.add_parser("create", help="Создать канал")
    p_create.add_argument("name")

    p_del = sub.add_parser("delete", help="Удалить канал")
    p_del.add_argument("name")

    p_new = sub.add_parser("new", help="Создать эпизод")
    p_new.add_argument("channel")
    p_new.add_argument("kind", choices=["shorts", "long", "longs", "short"])
    p_new.add_argument("short_name")

    p_render = sub.add_parser("render", help="Собрать ролик")
    p_render.add_argument("path")
    p_render.add_argument("--preview", action="store_true")
    p_render.add_argument("--channel", default=None)

    args = parser.parse_args()

    if args.cmd is None:
        interactive()
    elif args.cmd == "list":
        list_channels()
    elif args.cmd == "create":
        create_channel(args.name)
    elif args.cmd == "delete":
        delete_channel(args.name)
    elif args.cmd == "new":
        create_episode(args.channel, args.kind, args.short_name)
    elif args.cmd == "render":
        render(args.path, preview=args.preview, channel_override=args.channel)


if __name__ == "__main__":
    main()
