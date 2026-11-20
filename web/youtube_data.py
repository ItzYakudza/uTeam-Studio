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


def _parse_ts(val) -> Optional[datetime]:
    if not val:
        return None
    try:
        s = str(val).replace("Z", "+00:00")
        return datetime.fromisoformat(s)
    except Exception:
        return None


def _history_metrics_key(row: dict) -> tuple:
    """Core counters used to decide if a snapshot is new."""
    def _i(k):
        v = row.get(k)
        try:
            return int(v) if v is not None else None
        except Exception:
            return None
    def _f(k):
        v = row.get(k)
        try:
            return round(float(v), 3) if v is not None else None
        except Exception:
            return None
    return (
        _i("views"),
        _i("likes"),
        _i("comments"),
        _i("engaged_views"),
        _f("avg_view_duration_sec"),
        _f("average_view_percentage"),
        _f("stayed_pct"),
        _f("swipe_away_pct"),
        _i("impressions"),
    )


def append_stats_line(
    path: Path,
    row: dict,
    *,
    min_interval_minutes: int = 30,
    force: bool = False,
) -> bool:
    """
    Append a history snapshot only if meaningful:
      - views / likes / comments / engaged / retention metrics changed, OR
      - at least min_interval_minutes passed since the last line.
    Always safe to call; returns True if a line was written.
    """
    path.parent.mkdir(parents=True, exist_ok=True)

    if not force and path.exists() and path.stat().st_size > 0:
        last = None
        try:
            # read last non-empty line
            with path.open("rb") as f:
                f.seek(0, 2)
                size = f.tell()
                block = 4096
                data = b""
                while size > 0 and data.count(b"\n") < 2:
                    step = min(block, size)
                    size -= step
                    f.seek(size)
                    data = f.read(step) + data
                lines = [ln for ln in data.splitlines() if ln.strip()]
                if lines:
                    last = json.loads(lines[-1].decode("utf-8"))
        except Exception:
            last = None

        if last is not None:
            same = _history_metrics_key(last) == _history_metrics_key(row)
            if same:
                last_ts = _parse_ts(last.get("ts") or last.get("checked_at") or last.get("date"))
                now_ts = _parse_ts(row.get("ts") or row.get("checked_at")) or datetime.now().astimezone()
                if last_ts is not None:
                    # normalize tz-naive
                    if last_ts.tzinfo is None and now_ts.tzinfo is not None:
                        last_ts = last_ts.replace(tzinfo=now_ts.tzinfo)
                    if now_ts.tzinfo is None and last_ts.tzinfo is not None:
                        now_ts = now_ts.replace(tzinfo=last_ts.tzinfo)
                    delta_min = (now_ts - last_ts).total_seconds() / 60.0
                    if delta_min < max(1, int(min_interval_minutes)):
                        return False
                else:
                    # no timestamp on last line — skip identical metrics
                    return False

    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return True



def compact_stats_history(
    ep_path: Path,
    *,
    min_interval_minutes: int = 30,
) -> dict:
    """
    Rewrite stats.jsonl dropping consecutive identical metric snapshots
    within min_interval_minutes. Keeps latest.json untouched.
    """
    path = yt_dir(ep_path) / "stats.jsonl"
    if not path.exists():
        return {"ok": True, "before": 0, "after": 0}
    lines = [ln.strip() for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    before = len(lines)
    kept: list[dict] = []
    for ln in lines:
        try:
            row = json.loads(ln)
        except Exception:
            continue
        if not kept:
            kept.append(row)
            continue
        prev = kept[-1]
        same = _history_metrics_key(prev) == _history_metrics_key(row)
        if not same:
            kept.append(row)
            continue
        prev_ts = _parse_ts(prev.get("ts") or prev.get("checked_at") or prev.get("date"))
        cur_ts = _parse_ts(row.get("ts") or row.get("checked_at") or row.get("date"))
        if prev_ts and cur_ts:
            if prev_ts.tzinfo is None and cur_ts.tzinfo is not None:
                prev_ts = prev_ts.replace(tzinfo=cur_ts.tzinfo)
            if cur_ts.tzinfo is None and prev_ts.tzinfo is not None:
                cur_ts = cur_ts.replace(tzinfo=prev_ts.tzinfo)
            if (cur_ts - prev_ts).total_seconds() / 60.0 >= min_interval_minutes:
                kept.append(row)
            else:
                # replace last with newer timestamp but same metrics
                kept[-1] = row
        else:
            kept[-1] = row
    path.write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in kept),
        encoding="utf-8",
    )
    return {"ok": True, "before": before, "after": len(kept)}


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

    published = (
        meta.get("published_at")
        or meta.get("upload_date")
        or info.get("upload_date")
        or info.get("published_at")
    )

    # --- Fast layer: views/likes/comments (Data API v3, ~minutes lag) ---
    views = int(info.get("views") or 0)
    likes = int(info.get("likes") or 0)
    comments = int(info.get("comments") or 0)
    fast_source = info.get("source") or "public"
    try:
        import oauth_youtube as OYT
        if OYT.status().get("connected"):
            fast = OYT.fetch_video_public_stats(meta["video_id"])
            if fast.get("ok"):
                views = int(fast.get("views") or views or 0)
                likes = int(fast.get("likes") or likes or 0)
                comments = int(fast.get("comments") or comments or 0)
                if fast.get("duration_sec") is not None:
                    meta["duration_sec"] = fast.get("duration_sec")
                if fast.get("published_at"):
                    published = fast.get("published_at")
                    meta["published_at"] = published
                if fast.get("privacy"):
                    meta["privacy"] = fast.get("privacy")
                if fast.get("thumbnail") and not info.get("thumbnail"):
                    info["thumbnail"] = fast.get("thumbnail")
                if fast.get("title") and not meta.get("title"):
                    meta["title"] = fast.get("title")
                fast_source = "youtube-data-api-v3"
                # refresh meta on disk with richer fields
                write_json(d / "meta.json", meta)
    except Exception as e:
        fast_source = f"public+err:{(str(e))[:80]}"

    snap = {
        "ts": _now_iso(),
        "date": YT.today(),
        "video_id": meta["video_id"],
        "url": meta["url"],
        "views": views,
        "likes": likes,
        "comments": comments,
        "duration_sec": meta.get("duration_sec"),
        "avg_view_duration_sec": None,
        "average_view_percentage": None,
        "swipe_away_pct": None,
        "stayed_pct": None,
        "privacy": meta.get("privacy"),
        "source": fast_source,
        "include_in_aggregate": True,
        "layer": "fast",
    }

    # --- Deep layer: YouTube Analytics API only if age >= 24 hours ---
    try:
        import oauth_youtube as OYT
        if not OYT.status().get("connected"):
            snap["studio_error"] = "OAuth not connected"
        else:
            age_h = OYT.video_age_hours(published)
            snap["age_hours"] = round(age_h, 2) if age_h is not None else None
            # Unknown age → try Analytics (may still work)
            too_new = age_h is not None and age_h < 24
            if too_new:
                snap["studio_skipped"] = True
                snap["studio_skip_reason"] = (
                    f"ролик младше 24ч ({age_h:.1f}h) — только Data API "
                    "(views/likes ~5 мин). Analytics (ср. просмотр, реакция) после 24ч."
                )
            else:
                studio = OYT.video_studio_stats(
                    meta["video_id"],
                    days=28,
                    published_at=published,
                )
                if studio.get("ok"):
                    snap["avg_view_duration_sec"] = studio.get("average_view_duration_sec")
                    snap["average_view_percentage"] = studio.get("average_view_percentage")
                    if snap.get("average_view_percentage") is None and snap.get("avg_view_duration_sec") is not None:
                        dur = meta.get("duration_sec") or info.get("duration_sec")
                        try:
                            dur = float(dur) if dur else None
                        except Exception:
                            dur = None
                        if dur and dur > 0:
                            snap["average_view_percentage"] = round(
                                min(200.0, (float(snap["avg_view_duration_sec"]) / dur) * 100.0), 2
                            )
                    snap["swipe_away_pct"] = studio.get("swipe_away_pct")
                    snap["stayed_pct"] = studio.get("stayed_pct")
                    snap["engaged_views"] = studio.get("engaged_views")
                    snap["estimated_minutes_watched"] = studio.get("estimated_minutes_watched")
                    snap["shares"] = studio.get("shares")
                    snap["subscribers_gained"] = studio.get("subscribers_gained")
                    snap["subscribers_lost"] = studio.get("subscribers_lost")
                    snap["impressions"] = studio.get("impressions")
                    snap["impressions_ctr"] = studio.get("impressions_ctr")
                    snap["clicks_est"] = studio.get("clicks_est")
                    if studio.get("retention"):
                        snap["retention_early_drop_pct"] = (studio.get("retention") or {}).get("early_drop_pct")
                    if studio.get("reporting_reach"):
                        snap["reporting_reach"] = studio.get("reporting_reach")
                    # Keep Data API views/likes as source of truth for counters;
                    # only fill if Data API returned zeros and Analytics has numbers
                    if (not views) and studio.get("views") is not None:
                        snap["views"] = int(studio.get("views") or 0)
                    if (not likes) and studio.get("likes") is not None:
                        snap["likes"] = int(studio.get("likes") or 0)
                    if (not comments) and studio.get("comments") is not None:
                        snap["comments"] = int(studio.get("comments") or 0)
                    snap["source"] = f"{fast_source}+youtube-analytics-api"
                    snap["layer"] = "fast+deep"
                    snap["studio"] = {k: studio.get(k) for k in (
                        "average_view_duration_sec", "average_view_percentage", "swipe_away_pct",
                        "stayed_pct", "engaged_views", "estimated_minutes_watched", "shares",
                        "subscribers_gained", "subscribers_lost", "impressions", "impressions_ctr",
                        "clicks_est", "range_start", "range_end", "range_label", "notes",
                    )}
                else:
                    snap["studio_error"] = (studio.get("error") or "studio metrics unavailable")[:300]
                    if studio.get("hint"):
                        snap["studio_hint"] = studio["hint"]
    except Exception as e:
        snap["studio_error"] = str(e)[:300]

    append_stats_line(d / "stats.jsonl", snap)
    # One-shot compact if file got bloated by frequent identical polls
    try:
        if (d / "stats.jsonl").exists() and (d / "stats.jsonl").stat().st_size > 50_000:
            compact_stats_history(ep_path, min_interval_minutes=30)
    except Exception:
        pass
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
