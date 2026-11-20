"""Background YouTube sync worker.

When OAuth is connected:
  - lists channel uploads via YouTube Data API
  - creates local episode folders + youtube_data for videos missing in storage
  - syncs stats (public + Studio analytics) for all linked episodes
Without OAuth: only syncs episodes that already have youtube_id / url (yt-dlp).
"""
from __future__ import annotations

import threading
import time
import traceback
from pathlib import Path
from typing import Optional

import db as D
import youtube_data as YD

_lock = threading.Lock()
_thread: Optional[threading.Thread] = None
_stop = threading.Event()
_state = {
    "running": False,
    "last_run": None,
    "last_result": None,
    "interval_sec": 3600,
    "oauth_connected": False,
}


def get_state() -> dict:
    return dict(_state)


def _oauth_connected() -> bool:
    try:
        import oauth_youtube as OYT
        return bool(OYT.status().get("connected"))
    except Exception:
        return False


def _resolve_local_channel_for_oauth() -> Optional[dict]:
    """Pick local channel for OAuth imports."""
    try:
        import oauth_youtube as OYT
        tok = OYT.load_token() or {}
        yt_id = (tok.get("channel_id") or "").strip()
        yt_title = (tok.get("channel_title") or "").strip().lower()
    except Exception:
        yt_id, yt_title = "", ""

    channels = D.list_channels()
    if not channels:
        return None

    for ch in channels:
        url = (ch.get("youtube_channel_url") or "").lower()
        name = (ch.get("name") or "").lower()
        if yt_id and yt_id.lower() in url:
            return ch
        if yt_title and yt_title in name:
            return ch
        if yt_title and yt_title in url:
            return ch

    return channels[0]


def import_from_oauth(max_videos: int = 100) -> dict:
    """Pull channel videos via OAuth; create folders for missing ones; sync stats."""
    import oauth_youtube as OYT

    if not OYT.status().get("connected"):
        return {"ok": False, "error": "OAuth not connected", "created": 0, "synced": 0}

    try:
        ch_meta = OYT.fetch_mine_channel()
        tok = OYT.load_token() or {}
        tok.update(ch_meta)
        OYT.save_token(tok)
    except Exception as e:
        return {"ok": False, "error": f"channel meta: {e}", "created": 0, "synced": 0}

    local_ch = _resolve_local_channel_for_oauth()
    if not local_ch:
        return {"ok": False, "error": "Нет локального канала — создай канал в UI", "created": 0, "synced": 0}

    # Clean accidental duplicates from earlier imports (same youtube_id)
    try:
        dedupe_info = D.dedupe_youtube_episodes(delete_folders=True)
    except Exception:
        dedupe_info = None

    try:
        videos = OYT.list_all_channel_videos(max_videos=max_videos)
    except Exception as e:
        return {"ok": False, "error": str(e), "created": 0, "synced": 0}

    # snapshot existing youtube ids before import
    existing_ids = {
        ep.get("youtube_id")
        for ep in D.list_episodes()
        if ep.get("youtube_id")
    }

    created = []
    synced = []
    failed = []

    for v in videos:
        vid = v.get("video_id")
        if not vid:
            continue
        try:
            matched = D.find_episode_for_youtube_video(
                vid, title=v.get("title") or "", channel_id=local_ch["id"]
            )
            ep = D.ensure_youtube_episode(
                channel_id=local_ch["id"],
                video_id=vid,
                title=v.get("title") or vid,
                kind=v.get("kind") or "long",
                duration_sec=v.get("duration_sec"),
                youtube_url=v.get("url"),
                create_if_missing=True,
            )
            if not ep:
                failed.append({"video_id": vid, "error": "no episode"})
                continue

            result = YD.sync_episode_folder(Path(ep["disk_path"]), vid)
            if result.get("available") and result.get("stats"):
                s = result["stats"]
                D.upsert_video_stats(
                    ep["id"],
                    s.get("date") or D._now()[:10],
                    views=s.get("views") or v.get("views") or 0,
                    likes=s.get("likes") or v.get("likes") or 0,
                    comments=s.get("comments") or v.get("comments") or 0,
                    shares=s.get("shares") or 0,
                    source=s.get("source") or "youtube-oauth",
                    note="oauth-import",
                )
            row = {
                "episode_id": ep["id"],
                "video_id": vid,
                "title": ep.get("title"),
                "views": (result.get("stats") or {}).get("views") or v.get("views"),
            }
            if matched is None:
                created.append(row)  # brand-new local folder
            else:
                synced.append(row)   # updated / linked existing
            existing_ids.add(vid)
        except Exception as e:
            failed.append({"video_id": vid, "error": str(e)[:200]})

    return {
        "ok": True,
        "channel_id": local_ch["id"],
        "channel_name": local_ch.get("name"),
        "yt_videos": len(videos),
        "created": len(created),
        "synced": len(synced),
        "failed": len(failed),
        "created_items": created[:30],
        "failures": failed[:20],
        "deduped": dedupe_info,
    }


def sync_one(ep: dict) -> dict:
    ref = ep.get("youtube_id") or ep.get("youtube_url")
    if not ref:
        return {"episode_id": ep["id"], "skipped": True, "reason": "no link"}
    ep_path = ep.get("disk_path")
    if not ep_path:
        return {"episode_id": ep["id"], "skipped": True, "reason": "no path"}
    try:
        result = YD.sync_episode_folder(ep_path, ref)
        if result.get("available") and result.get("stats"):
            s = result["stats"]
            D.upsert_video_stats(
                ep["id"],
                s.get("date") or D._now()[:10],
                views=s.get("views") or 0,
                likes=s.get("likes") or 0,
                comments=s.get("comments") or 0,
                shares=s.get("shares") or 0,
                source=s.get("source") or "youtube",
                note="worker",
            )
            D.update_episode(
                ep["id"],
                youtube_id=result["meta"].get("video_id"),
                youtube_url=result["meta"].get("url"),
                duration_sec=result["meta"].get("duration_sec"),
            )
        elif result.get("available") is False:
            YD.mark_unavailable(ep_path, result.get("status", {}).get("error") or "unavailable")
        return {
            "episode_id": ep["id"],
            "ok": result.get("ok"),
            "available": result.get("available"),
            "views": (result.get("stats") or {}).get("views"),
            "source": (result.get("stats") or {}).get("source"),
        }
    except Exception as e:
        return {"episode_id": ep["id"], "ok": False, "error": str(e)}


def sync_all() -> dict:
    with _lock:
        oauth = _oauth_connected()
        _state["oauth_connected"] = oauth

        import_result = None
        if oauth:
            try:
                import_result = import_from_oauth(max_videos=100)
            except Exception as e:
                import_result = {"ok": False, "error": str(e)}

        eps = D.list_episodes()
        results = []
        for ep in eps:
            if ep.get("youtube_id") or ep.get("youtube_url"):
                results.append(sync_one(ep))
            else:
                results.append({"episode_id": ep["id"], "skipped": True, "reason": "no link"})

        summary = {
            "total": len(results),
            "synced": sum(1 for r in results if r.get("ok")),
            "skipped": sum(1 for r in results if r.get("skipped")),
            "failed": sum(1 for r in results if r.get("ok") is False),
            "oauth": oauth,
            "import": import_result,
            "results": results,
            "ts": D._now(),
        }
        _state["last_run"] = summary["ts"]
        _state["last_result"] = {
            k: summary[k]
            for k in ("total", "synced", "skipped", "failed", "oauth", "import", "ts")
            if k in summary
        }
        return summary


def _pick_interval(base: int) -> int:
    if _oauth_connected():
        return min(base, 900)
    return base


def _loop(interval: int):
    _state["running"] = True
    _state["interval_sec"] = interval
    time.sleep(5)
    while not _stop.is_set():
        try:
            sync_all()
        except Exception:
            _state["last_result"] = {"error": traceback.format_exc()[-500:]}
        wait = _pick_interval(interval)
        _state["interval_sec"] = wait
        _stop.wait(wait)
    _state["running"] = False


def start(interval_sec: int = 3600):
    global _thread
    if _thread and _thread.is_alive():
        return
    _stop.clear()
    _thread = threading.Thread(target=_loop, args=(interval_sec,), daemon=True, name="yt-worker")
    _thread.start()


def stop():
    _stop.set()
