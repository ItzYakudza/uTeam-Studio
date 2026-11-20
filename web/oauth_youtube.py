"""
YouTube OAuth2 + Analytics helpers.

Setup:
  1. Google Cloud Console → OAuth client (Web application)
  2. Redirect URI: http://127.0.0.1:5050/api/oauth/youtube/callback
  3. Save into web/youtube_oauth.json:
       {"client_id": "...", "client_secret": "..."}
     or set env YT_CLIENT_ID / YT_CLIENT_SECRET

Token file: YouTube/studio_oauth_token.json
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Optional

WEB_DIR = Path(__file__).resolve().parent
ROOT = WEB_DIR.parent / "YouTube"
if not (ROOT / "build.py").exists():
    alt = WEB_DIR.parent
    if (alt / "build.py").exists():
        ROOT = alt

TOKEN_PATH = ROOT / "studio_oauth_token.json"
CLIENT_CONFIG_PATH = WEB_DIR / "youtube_oauth.json"

SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/yt-analytics.readonly",
]

AUTH_URI = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URI = "https://oauth2.googleapis.com/token"
REDIRECT_URI = os.environ.get(
    "YT_REDIRECT_URI", "http://127.0.0.1:5050/api/oauth/youtube/callback"
)


def _load_client() -> dict:
    cfg: dict = {}
    if CLIENT_CONFIG_PATH.exists():
        try:
            cfg = json.loads(CLIENT_CONFIG_PATH.read_text(encoding="utf-8"))
        except Exception:
            cfg = {}
    if "web" in cfg:
        cfg = cfg["web"]
    elif "installed" in cfg:
        cfg = cfg["installed"]
    client_id = os.environ.get("YT_CLIENT_ID") or cfg.get("client_id")
    client_secret = os.environ.get("YT_CLIENT_SECRET") or cfg.get("client_secret")
    if not client_id or not client_secret:
        raise RuntimeError(
            "Нет OAuth client. Создай web/youtube_oauth.json с client_id и client_secret. "
            f"Redirect URI: {REDIRECT_URI}"
        )
    return {"client_id": client_id, "client_secret": client_secret}


def _http_json(method: str, url: str, data: Optional[dict] = None, headers: Optional[dict] = None) -> dict:
    body = None
    hdrs = {"User-Agent": "uTeam-Studio/2.0", "Accept": "application/json"}
    if headers:
        hdrs.update(headers)
    if data is not None:
        body = urllib.parse.urlencode(data).encode("utf-8")
        hdrs.setdefault("Content-Type", "application/x-www-form-urlencoded")
    req = urllib.request.Request(url, data=body, headers=hdrs, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", errors="replace")[:600]
        raise RuntimeError(f"HTTP {e.code}: {err}") from e


def load_token() -> Optional[dict]:
    if not TOKEN_PATH.exists():
        return None
    try:
        return json.loads(TOKEN_PATH.read_text(encoding="utf-8"))
    except Exception:
        return None


def save_token(data: dict) -> None:
    TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def clear_token() -> None:
    if TOKEN_PATH.exists():
        TOKEN_PATH.unlink()


def status() -> dict:
    try:
        _load_client()
        configured = True
        cfg_error = None
    except Exception as e:
        return {"configured": False, "connected": False, "error": str(e)}
    tok = load_token()
    if not tok or not tok.get("access_token"):
        return {"configured": True, "connected": False}
    return {
        "configured": True,
        "connected": True,
        "expires_at": tok.get("expires_at"),
        "has_refresh": bool(tok.get("refresh_token")),
        "channel_id": tok.get("channel_id"),
        "channel_title": tok.get("channel_title"),
        "scope": tok.get("scope"),
    }


def auth_url(state: str = "uteam") -> str:
    client = _load_client()
    params = {
        "client_id": client["client_id"],
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "access_type": "offline",
        "prompt": "consent",
        "include_granted_scopes": "true",
        "state": state,
    }
    return AUTH_URI + "?" + urllib.parse.urlencode(params)


def exchange_code(code: str) -> dict:
    client = _load_client()
    data = {
        "code": code,
        "client_id": client["client_id"],
        "client_secret": client["client_secret"],
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    tok = _http_json("POST", TOKEN_URI, data=data)
    now = int(time.time())
    out = {
        "access_token": tok["access_token"],
        "refresh_token": tok.get("refresh_token"),
        "token_type": tok.get("token_type", "Bearer"),
        "scope": tok.get("scope"),
        "expires_at": now + int(tok.get("expires_in", 3600)) - 60,
        "obtained_at": now,
    }
    # keep old refresh if Google omitted it
    prev = load_token() or {}
    if not out.get("refresh_token") and prev.get("refresh_token"):
        out["refresh_token"] = prev["refresh_token"]
    save_token(out)
    # enrich with channel
    try:
        ch = fetch_mine_channel(out["access_token"])
        out.update(ch)
        save_token(out)
    except Exception:
        pass
    return out


def refresh_access_token() -> dict:
    client = _load_client()
    tok = load_token()
    if not tok or not tok.get("refresh_token"):
        raise RuntimeError("Нет refresh_token — нужно заново подключить YouTube")
    data = {
        "client_id": client["client_id"],
        "client_secret": client["client_secret"],
        "refresh_token": tok["refresh_token"],
        "grant_type": "refresh_token",
    }
    fresh = _http_json("POST", TOKEN_URI, data=data)
    now = int(time.time())
    tok["access_token"] = fresh["access_token"]
    tok["expires_at"] = now + int(fresh.get("expires_in", 3600)) - 60
    if fresh.get("scope"):
        tok["scope"] = fresh["scope"]
    save_token(tok)
    return tok


def get_access_token() -> str:
    tok = load_token()
    if not tok:
        raise RuntimeError("YouTube не подключён")
    if int(time.time()) >= int(tok.get("expires_at") or 0):
        tok = refresh_access_token()
    return tok["access_token"]


def _auth_headers() -> dict:
    return {"Authorization": f"Bearer {get_access_token()}"}


def fetch_mine_channel(access_token: Optional[str] = None) -> dict:
    token = access_token or get_access_token()
    url = "https://www.googleapis.com/youtube/v3/channels?part=snippet,contentDetails,statistics&mine=true"
    data = _http_json("GET", url, headers={"Authorization": f"Bearer {token}"})
    items = data.get("items") or []
    if not items:
        return {}
    item = items[0]
    sn = item.get("snippet") or {}
    cd = item.get("contentDetails") or {}
    related = cd.get("relatedPlaylists") or {}
    st = item.get("statistics") or {}
    return {
        "channel_id": item.get("id"),
        "channel_title": sn.get("title"),
        "channel_thumb": ((sn.get("thumbnails") or {}).get("default") or {}).get("url"),
        "uploads_playlist_id": related.get("uploads"),
        "subscribers": int(st.get("subscriberCount") or 0),
        "subscriberCount": int(st.get("subscriberCount") or 0),
        "viewCount": int(st.get("viewCount") or 0),
        "videoCount": int(st.get("videoCount") or 0),
        "statistics": st,
        "ok": True,
    }



def fetch_video_public_stats(video_id: str) -> dict:
    """
    Fast counters via YouTube Data API v3 (OAuth).
    Lag ~minutes. Returns views/likes/comments/duration/published_at.
    """
    if not video_id:
        return {"ok": False, "error": "no video_id"}
    params = {
        "part": "statistics,contentDetails,snippet,status",
        "id": video_id,
    }
    url = "https://www.googleapis.com/youtube/v3/videos?" + urllib.parse.urlencode(params)
    try:
        data = _http_json("GET", url, headers=_auth_headers())
    except Exception as e:
        return {"ok": False, "error": str(e)[:300]}
    items = data.get("items") or []
    if not items:
        return {"ok": False, "error": "video not found", "exists": False}
    it = items[0]
    st = it.get("statistics") or {}
    cd = it.get("contentDetails") or {}
    sn = it.get("snippet") or {}
    status = it.get("status") or {}
    dur = _parse_iso_duration(cd.get("duration")) if "_parse_iso_duration" in dir() else None
    try:
        dur = _parse_iso_duration(cd.get("duration"))
    except Exception:
        dur = None
    return {
        "ok": True,
        "exists": True,
        "video_id": video_id,
        "views": int(st.get("viewCount") or 0),
        "likes": int(st.get("likeCount") or 0),
        "comments": int(st.get("commentCount") or 0),
        "duration_sec": dur,
        "title": sn.get("title"),
        "description": sn.get("description"),
        "published_at": sn.get("publishedAt"),
        "channel_id": sn.get("channelId"),
        "privacy": status.get("privacyStatus"),
        "thumbnail": ((sn.get("thumbnails") or {}).get("high") or {}).get("url")
            or ((sn.get("thumbnails") or {}).get("medium") or {}).get("url"),
        "source": "youtube-data-api-v3",
    }


def video_age_hours(published_at: Optional[str]) -> Optional[float]:
    """Hours since publish, or None if unknown."""
    if not published_at:
        return None
    import datetime, re
    s = str(published_at).strip()
    pub = None
    m = re.match(r"^(\d{4})(\d{2})(\d{2})$", s[:8]) if len(s) >= 8 and s[4:5].isdigit() else None
    if m:
        try:
            pub = datetime.datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)), tzinfo=datetime.timezone.utc)
        except Exception:
            pub = None
    if pub is None:
        m2 = re.match(r"(\d{4})-(\d{2})-(\d{2})[T ]?(\d{2})?:?(\d{2})?:?(\d{2})?", s)
        if m2:
            try:
                pub = datetime.datetime(
                    int(m2.group(1)), int(m2.group(2)), int(m2.group(3)),
                    int(m2.group(4) or 0), int(m2.group(5) or 0), int(m2.group(6) or 0),
                    tzinfo=datetime.timezone.utc,
                )
            except Exception:
                pub = None
    if pub is None:
        try:
            pub = datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))
            if pub.tzinfo is None:
                pub = pub.replace(tzinfo=datetime.timezone.utc)
        except Exception:
            return None
    now = datetime.datetime.now(datetime.timezone.utc)
    return max(0.0, (now - pub.astimezone(datetime.timezone.utc)).total_seconds() / 3600.0)


def list_channel_videos(limit: int = 50, page_token: Optional[str] = None) -> dict:
    """
    List videos from the authorized channel's uploads playlist (OAuth).
    Returns {items: [...], next_page_token}.
    Each item: video_id, title, description, published_at, thumbnail, duration_sec, kind guess.
    """
    tok = load_token() or {}
    uploads = tok.get("uploads_playlist_id")
    if not uploads:
        ch = fetch_mine_channel()
        uploads = ch.get("uploads_playlist_id")
        if ch:
            tok.update(ch)
            save_token(tok)
    if not uploads:
        raise RuntimeError("Нет uploads playlist — переподключи OAuth")

    params = {
        "part": "snippet,contentDetails",
        "playlistId": uploads,
        "maxResults": min(50, max(1, int(limit))),
    }
    if page_token:
        params["pageToken"] = page_token
    url = "https://www.googleapis.com/youtube/v3/playlistItems?" + urllib.parse.urlencode(params)
    data = _http_json("GET", url, headers=_auth_headers())

    # durations need videos.list
    ids = []
    prelim = []
    for it in data.get("items") or []:
        sn = it.get("snippet") or {}
        res = sn.get("resourceId") or {}
        vid = res.get("videoId")
        if not vid:
            continue
        ids.append(vid)
        thumbs = sn.get("thumbnails") or {}
        thumb = (thumbs.get("high") or thumbs.get("medium") or thumbs.get("default") or {}).get("url")
        prelim.append({
            "video_id": vid,
            "title": sn.get("title") or "",
            "description": (sn.get("description") or "")[:2000],
            "published_at": sn.get("publishedAt"),
            "thumbnail": thumb,
            "channel_title": sn.get("channelTitle"),
            "url": f"https://www.youtube.com/watch?v={vid}",
        })

    duration_map: dict[str, float] = {}
    if ids:
        # batch videos.list for duration + stats
        vparams = {
            "part": "contentDetails,statistics,snippet",
            "id": ",".join(ids[:50]),
        }
        vurl = "https://www.googleapis.com/youtube/v3/videos?" + urllib.parse.urlencode(vparams)
        try:
            vdata = _http_json("GET", vurl, headers=_auth_headers())
            for vit in vdata.get("items") or []:
                vid = vit.get("id")
                cd = vit.get("contentDetails") or {}
                duration_map[vid] = {
                    "duration_sec": _parse_iso_duration(cd.get("duration")),
                    "views": int(((vit.get("statistics") or {}).get("viewCount") or 0)),
                    "likes": int(((vit.get("statistics") or {}).get("likeCount") or 0)),
                    "comments": int(((vit.get("statistics") or {}).get("commentCount") or 0)),
                }
        except Exception:
            pass

    out_items = []
    for p in prelim:
        extra = duration_map.get(p["video_id"]) or {}
        dur = extra.get("duration_sec")
        # Shorts heuristic: <= 60s or title/url patterns later
        kind = "shorts" if (dur is not None and dur <= 60) else "long"
        p["duration_sec"] = dur
        p["views"] = extra.get("views")
        p["likes"] = extra.get("likes")
        p["comments"] = extra.get("comments")
        p["kind"] = kind
        out_items.append(p)

    return {
        "items": out_items,
        "next_page_token": data.get("nextPageToken"),
        "total": len(out_items),
    }


def list_all_channel_videos(max_videos: int = 200) -> list[dict]:
    """Paginate uploads playlist up to max_videos."""
    all_items: list[dict] = []
    token = None
    while len(all_items) < max_videos:
        batch = min(50, max_videos - len(all_items))
        page = list_channel_videos(limit=batch, page_token=token)
        items = page.get("items") or []
        if not items:
            break
        all_items.extend(items)
        token = page.get("next_page_token")
        if not token:
            break
    return all_items[:max_videos]


def _parse_iso_duration(s: Optional[str]) -> Optional[float]:
    """Parse YouTube ISO-8601 duration PT#H#M#S → seconds."""
    if not s or not isinstance(s, str):
        return None
    import re
    m = re.match(
        r"^PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)(?:\.\d+)?S)?$",
        s.strip(),
    )
    if not m:
        return None
    h = int(m.group(1) or 0)
    mi = int(m.group(2) or 0)
    sec = float(m.group(3) or 0)
    return h * 3600 + mi * 60 + sec


def analytics_report(
    video_id: str,
    start_date: str,
    end_date: str,
    metrics: Optional[list[str]] = None,
    *,
    use_mine: bool = True,
) -> dict:
    """
    YouTube Analytics API v2 report for one video.

    Canonical channel report (Google docs):
      ids=channel==MINE  (or channel==CHANNEL_ID)
      metrics=views,estimatedMinutesWatched,averageViewDuration,averageViewPercentage
      filters=video==VIDEO_ID
      no dimensions  → one aggregate row for the date range
    """
    tok = load_token() or {}
    channel_id = tok.get("channel_id")
    if not channel_id:
        ch = fetch_mine_channel()
        channel_id = ch.get("channel_id")
        if channel_id:
            tok.update(ch)
            save_token(tok)

    metrics = metrics or [
        "views",
        "estimatedMinutesWatched",
        "averageViewDuration",
        "averageViewPercentage",
    ]

    # Prefer channel==MINE — works with the authorized channel without stale channel_id
    ids_value = "channel==MINE" if use_mine else f"channel=={channel_id}"
    if not use_mine and not channel_id:
        raise RuntimeError("Не удалось получить channel_id")

    params = {
        "ids": ids_value,
        "startDate": start_date,
        "endDate": end_date,
        "metrics": ",".join(metrics),
        "filters": f"video=={video_id}",
    }
    url = "https://youtubeanalytics.googleapis.com/v2/reports?" + urllib.parse.urlencode(params)
    return _http_json("GET", url, headers=_auth_headers())


def parse_report(report: dict) -> dict[str, Any]:
    """Flatten single-row analytics report into a dict."""
    headers = [h.get("name") for h in (report.get("columnHeaders") or [])]
    rows = report.get("rows") or []
    if not rows:
        return {"empty": True, "headers": headers, "row_count": 0}
    row = rows[0]
    out: dict[str, Any] = {"row_count": len(rows)}
    for i, name in enumerate(headers):
        if i < len(row):
            out[name] = row[i]
    return out


def _num(v):
    if v is None or v == "":
        return None
    try:
        return float(v)
    except Exception:
        return None



def audience_retention(video_id: str, days: int = 28) -> dict:
    """
    Retention curve via Analytics API:
      dimensions=elapsedVideoTimeRatio
      metrics=audienceWatchRatio,relativeRetentionPerformance
      filters=video==ID

    Early points approximate how many still watching after start
    (proxy for Shorts hook / early swipe loss — not Studio «Viewed vs swiped»).
    """
    import datetime
    end = datetime.date.today()
    start = end - datetime.timedelta(days=max(1, days))
    params = {
        "ids": "channel==MINE",
        "startDate": start.isoformat(),
        "endDate": end.isoformat(),
        "dimensions": "elapsedVideoTimeRatio",
        "metrics": "audienceWatchRatio,relativeRetentionPerformance",
        "filters": f"video=={video_id}",
        "sort": "elapsedVideoTimeRatio",
    }
    url = "https://youtubeanalytics.googleapis.com/v2/reports?" + urllib.parse.urlencode(params)
    try:
        rep = _http_json("GET", url, headers=_auth_headers())
    except Exception as e:
        return {"ok": False, "error": str(e)[:300]}

    headers = [h.get("name") for h in (rep.get("columnHeaders") or [])]
    rows = rep.get("rows") or []
    points = []
    for row in rows:
        d = {}
        for i, name in enumerate(headers):
            if i < len(row):
                d[name] = row[i]
        try:
            points.append({
                "elapsed": float(d.get("elapsedVideoTimeRatio") or 0),
                "watch_ratio": _num(d.get("audienceWatchRatio")),
                "relative": _num(d.get("relativeRetentionPerformance")),
            })
        except Exception:
            continue
    points.sort(key=lambda x: x["elapsed"])

    # Early-drop estimates from first buckets
    early = None
    at_10 = None
    at_25 = None
    at_50 = None
    for pt in points:
        e, w = pt["elapsed"], pt["watch_ratio"]
        if w is None:
            continue
        if early is None and e <= 0.05:
            early = w
        if at_10 is None and e >= 0.10:
            at_10 = w
        if at_25 is None and e >= 0.25:
            at_25 = w
        if at_50 is None and e >= 0.50:
            at_50 = w

    # If first point is near 1.0 and drops, early_swipe_proxy = 1 - early_watch
    early_swipe = None
    if early is not None:
        # audienceWatchRatio can be >1 on Shorts (loops); clamp
        early_swipe = round(max(0.0, min(100.0, (1.0 - min(early, 1.0)) * 100.0)), 2)

    return {
        "ok": True,
        "points": points[:120],
        "early_watch_ratio": early,
        "at_10_pct": at_10,
        "at_25_pct": at_25,
        "at_50_pct": at_50,
        "early_drop_pct": early_swipe,  # rough % gone by ~first bucket
        "range_start": start.isoformat(),
        "range_end": end.isoformat(),
    }


# ---------- YouTube Reporting API (bulk) for thumbnail impressions ----------

def _reporting_headers() -> dict:
    return _auth_headers()


def reporting_list_report_types() -> list:
    url = "https://youtubereporting.googleapis.com/v1/reportTypes"
    data = _http_json("GET", url, headers=_reporting_headers())
    return data.get("reportTypes") or []


def reporting_list_jobs() -> list:
    url = "https://youtubereporting.googleapis.com/v1/jobs"
    data = _http_json("GET", url, headers=_reporting_headers())
    return data.get("jobs") or []


def reporting_ensure_reach_job() -> dict:
    """
    Ensure a bulk job for channel_reach_basic_a1 exists
    (video_thumbnail_impressions + CTR per video/day).
    """
    report_type = "channel_reach_basic_a1"
    jobs = reporting_list_jobs()
    for j in jobs:
        if j.get("reportTypeId") == report_type:
            return {"ok": True, "job": j, "created": False}
    # create
    body = json.dumps({
        "reportTypeId": report_type,
        "name": "uTeam-Studio reach basic",
    }).encode("utf-8")
    req = urllib.request.Request(
        "https://youtubereporting.googleapis.com/v1/jobs",
        data=body,
        headers={**_reporting_headers(), "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            job = json.loads(resp.read().decode("utf-8"))
        return {"ok": True, "job": job, "created": True}
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", errors="replace")[:400]
        return {"ok": False, "error": f"HTTP {e.code}: {err}"}


def reporting_list_reports(job_id: str, page_size: int = 25) -> list:
    q = urllib.parse.urlencode({"pageSize": page_size})
    url = f"https://youtubereporting.googleapis.com/v1/jobs/{job_id}/reports?{q}"
    data = _http_json("GET", url, headers=_reporting_headers())
    return data.get("reports") or []


def reporting_download_report_csv(download_url: str) -> str:
    # downloadUrl already includes auth? Docs: use Authorization header
    req = urllib.request.Request(download_url, headers=_reporting_headers())
    with urllib.request.urlopen(req, timeout=120) as resp:
        return resp.read().decode("utf-8", errors="replace")


def video_impressions_from_reporting(video_id: str, days: int = 28) -> dict:
    """
    Sum thumbnail impressions + average CTR from bulk reach reports.
    First call creates the job; reports appear after YouTube generates daily files
    (often next day). Until then returns pending.
    """
    import datetime
    import csv
    import io

    ens = reporting_ensure_reach_job()
    if not ens.get("ok"):
        return {"ok": False, "error": ens.get("error"), "pending": False}
    job = ens["job"]
    job_id = job.get("id")
    if not job_id:
        return {"ok": False, "error": "no job id"}

    reports = reporting_list_reports(job_id)
    if not reports:
        return {
            "ok": False,
            "pending": True,
            "created_job": ens.get("created"),
            "error": (
                "Reach job создан/есть, но daily CSV ещё нет. "
                "YouTube отдаёт bulk-отчёты с задержкой (часто на следующий день). "
                "Повтори синк завтра."
            ),
            "job_id": job_id,
        }

    end = datetime.date.today()
    start = end - datetime.timedelta(days=max(1, days))
    # Prefer newest reports; each report is one day
    reports_sorted = sorted(reports, key=lambda r: r.get("startTime") or "", reverse=True)

    total_impr = 0
    ctr_weighted = 0.0
    days_used = 0
    samples = []

    for rep in reports_sorted[:40]:
        # startTime is report day
        st = (rep.get("startTime") or "")[:10]
        try:
            d = datetime.date.fromisoformat(st)
        except Exception:
            continue
        if d < start or d > end:
            continue
        url = rep.get("downloadUrl")
        if not url:
            continue
        try:
            csv_text = reporting_download_report_csv(url)
        except Exception as e:
            continue
        # CSV columns typically: date,channel_id,video_id,video_thumbnail_impressions,video_thumbnail_impressions_ctr
        reader = csv.DictReader(io.StringIO(csv_text))
        for row in reader:
            vid = row.get("video_id") or row.get("video") or ""
            if vid != video_id:
                continue
            try:
                impr = int(float(row.get("video_thumbnail_impressions") or 0))
            except Exception:
                impr = 0
            try:
                ctr = float(row.get("video_thumbnail_impressions_ctr") or 0)
            except Exception:
                ctr = 0.0
            # CTR in bulk reports is often a ratio 0–1
            if ctr > 1.5:
                ctr = ctr / 100.0
            total_impr += impr
            ctr_weighted += ctr * impr
            days_used += 1
            samples.append({"date": st, "impressions": impr, "ctr": ctr})

    if days_used == 0 and not samples:
        return {
            "ok": False,
            "pending": True,
            "error": "В bulk CSV нет строк по этому video_id за период (или отчёты ещё пустые).",
            "job_id": job_id,
        }

    avg_ctr = (ctr_weighted / total_impr) if total_impr > 0 else None
    clicks_est = int(round(total_impr * avg_ctr)) if avg_ctr is not None else None

    return {
        "ok": True,
        "pending": False,
        "impressions": total_impr,
        "impressions_ctr": round(avg_ctr * 100, 3) if avg_ctr is not None else None,  # percent
        "clicks_est": clicks_est,
        "days_with_data": days_used,
        "job_id": job_id,
        "samples": samples[:10],
        "range_start": start.isoformat(),
        "range_end": end.isoformat(),
        "source": "youtube-reporting-api:channel_reach_basic_a1",
    }


def video_studio_stats(video_id: str, days: int = 28, published_at: Optional[str] = None) -> dict:
    """
    Watch metrics for the last `days` days (default 28).

    For brand-new uploads Analytics often has no rows for 1–3 days even when
    public viewCount is already > 0. We clamp the window to publish date and
    try publish→today as a second pass.
    """
    import datetime
    import re

    end = datetime.date.today()
    primary_days = max(1, int(days or 28))
    start_d = end - datetime.timedelta(days=primary_days)

    pub_date = None
    if published_at:
        s = str(published_at).strip()
        # 20261119 or 2026-11-19 or ISO
        m = re.match(r"^(\d{4})(\d{2})(\d{2})$", s[:8]) if len(s) >= 8 and s[4:5].isdigit() else None
        if m:
            try:
                pub_date = datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
            except Exception:
                pub_date = None
        if pub_date is None:
            m2 = re.match(r"(\d{4})-(\d{2})-(\d{2})", s)
            if m2:
                try:
                    pub_date = datetime.date(int(m2.group(1)), int(m2.group(2)), int(m2.group(3)))
                except Exception:
                    pub_date = None
    if pub_date and pub_date > start_d:
        start_d = pub_date
    if pub_date and pub_date > end:
        # clock skew / future publish label — still query last day
        start_d = end

    metric_sets = [
        ["views", "engagedViews", "estimatedMinutesWatched", "averageViewDuration", "averageViewPercentage"],
        ["views", "engagedViews", "averageViewDuration", "averageViewPercentage"],
        ["views", "engagedViews", "estimatedMinutesWatched", "averageViewDuration"],
        ["views", "engagedViews"],
        ["views", "estimatedMinutesWatched", "averageViewDuration", "averageViewPercentage"],
        ["averageViewDuration", "averageViewPercentage"],
    ]

    errors: list[str] = []
    parsed: Optional[dict] = None
    used_metrics: Optional[list[str]] = None
    used_ids = None
    best_score = -1

    def _score(p: dict) -> int:
        s = 0
        if p.get("averageViewDuration") is not None:
            s += 4
        if p.get("averageViewPercentage") is not None:
            s += 3
        if p.get("estimatedMinutesWatched") is not None:
            s += 2
        if p.get("engagedViews") is not None:
            s += 2
        if p.get("views") is not None:
            s += 1
        return s

    for use_mine in (True, False):
        for metrics in metric_sets:
            try:
                rep = analytics_report(
                    video_id,
                    start_d.isoformat(),
                    end.isoformat(),
                    metrics=metrics,
                    use_mine=use_mine,
                )
                p = parse_report(rep)
                if p.get("empty"):
                    errors.append(f"empty {'MINE' if use_mine else 'id'} {metrics[0]}…")
                    continue
                sc = _score(p)
                if sc > best_score:
                    best_score = sc
                    parsed = p
                    used_metrics = metrics
                    used_ids = "channel==MINE" if use_mine else "channel==ID"
                # Prefer a result that already has averageViewDuration
                if p.get("averageViewDuration") is not None:
                    break
            except Exception as e:
                msg = str(e)
                errors.append(msg[:180])
                if "401" in msg or "invalid_grant" in msg.lower():
                    return {"ok": False, "error": msg, "video_id": video_id}
                if "403" in msg:
                    return {
                        "ok": False,
                        "error": msg,
                        "video_id": video_id,
                        "hint": "Переподключи OAuth с scope yt-analytics.readonly (владелец канала).",
                    }
        if parsed and parsed.get("averageViewDuration") is not None:
            break

    # Second pass for very new videos: publish day → today (or last 3 days)
    if (not parsed or (
        parsed.get("engagedViews") is None
        and parsed.get("averageViewDuration") is None
    )) and pub_date is not None:
        alt_starts = []
        alt_starts.append(pub_date)
        alt_starts.append(end - datetime.timedelta(days=3))
        alt_starts.append(end - datetime.timedelta(days=1))
        for alt_start in alt_starts:
            if alt_start > end:
                continue
            if alt_start < pub_date:
                alt_start = pub_date
            for use_mine in (True, False):
                for metrics in metric_sets[:3]:
                    try:
                        rep = analytics_report(
                            video_id,
                            alt_start.isoformat(),
                            end.isoformat(),
                            metrics=metrics,
                            use_mine=use_mine,
                        )
                        p = parse_report(rep)
                        if p.get("empty"):
                            continue
                        sc = _score(p)
                        if parsed is None or sc > best_score:
                            best_score = sc
                            parsed = p
                            used_metrics = metrics
                            used_ids = "channel==MINE" if use_mine else "channel==ID"
                            start_d = alt_start
                        if p.get("engagedViews") is not None or p.get("averageViewDuration") is not None:
                            break
                    except Exception as e:
                        errors.append(str(e)[:120])
                if parsed and (parsed.get("engagedViews") is not None or parsed.get("averageViewDuration") is not None):
                    break
            if parsed and (parsed.get("engagedViews") is not None or parsed.get("averageViewDuration") is not None):
                break

    if not parsed:
        age_hint = ""
        if pub_date is not None:
            age = (end - pub_date).days
            if age <= 3:
                age_hint = f" Ролик загружен ~{age} дн. назад — у Studio «Реакция зрителей» часто есть раньше, чем в Analytics API (лаг 1–3 дня)."
        return {
            "ok": False,
            "error": errors[-1] if errors else "Analytics API: пустой ответ за период",
            "video_id": video_id,
            "range_start": start_d.isoformat(),
            "range_end": end.isoformat(),
            "published_at": published_at,
            "attempts": errors[-10:],
            "hint": (
                "Для свежих Shorts engagedViews/AVD в API могут быть пустыми,"
                " хотя в Studio уже видна «Реакция зрителей»."
                + age_hint
            ),
        }

    avg_dur = _num(parsed.get("averageViewDuration"))
    avg_pct = _num(parsed.get("averageViewPercentage"))
    minutes = _num(parsed.get("estimatedMinutesWatched"))
    views = _num(parsed.get("views"))
    engaged = _num(parsed.get("engagedViews"))

    # Fallbacks for Shorts: Studio AVD is among those who stayed (engaged).
    # minutes/engaged is closer than minutes/views when many swipe away.
    if avg_dur is None and minutes is not None:
        if engaged and engaged > 0:
            avg_dur = (minutes * 60.0) / engaged
        elif views and views > 0:
            avg_dur = (minutes * 60.0) / views

    # % досмотра: if API omitted it but we know duration of video is unknown here —
    # leave avg_pct; can be filled later when duration known in youtube_data layer

    # Shorts proxy: stayed vs swiped from engagedViews / views
    stayed_pct = None
    swipe_away_pct = None
    if engaged is not None and views is not None and views > 0:
        stayed_pct = round(min(100.0, max(0.0, (engaged / views) * 100.0)), 2)
        swipe_away_pct = round(max(0.0, 100.0 - stayed_pct), 2)
    elif avg_pct is not None:
        # weaker fallback
        swipe_away_pct = round(max(0.0, 100.0 - float(avg_pct)), 2)
        stayed_pct = round(float(avg_pct), 2)

    out = {
        "ok": True,
        "video_id": video_id,
        "range_start": start_d.isoformat(),
        "range_end": end.isoformat(),
        "range_label": f"{primary_days}d",
        "ids": used_ids,
        "views": int(views) if views is not None else None,
        "engaged_views": int(engaged) if engaged is not None else None,
        "likes": parsed.get("likes"),
        "comments": parsed.get("comments"),
        "shares": parsed.get("shares"),
        "estimated_minutes_watched": minutes,
        "average_view_duration_sec": avg_dur,
        "average_view_percentage": avg_pct,
        "stayed_pct": stayed_pct,
        "swipe_away_pct": swipe_away_pct,
        "impressions": None,
        "impressions_ctr": None,
        "clicks_est": None,
        "raw": parsed,
        "source": "youtube-analytics-api",
        "metrics_used": used_metrics,
        "notes": {
            "swipe_away": (
                "proxy engagedViews/views; доп. early_drop из retention curve"
            ),
            "impressions": (
                "thumbnail impressions из Reporting API bulk channel_reach_basic_a1"
            ),
        },
    }

    # Alt 1: retention curve → early drop for Shorts
    try:
        ret = audience_retention(video_id, days=primary_days)
        out["retention"] = {
            "ok": ret.get("ok"),
            "early_drop_pct": ret.get("early_drop_pct"),
            "early_watch_ratio": ret.get("early_watch_ratio"),
            "at_10_pct": ret.get("at_10_pct"),
            "at_25_pct": ret.get("at_25_pct"),
            "at_50_pct": ret.get("at_50_pct"),
            "error": ret.get("error"),
        }
        if out.get("swipe_away_pct") is None and ret.get("early_drop_pct") is not None:
            out["swipe_away_pct"] = ret["early_drop_pct"]
            out["swipe_away_source"] = "retention_early_drop"
        if out.get("stayed_pct") is None and ret.get("early_watch_ratio") is not None:
            try:
                out["stayed_pct"] = round(min(100.0, max(0.0, float(ret["early_watch_ratio"]) * 100.0)), 2)
            except Exception:
                pass
    except Exception as e:
        out["retention"] = {"ok": False, "error": str(e)[:200]}

    # Alt 2: bulk Reporting API impressions (long-form reach)
    try:
        impr = video_impressions_from_reporting(video_id, days=primary_days)
        out["reporting_reach"] = {
            "ok": impr.get("ok"),
            "pending": impr.get("pending"),
            "error": impr.get("error"),
            "job_id": impr.get("job_id"),
            "days_with_data": impr.get("days_with_data"),
        }
        if impr.get("ok"):
            out["impressions"] = impr.get("impressions")
            out["impressions_ctr"] = impr.get("impressions_ctr")
            out["clicks_est"] = impr.get("clicks_est")
    except Exception as e:
        out["reporting_reach"] = {"ok": False, "error": str(e)[:200]}

    return out
