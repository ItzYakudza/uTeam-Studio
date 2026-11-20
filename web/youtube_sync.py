"""
Fetch public YouTube metadata / stats.

Primary: yt-dlp (no API key)
Optional: YOUTUBE_API_KEY env for Data API v3
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from datetime import datetime
from typing import Any, Optional
from urllib.parse import parse_qs, urlparse
from urllib.request import Request, urlopen


YOUTUBE_ID_RE = re.compile(
    r"(?:youtu\.be/|youtube\.com/(?:watch\?v=|shorts/|embed/|live/))([A-Za-z0-9_-]{11})"
)


def extract_video_id(url_or_id: str) -> Optional[str]:
    s = (url_or_id or "").strip()
    if not s:
        return None
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", s):
        return s
    m = YOUTUBE_ID_RE.search(s)
    if m:
        return m.group(1)
    # query v=
    try:
        q = parse_qs(urlparse(s).query)
        if "v" in q and q["v"]:
            vid = q["v"][0]
            if re.fullmatch(r"[A-Za-z0-9_-]{11}", vid):
                return vid
    except Exception:
        pass
    return None


def canonical_url(video_id: str) -> str:
    return f"https://www.youtube.com/watch?v={video_id}"


def _ytdlp() -> Optional[str]:
    return shutil.which("yt-dlp") or shutil.which("yt_dlp")


def fetch_via_ytdlp(video_id: str) -> dict[str, Any]:
    exe = _ytdlp()
    if not exe:
        raise RuntimeError(
            "yt-dlp не найден. Установи: pip install yt-dlp   "
            "или скачай с https://github.com/yt-dlp/yt-dlp"
        )
    url = canonical_url(video_id)
    cmd = [
        exe,
        "--skip-download",
        "--no-warnings",
        "-J",
        url,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "").strip()[:400]
        raise RuntimeError(f"yt-dlp error: {err or 'unknown'}")
    data = json.loads(proc.stdout)
    # availability
    if data.get("availability") in ("private", "premium_only"):
        raise RuntimeError("Видео недоступно (private/premium)")
    views = data.get("view_count") or 0
    likes = data.get("like_count") or 0
    comments = data.get("comment_count") or 0
    title = data.get("title") or ""
    channel = data.get("channel") or data.get("uploader") or ""
    duration = data.get("duration")
    thumb = None
    if data.get("thumbnails"):
        thumb = data["thumbnails"][-1].get("url")
    elif data.get("thumbnail"):
        thumb = data.get("thumbnail")
    tags = data.get("tags") or []
    if isinstance(tags, str):
        tags = [tags]
    privacy = data.get("availability") or data.get("live_status") or "public"
    # normalize
    if data.get("availability") == "public":
        privacy = "public"
    elif data.get("availability") in ("unlisted", "private", "premium_only", "subscriber_only"):
        privacy = data.get("availability")
    return {
        "ok": True,
        "exists": True,
        "video_id": video_id,
        "url": canonical_url(video_id),
        "title": title,
        "channel": channel,
        "views": int(views or 0),
        "likes": int(likes or 0),
        "comments": int(comments or 0),
        "duration_sec": float(duration) if duration else None,
        "thumbnail": thumb,
        "upload_date": data.get("upload_date"),
        "published_at": data.get("upload_date"),
        "description": (data.get("description") or "")[:4000],
        "tags": tags,
        "privacy": privacy,
        "availability": data.get("availability"),
        "source": "yt-dlp",
        # Studio-only metrics — null unless provided by future API
        "avg_view_duration_sec": None,
        "retention_pct": None,
        "swipe_away_pct": None,
    }


def fetch_via_api(video_id: str) -> dict[str, Any]:
    key = os.environ.get("YOUTUBE_API_KEY") or os.environ.get("YT_API_KEY")
    if not key:
        raise RuntimeError("YOUTUBE_API_KEY не задан")
    api = (
        "https://www.googleapis.com/youtube/v3/videos"
        f"?part=snippet,statistics,contentDetails&id={video_id}&key={key}"
    )
    req = Request(api, headers={"User-Agent": "uTeam-Studio/2.0"})
    with urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    items = data.get("items") or []
    if not items:
        return {
            "ok": False,
            "exists": False,
            "video_id": video_id,
            "error": "Видео не найдено в YouTube API",
        }
    item = items[0]
    sn = item.get("snippet") or {}
    st = item.get("statistics") or {}
    return {
        "ok": True,
        "exists": True,
        "video_id": video_id,
        "url": canonical_url(video_id),
        "title": sn.get("title") or "",
        "channel": sn.get("channelTitle") or "",
        "views": int(st.get("viewCount") or 0),
        "likes": int(st.get("likeCount") or 0),
        "comments": int(st.get("commentCount") or 0),
        "duration_sec": None,
        "thumbnail": (sn.get("thumbnails") or {}).get("high", {}).get("url"),
        "upload_date": (sn.get("publishedAt") or "")[:10].replace("-", ""),
        "description": (sn.get("description") or "")[:500],
        "source": "youtube-api",
    }


def fetch_oembed_exists(video_id: str) -> dict[str, Any]:
    """Lightweight existence + title check (no stats)."""
    url = f"https://www.youtube.com/oembed?url={canonical_url(video_id)}&format=json"
    try:
        req = Request(url, headers={"User-Agent": "uTeam-Studio/2.0"})
        with urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return {
            "ok": True,
            "exists": True,
            "video_id": video_id,
            "url": canonical_url(video_id),
            "title": data.get("title") or "",
            "channel": data.get("author_name") or "",
            "views": 0,
            "likes": 0,
            "comments": 0,
            "source": "oembed",
        }
    except Exception as e:
        return {
            "ok": False,
            "exists": False,
            "video_id": video_id,
            "error": str(e),
        }


def fetch_video(url_or_id: str) -> dict[str, Any]:
    vid = extract_video_id(url_or_id)
    if not vid:
        return {"ok": False, "exists": False, "error": "Не удалось распознать YouTube ID / ссылку"}

    errors = []
    # 1) yt-dlp
    try:
        return fetch_via_ytdlp(vid)
    except Exception as e:
        errors.append(f"yt-dlp: {e}")

    # 2) official API
    try:
        return fetch_via_api(vid)
    except Exception as e:
        errors.append(f"api: {e}")

    # 3) oembed existence only
    info = fetch_oembed_exists(vid)
    if info.get("exists"):
        info["warning"] = "; ".join(errors)
        return info

    return {
        "ok": False,
        "exists": False,
        "video_id": vid,
        "error": "Видео не найдено или недоступно",
        "details": errors,
    }


def today() -> str:
    return datetime.now().strftime("%Y-%m-%d")



def list_channel_videos(channel_url: str, limit: int = 50) -> list[dict]:
    """List recent videos on a channel via yt-dlp flat playlist."""
    exe = _ytdlp()
    if not exe:
        raise RuntimeError("yt-dlp не найден (pip install yt-dlp)")
    url = channel_url.strip()
    if not url:
        raise RuntimeError("Пустой URL канала")
    # normalize common forms
    if url.startswith("@"):
        url = "https://www.youtube.com/" + url + "/videos"
    elif "youtube.com" in url and "/videos" not in url and "/@" in url:
        url = url.rstrip("/") + "/videos"
    cmd = [
        exe,
        "--skip-download",
        "--flat-playlist",
        "--playlist-end", str(limit),
        "-J",
        url,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if proc.returncode != 0:
        raise RuntimeError((proc.stderr or proc.stdout or "yt-dlp channel error")[:400])
    data = json.loads(proc.stdout)
    entries = data.get("entries") or []
    out = []
    for e in entries:
        if not e:
            continue
        vid = e.get("id") or extract_video_id(e.get("url") or "")
        title = e.get("title") or ""
        if not vid:
            continue
        out.append({
            "video_id": vid,
            "title": title,
            "url": canonical_url(vid),
            "duration": e.get("duration"),
            "view_count": e.get("view_count"),
        })
    return out


def best_title_match(title: str, candidates: list[dict], threshold: float = 0.45) -> dict | None:
    """Simple token overlap match."""
    def tokens(s):
        s = re.sub(r"[^a-z0-9а-яё\s]", " ", (s or "").lower())
        return {t for t in s.split() if len(t) > 2}
    base = tokens(title)
    if not base:
        return None
    best = None
    best_score = 0.0
    for c in candidates:
        ct = tokens(c.get("title") or "")
        if not ct:
            continue
        score = len(base & ct) / max(len(base | ct), 1)
        if score > best_score:
            best_score = score
            best = c
    if best and best_score >= threshold:
        best = dict(best)
        best["match_score"] = round(best_score, 3)
        return best
    return None
