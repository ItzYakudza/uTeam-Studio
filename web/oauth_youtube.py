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
    return {
        "channel_id": item.get("id"),
        "channel_title": sn.get("title"),
        "channel_thumb": ((sn.get("thumbnails") or {}).get("default") or {}).get("url"),
    }


def analytics_report(
    video_id: str,
    start_date: str,
    end_date: str,
    metrics: Optional[list[str]] = None,
) -> dict:
    """
    YouTube Analytics API report for one video.
    dates: YYYY-MM-DD
    """
    tok = load_token() or {}
    channel_id = tok.get("channel_id")
    if not channel_id:
        ch = fetch_mine_channel()
        channel_id = ch.get("channel_id")
        if channel_id:
            tok.update(ch)
            save_token(tok)
    if not channel_id:
        raise RuntimeError("Не удалось получить channel_id")

    metrics = metrics or [
        "views",
        "likes",
        "comments",
        "shares",
        "estimatedMinutesWatched",
        "averageViewDuration",
        "averageViewPercentage",
        "subscribersGained",
        "subscribersLost",
        "videosAddedToPlaylists",
        "videosRemovedFromPlaylists",
    ]
    params = {
        "ids": f"channel=={channel_id}",
        "startDate": start_date,
        "endDate": end_date,
        "metrics": ",".join(metrics),
        "dimensions": "video",
        "filters": f"video=={video_id}",
    }
    url = "https://youtubeanalytics.googleapis.com/v2/reports?" + urllib.parse.urlencode(params)
    return _http_json("GET", url, headers=_auth_headers())


def parse_report(report: dict) -> dict[str, Any]:
    """Flatten single-row analytics report into a dict."""
    headers = [h.get("name") for h in (report.get("columnHeaders") or [])]
    rows = report.get("rows") or []
    if not rows:
        return {"empty": True, "headers": headers}
    row = rows[0]
    out = {}
    for i, name in enumerate(headers):
        if i < len(row):
            out[name] = row[i]
    return out


def video_studio_stats(video_id: str, days: int = 90) -> dict:
    """High-level stats for one video over the last N days (+ lifetime-ish window)."""
    import datetime

    end = datetime.date.today()
    start = end - datetime.timedelta(days=max(1, days))
    # also try from 2010 for cumulative-ish (API returns range totals)
    try:
        rep = analytics_report(video_id, start.isoformat(), end.isoformat())
        parsed = parse_report(rep)
    except Exception as e:
        return {"ok": False, "error": str(e), "video_id": video_id}

    avg_dur = parsed.get("averageViewDuration")  # seconds
    avg_pct = parsed.get("averageViewPercentage")
    minutes = parsed.get("estimatedMinutesWatched")
    views = parsed.get("views")
    out = {
        "ok": True,
        "video_id": video_id,
        "range_start": start.isoformat(),
        "range_end": end.isoformat(),
        "views": views,
        "likes": parsed.get("likes"),
        "comments": parsed.get("comments"),
        "shares": parsed.get("shares"),
        "estimated_minutes_watched": minutes,
        "average_view_duration_sec": avg_dur,
        "average_view_percentage": avg_pct,
        "subscribers_gained": parsed.get("subscribersGained"),
        "subscribers_lost": parsed.get("subscribersLost"),
        "playlist_adds": parsed.get("videosAddedToPlaylists"),
        "playlist_removes": parsed.get("videosRemovedFromPlaylists"),
        "raw": parsed,
        "source": "youtube-analytics-api",
    }
    # approximate swipe-away / non-retention
    if avg_pct is not None:
        try:
            out["swipe_away_pct"] = round(100.0 - float(avg_pct), 2)
        except Exception:
            pass
    return out
