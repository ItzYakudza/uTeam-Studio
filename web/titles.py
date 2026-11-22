"""Extract human title from youtube_metadata.txt / scenes.py / folder name."""
from __future__ import annotations

import re
from pathlib import Path


def title_from_folder(folder: str) -> str:
    parts = folder.split("_")
    if parts and parts[0].isdigit():
        parts = parts[1:]
    cleaned = []
    for p in parts:
        if len(p) == 10 and p[4:5] == "-" and p[7:8] == "-":
            break
        if len(p) == 4 and p.isdigit():
            break
        cleaned.append(p)
    if not cleaned:
        return folder
    return " ".join(cleaned).replace("-", " ").strip()


def title_from_meta_file(path: Path) -> str | None:
    """
    Format used by uTeam-Studio:

        TITLE
        How Children Were Treated...

        DESCRIPTION
        ...
    """
    if not path.exists():
        return None
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return None

    lines = text.splitlines()
    for i, line in enumerate(lines):
        key = line.strip().upper()
        if key == "TITLE":
            # next non-empty line is the title
            for j in range(i + 1, len(lines)):
                t = lines[j].strip()
                if not t:
                    continue
                # stop if we hit another section header
                if t.upper() in ("DESCRIPTION", "TAGS", "CHAPTERS", "SOURCES"):
                    break
                if t.upper().startswith("DESCRIPTION") or t.upper().startswith("TAGS"):
                    break
                return t
        # TITLE: value
        if key.startswith("TITLE:"):
            t = line.split(":", 1)[1].strip()
            if t:
                return t
        # TITLE = value
        if key.startswith("TITLE=") or key.startswith("TITLE ="):
            t = line.split("=", 1)[1].strip().strip('"').strip("'")
            if t:
                return t
    return None


def title_from_scenes(text: str) -> str | None:
    m = re.search(
        r'''^\s*TITLE\s*=\s*([ruUfF]?"""[\s\S]*?"""|[ruUfF]?\'\'\'[\s\S]*?\'\'\'|[ruUfF]?"(?:\\.|[^"\\])*"|[ruUfF]?'(?:\\.|[^'\\])*')''',
        text,
        re.M,
    )
    if m:
        raw = m.group(1)
        raw = re.sub(r"^[ruUfF]+", "", raw)
        if raw.startswith('"""') or raw.startswith("'''"):
            val = raw[3:-3]
        else:
            val = raw[1:-1]
        val = val.strip()
        if val and "META[" not in val and not val.startswith("{"):
            return val
    return None


def resolve_title(ep_dir: Path, folder_name: str | None = None) -> str:
    """
    Priority:
      1. build/youtube_metadata.txt  (TITLE + next line)
      2. scenes.py TITLE = "..."
      3. folder name humanized
    """
    folder_name = folder_name or ep_dir.name

    meta = ep_dir / "build" / "youtube_metadata.txt"
    t = title_from_meta_file(meta)
    if t:
        return t

    scenes = ep_dir / "scenes.py"
    if scenes.exists():
        try:
            t = title_from_scenes(scenes.read_text(encoding="utf-8", errors="ignore"))
            if t:
                return t
        except Exception:
            pass

    return title_from_folder(folder_name)
