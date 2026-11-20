"""Background hourly YouTube sync worker."""
from __future__ import annotations

import threading
import time
import traceback
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
}


def get_state() -> dict:
    return dict(_state)


def sync_one(ep: dict) -> dict:
    ref = ep.get("youtube_id") or ep.get("youtube_url")
    if not ref:
        return {"episode_id": ep["id"], "skipped": True, "reason": "no link"}
    ep_path = ep.get("disk_path")
    if not ep_path:
        return {"episode_id": ep["id"], "skipped": True, "reason": "no path"}
    try:
        result = YD.sync_episode_folder(ep_path, ref)
        # mirror into central DB stats if available
        if result.get("available") and result.get("stats"):
            s = result["stats"]
            D.upsert_video_stats(
                ep["id"],
                s.get("date") or D._now()[:10],
                views=s.get("views") or 0,
                likes=s.get("likes") or 0,
                comments=s.get("comments") or 0,
                source=s.get("source") or "youtube",
                note="worker",
            )
            D.update_episode(
                ep["id"],
                youtube_id=result["meta"].get("video_id"),
                youtube_url=result["meta"].get("url"),
                duration_sec=result["meta"].get("duration_sec"),
            )
            # optional: align title with YT
            # D.update_episode(ep["id"], title=result["meta"].get("title"))
        elif result.get("available") is False:
            YD.mark_unavailable(ep_path, result.get("status", {}).get("error") or "unavailable")
        return {
            "episode_id": ep["id"],
            "ok": result.get("ok"),
            "available": result.get("available"),
            "views": (result.get("stats") or {}).get("views"),
        }
    except Exception as e:
        return {"episode_id": ep["id"], "ok": False, "error": str(e)}


def sync_all() -> dict:
    with _lock:
        eps = D.list_episodes()
        results = []
        for ep in eps:
            results.append(sync_one(ep))
        summary = {
            "total": len(results),
            "synced": sum(1 for r in results if r.get("ok")),
            "skipped": sum(1 for r in results if r.get("skipped")),
            "failed": sum(1 for r in results if r.get("ok") is False),
            "results": results,
            "ts": D._now(),
        }
        _state["last_run"] = summary["ts"]
        _state["last_result"] = {
            k: summary[k] for k in ("total", "synced", "skipped", "failed", "ts")
        }
        return summary


def _loop(interval: int):
    _state["running"] = True
    _state["interval_sec"] = interval
    # initial delay so server starts cleanly
    time.sleep(5)
    while not _stop.is_set():
        try:
            sync_all()
        except Exception:
            _state["last_result"] = {"error": traceback.format_exc()[-500:]}
        _stop.wait(interval)
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
