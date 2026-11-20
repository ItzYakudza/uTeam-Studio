"""
Per-episode YouTube data under:
  storage/<channel>/<shorts|longs>/<episode>/youtube_data/

Layout:
  meta.json      — title, description, tags, duration, privacy, published_at, ids
  stats.jsonl    — append-only snapshots (one JSON object per line)
  latest.json    — last successful snapshot (stats + meta refs)
  thumb.jpg|png  — cover from YouTube (never generated from video frames)
  status.json    — exists / unavailable / error flags for workers
"""
from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional
from urllib.request import Request, urlopen

import youtube_sync as YT

YT_DIRNAME = "youtube_data"


def _now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def yt_dir(ep_path: Path) -> Path:
    return Path(ep_path) / YT_DIRNAME


def ensure_yt_dir(ep_path: Path) -> Path:
    d = yt_dir(ep_path)
    d.mkdir(parents=True, exist_ok=True)
    return d


def read_json(path: Path, default=None):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def append_stats_line(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def local_preview_path(ep_path: Path) -> Optional[Path]:
    """Cover only from explicit files — never from video frames."""
    build = Path(ep_path) / "build"
    candidates = []
    # prefer youtube_data thumb after sync
    yd = yt_dir(ep_path)
    for name in ("thumb.jpg", "thumb.png", "cover.jpg", "cover.png"):
        candidates.append(yd / name)
    for name in (
        "preview.png", "preview.jpg", "preview.jpeg",
        "Preview.png", "Preview.jpg",
        "thumb.jpg", "thumb.png",
    ):
        candidates.append(Path(ep_path) / name)
        candidates.append(build / name)
    for p in candidates:
        if p.exists() and p.is_file():
            return p
    return None


def display_meta(ep_path: Path) -> dict:
    """
    What UI should show for a card/detail.
    Prefer youtube_data after publish; else local production files.
    """
    ep_path = Path(ep_path)
    yd = yt_dir(ep_path)
    meta = read_json(yd / "meta.json") or {}
    latest = read_json(yd / "latest.json") or {}
    status = read_json(yd / "status.json") or {}

    # local production title/desc from build metadata
    local_title = None
    local_desc = None
    local_tags = None
    meta_txt = ep_path / "build" / "youtube_metadata.txt"
    if meta_txt.exists():
        try:
            import titles as titlelib
            local_title = titlelib.title_from_meta_file(meta_txt)
        except Exception:
            local_title = None
        try:
            text = meta_txt.read_text(encoding="utf-8", errors="ignore")
            lines = text.splitlines()
            section = None
            buf = []
            sections = {}
            for line in lines:
                key = line.strip().upper()
                if key in ("TITLE", "DESCRIPTION", "TAGS"):
                    if section:
                        sections[section] = "\n".join(buf).strip()
                    section = key
                    buf = []
                else:
                    if section:
                        buf.append(line)
            if section:
                sections[section] = "\n".join(buf).strip()
            local_desc = sections.get("DESCRIPTION")
            local_tags = sections.get("TAGS")
            if not local_title:
                local_title = sections.get("TITLE")
        except Exception:
            pass

    use_yt = bool(meta.get("video_id")) and status.get("available") is not False
    title = (meta.get("title") if use_yt else None) or local_title
    description = (meta.get("description") if use_yt else None) or local_desc or ""
    tags = (meta.get("tags") if use_yt else None) or local_tags or ""
    if isinstance(tags, list):
        tags = ", ".join(tags)

    preview = local_preview_path(ep_path)
    return {
        "title": title,
        "description": description,
        "tags": tags,
        "has_youtube_data": (yd / "meta.json").exists(),
        "youtube_available": status.get("available"),
        "youtube_id": meta.get("video_id") or latest.get("video_id"),
        "youtube_url": meta.get("url") or latest.get("url"),
        "privacy": meta.get("privacy"),
        "published_at": meta.get("published_at"),
        "duration_sec": meta.get("duration_sec") or latest.get("duration_sec"),
        "preview_path": str(preview) if preview else None,
        "has_preview": preview is not None,
        "views": latest.get("views"),
        "likes": latest.get("likes"),
        "comments": latest.get("comments"),
        "source": "youtube_data" if use_yt else "local",
    }


def download_thumb(url: str, dest_jpg: Path) -> bool:
    if not url:
        return False
    try:
        req = Request(url, headers={"User-Agent": "uTeam-Studio/2.0"})
        with urlopen(req, timeout=45) as resp:
            data = resp.read()
        if len(data) < 500:
            return False
        dest_jpg.parent.mkdir(parents=True, exist_ok=True)
        # try keep as jpg; if png magic, save png
        if data[:8] == b"\x89PNG\r\n\x1a\n":
            dest = dest_jpg.with_suffix(".png")
            dest.write_bytes(data)
            return True
        dest_jpg.write_bytes(data)
        return True
    except Exception:
        return False


def sync_episode_folder(ep_path: Path, url_or_id: str) -> dict:
    """
    Fetch YouTube info → write youtube_data/* and return normalized result.
    """
    ep_path = Path(ep_path)
    d = ensure_yt_dir(ep_path)
    info = YT.fetch_video(url_or_id)

    status = {
        "checked_at": _now_iso(),
        "available": bool(info.get("exists")),
        "ok": bool(info.get("ok") and info.get("exists")),
        "error": info.get("error"),
        "source": info.get("source"),
    }

    if not info.get("exists"):
        write_json(d / "status.json", status)
        # keep previous meta/stats; only mark unavailable
        return {"ok": False, "available": False, "status": status, "info": info}

    meta = {
        "video_id": info.get("video_id"),
        "url": info.get("url") or YT.canonical_url(info["video_id"]),
        "title": info.get("title") or "",
        "description": info.get("description") or "",
        "tags": info.get("tags") or [],
        "channel": info.get("channel") or "",
        "duration_sec": info.get("duration_sec"),
        "privacy": info.get("privacy") or info.get("availability") or "public",
        "published_at": info.get("upload_date") or info.get("published_at"),
        "thumbnail_url": info.get("thumbnail"),
        "updated_at": _now_iso(),
    }
    # yt-dlp sometimes has more fields on raw — ignore if absent
    write_json(d / "meta.json", meta)

    snap = {
        "ts": _now_iso(),
        "date": YT.today(),
        "video_id": meta["video_id"],
        "url": meta["url"],
        "views": int(info.get("views") or 0),
        "likes": int(info.get("likes") or 0),
        "comments": int(info.get("comments") or 0),
        "duration_sec": meta.get("duration_sec"),
        "avg_view_duration_sec": info.get("avg_view_duration_sec"),  # usually null without Studio API
        "retention_pct": info.get("retention_pct"),
        "swipe_away_pct": info.get("swipe_away_pct"),
        "privacy": meta.get("privacy"),
        "source": info.get("source"),
        "include_in_aggregate": True,
    }
    # Studio OAuth metrics (if connected)
    try:
        import oauth_youtube as OYT
        if OYT.status().get("connected"):
            studio = OYT.video_studio_stats(meta["video_id"], days=365)
            if studio.get("ok"):
                snap["avg_view_duration_sec"] = studio.get("average_view_duration_sec")
                snap["average_view_percentage"] = studio.get("average_view_percentage")
                snap["swipe_away_pct"] = studio.get("swipe_away_pct")
                snap["estimated_minutes_watched"] = studio.get("estimated_minutes_watched")
                snap["shares"] = studio.get("shares")
                snap["subscribers_gained"] = studio.get("subscribers_gained")
                snap["subscribers_lost"] = studio.get("subscribers_lost")
                # prefer analytics views if present
                if studio.get("views") is not None:
                    snap["views"] = int(studio.get("views") or snap.get("views") or 0)
                if studio.get("likes") is not None:
                    snap["likes"] = int(studio.get("likes") or snap.get("likes") or 0)
                if studio.get("comments") is not None:
                    snap["comments"] = int(studio.get("comments") or snap.get("comments") or 0)
                snap["source"] = "youtube-analytics-api"
                snap["studio"] = {k: studio.get(k) for k in (
                    "average_view_duration_sec", "average_view_percentage", "swipe_away_pct",
                    "estimated_minutes_watched", "shares", "subscribers_gained", "subscribers_lost",
                    "range_start", "range_end",
                )}
    except Exception as e:
        snap["studio_error"] = str(e)[:200]

    append_stats_line(d / "stats.jsonl", snap)
    write_json(d / "latest.json", snap)

    # cover from YT thumbnail only (not video frame)
    if info.get("thumbnail"):
        download_thumb(info["thumbnail"], d / "thumb.jpg")

    status["available"] = True
    status["ok"] = True
    write_json(d / "status.json", status)

    return {
        "ok": True,
        "available": True,
        "status": status,
        "meta": meta,
        "stats": snap,
        "info": info,
        "youtube_data_dir": str(d),
    }


def load_stats_history(ep_path: Path) -> list[dict]:
    path = yt_dir(ep_path) / "stats.jsonl"
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except Exception:
            pass
    return rows


def mark_unavailable(ep_path: Path, error: str = "not found") -> None:
    d = ensure_yt_dir(ep_path)
    status = read_json(d / "status.json") or {}
    status.update({
        "checked_at": _now_iso(),
        "available": False,
        "ok": False,
        "error": error,
    })
    write_json(d / "status.json", status)
    # flag last latest.json
    latest = read_json(d / "latest.json")
    if latest:
        latest["include_in_aggregate"] = False
        latest["unavailable_at"] = _now_iso()
        write_json(d / "latest.json", latest)
