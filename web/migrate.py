#!/usr/bin/env python3
"""
Миграция старых роликов из YouTube/channels/ в SQLite + storage/

Запуск (из папки web/):
    python migrate.py
    python migrate.py --dry-run
    python migrate.py --force   # перезаписать файлы в storage из channels
"""
from __future__ import annotations

import argparse
import shutil
import sys
from datetime import datetime
from pathlib import Path

WEB_DIR = Path(__file__).resolve().parent
ROOT = WEB_DIR.parent / "YouTube"
if not (ROOT / "build.py").exists():
    # fallback: web is inside YouTube/web
    alt = WEB_DIR.parent
    if (alt / "build.py").exists():
        ROOT = alt

sys.path.insert(0, str(WEB_DIR))
sys.path.insert(0, str(ROOT))

import db as D
import titles as titlelib


def read_title(scenes_path: Path, fallback: str) -> str:
    if not scenes_path.exists():
        return fallback
    try:
        text = scenes_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return fallback
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("TITLE") and "=" in s:
            part = s.split("=", 1)[1].strip()
            if part.startswith(("'", '"')):
                quote = part[0]
                end = part.find(quote, 1)
                if end > 1:
                    return part[1:end] or fallback
            return part.strip("'\"") or fallback
    # folder name: 006_stopped_clock_... -> stopped clock
    parts = fallback.split("_")
    if parts and parts[0].isdigit():
        parts = parts[1:]
    # drop date-like tail
    cleaned = []
    for p in parts:
        if len(p) == 10 and p[4] == "-" and p[7] == "-":
            break
        if len(p) == 4 and p.isdigit():
            break
        cleaned.append(p)
    if cleaned:
        return " ".join(cleaned).replace("-", " ").strip() or fallback
    return fallback


def migrate(dry_run: bool = False, force: bool = False) -> dict:
    legacy = ROOT / "channels"
    stats = {
        "channels_created": 0,
        "channels_existing": 0,
        "episodes_created": 0,
        "episodes_existing": 0,
        "files_copied": 0,
        "errors": [],
    }

    print(f"ROOT     = {ROOT}")
    print(f"DB       = {D.DB_PATH}")
    print(f"STORAGE  = {D.STORAGE}")
    print(f"LEGACY   = {legacy}")
    print(f"dry_run  = {dry_run}  force = {force}")
    print("-" * 50)

    if not legacy.exists():
        print("[!] Папка channels/ не найдена — нечего импортировать.")
        print(f"    Ожидалось: {legacy}")
        return stats

    if not dry_run:
        D.init_db()

    ch_dirs = sorted([p for p in legacy.iterdir() if p.is_dir()])
    if not ch_dirs:
        print("[!] channels/ пустая")
        return stats

    for ch_dir in ch_dirs:
        slug = ch_dir.name
        print(f"\n# Канал: {slug}")

        ch = None if dry_run else D.get_channel_by_slug(slug)
        if ch:
            stats["channels_existing"] += 1
            print(f"  (уже в БД id={ch['id']})")
        else:
            if dry_run:
                print(f"  + создал бы канал «{slug}»")
                stats["channels_created"] += 1
                ch = {"id": -1, "slug": slug, "name": slug}
            else:
                try:
                    ch = D.create_channel(slug)
                    stats["channels_created"] += 1
                    print(f"  + канал создан id={ch['id']}")
                except ValueError:
                    ch = D.get_channel_by_slug(slug)
                    stats["channels_existing"] += 1

        for kind, folder_name in (("shorts", "shorts"), ("long", "longs")):
            src_kind = ch_dir / "videos" / folder_name
            if not src_kind.is_dir():
                # also try without videos/
                alt = ch_dir / folder_name
                if alt.is_dir():
                    src_kind = alt
                else:
                    continue

            for ep_dir in sorted(src_kind.iterdir()):
                if not ep_dir.is_dir():
                    continue
                folder = ep_dir.name
                title = titlelib.resolve_title(ep_dir, folder)

                exists = False
                if not dry_run and ch and ch["id"] != -1:
                    import sqlite3
                    conn = D.connect()
                    row = conn.execute(
                        "SELECT id FROM episodes WHERE channel_id=? AND folder=?",
                        (ch["id"], folder),
                    ).fetchone()
                    conn.close()
                    exists = row is not None
                    if exists:
                        stats["episodes_existing"] += 1
                        print(f"  · {folder} — уже в БД, обновляю флаги…")
                        D._refresh_flags(row["id"])
                        # optionally force-copy files
                        if force:
                            dest = (
                                D.STORAGE
                                / ch["slug"]
                                / folder_name
                                / folder
                            )
                            if dest.exists():
                                shutil.rmtree(dest)
                            shutil.copytree(ep_dir, dest)
                            stats["files_copied"] += 1
                            D._refresh_flags(row["id"])
                            print(f"    force-copy → {dest}")
                        continue

                dest = D.STORAGE / slug / folder_name / folder
                print(f"  + {kind}: «{title}»")
                print(f"    from {ep_dir}")
                print(f"    to   {dest}")

                if dry_run:
                    stats["episodes_created"] += 1
                    continue

                try:
                    if not dest.exists():
                        shutil.copytree(ep_dir, dest)
                        stats["files_copied"] += 1
                    elif force:
                        shutil.rmtree(dest)
                        shutil.copytree(ep_dir, dest)
                        stats["files_copied"] += 1

                    now = datetime.now().isoformat(timespec="seconds")
                    conn = D.connect()
                    conn.execute(
                        """
                        INSERT INTO episodes(
                            channel_id, title, kind, status, folder,
                            created_at, updated_at
                        ) VALUES (?,?,?,?,?,?,?)
                        """,
                        (
                            ch["id"],
                            title,
                            "shorts" if kind == "shorts" else "long",
                            "draft",
                            folder,
                            now,
                            now,
                        ),
                    )
                    conn.commit()
                    ep_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
                    conn.close()
                    ep = D._refresh_flags(ep_id)
                    stats["episodes_created"] += 1
                    print(
                        f"    id={ep_id} status={ep.get('status')} "
                        f"voice={ep.get('has_voice')} video={ep.get('has_video')}"
                    )
                except Exception as e:
                    msg = f"{folder}: {e}"
                    stats["errors"].append(msg)
                    print(f"    [ERR] {msg}")

    print("\n" + "=" * 50)
    print("ИТОГО:")
    for k, v in stats.items():
        if k != "errors":
            print(f"  {k}: {v}")
    if stats["errors"]:
        print("  errors:")
        for e in stats["errors"]:
            print(f"    - {e}")
    print("=" * 50)
    if not dry_run:
        print(f"\nБД: {D.DB_PATH}")
        print("Открой UI → Контент — ролики должны появиться.")
    return stats


def main():
    ap = argparse.ArgumentParser(description="Миграция channels/ → SQLite + storage/")
    ap.add_argument("--dry-run", action="store_true", help="Только показать, без записи")
    ap.add_argument("--force", action="store_true", help="Перезаписать файлы в storage/")
    args = ap.parse_args()
    migrate(dry_run=args.dry_run, force=args.force)


if __name__ == "__main__":
    main()
