"""Two-speed YouTube statistics collector for uTeam-Studio."""
from __future__ import annotations

import asyncio
import json
import logging
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import db as D
import oauth_youtube as OYT
import youtube_data as YD
import worker as W

log = logging.getLogger("uteam.stats")
FAST_INTERVAL_SEC = 15 * 60
SLOW_INTERVAL_SEC = 6 * 60 * 60
STATE_PATH = D.STORAGE / ".stats_sync_state.json"
_state_lock = threading.Lock()
_run_lock = threading.Lock()
_state: dict[str, Any] = {
    "last_sync_at": None, "last_slow_sync_at": None,
    "fast_status": "idle", "slow_status": "idle", "last_error": None,
}


def _now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def _load_state() -> None:
    try:
        saved = json.loads(STATE_PATH.read_text(encoding="utf-8"))
        with _state_lock:
            for key in _state:
                if key in saved:
                    _state[key] = saved[key]
    except Exception:
        pass


def _save_state() -> None:
    try:
        STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with _state_lock:
            data = dict(_state)
        STATE_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        log.exception("Unable to persist sync state")


def get_state() -> dict:
    with _state_lock:
        return dict(_state)


def _episode_rows() -> list[dict]:
    result = []
    for ep in D.list_episodes():
        vid = ep.get("youtube_id")
        if not vid:
            meta = YD.read_json(YD.yt_dir(Path(ep["disk_path"])) / "meta.json") or {}
            vid = meta.get("video_id")
        if vid:
            result.append({**ep, "youtube_id": vid})
    return result


def _read_history(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        try:
            if line.strip():
                rows.append(json.loads(line))
        except Exception:
            continue
    return rows


def _write_history(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")


def _counters(row: dict) -> tuple:
    return tuple(row.get(k) for k in ("views", "likes", "comments"))


def sync_fast() -> dict:
    """Batch-fetch public counters and append a point only when a counter changes."""
    if not OYT.status().get("connected"):
        with _state_lock:
            _state["fast_status"] = "waiting_for_oauth"
        _save_state()
        return {"ok": False, "reason": "OAuth not connected", "synced": 0}
    if not _run_lock.acquire(blocking=False):
        return {"ok": False, "reason": "sync already running", "synced": 0}
    try:
        episodes = _episode_rows()
        by_id = {ep["youtube_id"]: ep for ep in episodes}
        fetched = OYT.fetch_videos_public_stats(list(by_id))
        now = _now()
        changed = 0
        missing = []
        for vid, ep in by_id.items():
            data = fetched.get(vid)
            if not data:
                missing.append(vid)
                continue
            folder = Path(ep["disk_path"])
            yd = YD.ensure_yt_dir(folder)
            latest_path = yd / "latest.json"
            latest = YD.read_json(latest_path) or {}
            history_path = yd / "stats.jsonl"
            history = _read_history(history_path)
            previous = history[-1] if history else latest
            snap = dict(latest)
            snap.update({
                "ts": now, "date": datetime.now().date().isoformat(),
                "video_id": vid,
                "url": latest.get("url") or f"https://www.youtube.com/watch?v={vid}",
                "views": data["views"], "likes": data["likes"], "comments": data["comments"],
                "source": "youtube-data-api-v3", "layer": "fast",
            })
            if _counters(previous or {}) != _counters(snap):
                history.append(snap)
                _write_history(history_path, history)
                changed += 1
            YD.write_json(latest_path, snap)
            status = YD.read_json(yd / "status.json") or {}
            status.update({"available": True, "ok": True, "checked_at": now,
                           "source": "youtube-data-api-v3", "error": None})
            YD.write_json(yd / "status.json", status)
            D.upsert_video_stats(ep["id"], datetime.now().date().isoformat(),
                                 views=data["views"], likes=data["likes"],
                                 comments=data["comments"], source="youtube-data-api-v3",
                                 note="15-minute fast sync")
        success = len(fetched)
        with _state_lock:
            _state["fast_status"] = "ok" if success or not by_id else "no_data"
            if success or not by_id:
                _state["last_sync_at"] = now
            _state["last_error"] = f"No Data API response for {len(missing)} video(s)" if missing else None
        _save_state()
        log.info("Fast sync: %s/%s videos, %s changed", success, len(by_id), changed)
        return {"ok": success > 0 or not by_id, "synced": success, "changed": changed,
                "total": len(by_id), "missing": missing[:30], "last_sync_at": get_state()["last_sync_at"]}
    except Exception as exc:
        with _state_lock:
            _state["fast_status"] = "error"
            _state["last_error"] = str(exc)[:500]
        _save_state()
        log.exception("Fast sync failed")
        return {"ok": False, "error": str(exc)[:300], "synced": 0}
    finally:
        _run_lock.release()


def sync_slow() -> dict:
    """Merge non-empty Analytics and Reporting metrics without clearing old values."""
    if not OYT.status().get("connected"):
        with _state_lock:
            _state["slow_status"] = "waiting_for_oauth"
        _save_state()
        return {"ok": False, "reason": "OAuth not connected", "synced": 0}
    # Discover newly published channel uploads without running the old full,
    # slow per-video sync. The fast collector picks them up on its next cycle.
    try:
        discovery = W.import_from_oauth(max_videos=500, sync_stats=False)
        log.info("Channel discovery: %s created, %s linked", discovery.get("created", 0), discovery.get("synced", 0))
    except Exception as exc:
        log.warning("Channel discovery failed: %s", exc)
    synced = pending = 0
    failed = []
    now = _now()
    mapping = {
        "avg_view_duration_sec": "average_view_duration_sec",
        "average_view_percentage": "average_view_percentage",
        "engaged_views": "engaged_views",
        "impressions_ctr": "impressions_ctr",
        "impressions": "impressions",
        "stayed_pct": "stayed_pct",
        "swipe_away_pct": "swipe_away_pct",
    }
    for ep in _episode_rows():
        vid = ep["youtube_id"]
        folder = Path(ep["disk_path"])
        yd = YD.ensure_yt_dir(folder)
        latest_path = yd / "latest.json"
        latest = YD.read_json(latest_path) or {}
        meta = YD.read_json(yd / "meta.json") or {}
        try:
            studio = OYT.video_studio_stats(vid, days=28, published_at=meta.get("published_at"))
            if not studio.get("ok"):
                pending += 1
                continue
            for target, source in mapping.items():
                if studio.get(source) is not None:
                    latest[target] = studio[source]
            if studio.get("reporting_reach"):
                latest["reporting_reach"] = studio["reporting_reach"]
            latest["studio"] = {**(latest.get("studio") or {}),
                                **{k: v for k, v in studio.items() if v is not None}}
            latest["slow_synced_at"] = now
            latest["layer"] = "fast+deep"
            YD.write_json(latest_path, latest)
            # Enrich the latest existing point; deep-only sync does not create a new point.
            history_path = yd / "stats.jsonl"
            history = _read_history(history_path)
            if history:
                for key in mapping:
                    if latest.get(key) is not None:
                        history[-1][key] = latest[key]
                history[-1]["slow_synced_at"] = now
                _write_history(history_path, history)
            synced += 1
        except Exception as exc:
            failed.append({"video_id": vid, "error": str(exc)[:200]})
            log.warning("Slow sync failed for %s: %s", vid, exc)
    with _state_lock:
        _state["slow_status"] = "partial" if failed else "ok"
        if synced:
            _state["last_slow_sync_at"] = now
        _state["last_error"] = f"{len(failed)} slow sync error(s)" if failed else None
    _save_state()
    log.info("Slow sync: %s updated, %s pending, %s failed", synced, pending, len(failed))
    return {"ok": not failed, "synced": synced, "pending": pending,
            "failed": failed[:30], "last_slow_sync_at": get_state()["last_slow_sync_at"]}


async def background_sync_loop() -> None:
    """Run fast sync every 15 minutes and deep sync every 6 hours."""
    _load_state()
    loop = asyncio.get_running_loop()
    next_fast = 0.0
    saved_slow = get_state().get("last_slow_sync_at")
    next_slow = 0.0
    if saved_slow:
        try:
            last = datetime.fromisoformat(str(saved_slow).replace("Z", "+00:00"))
            if last.tzinfo is None:
                last = last.replace(tzinfo=timezone.utc)
            age = (datetime.now(timezone.utc) - last.astimezone(timezone.utc)).total_seconds()
            next_slow = loop.time() + max(0.0, SLOW_INTERVAL_SEC - age)
        except Exception:
            next_slow = 0.0
    while True:
        now = loop.time()
        if now >= next_fast:
            await asyncio.to_thread(sync_fast)
            next_fast = loop.time() + FAST_INTERVAL_SEC
        if now >= next_slow:
            await asyncio.to_thread(sync_slow)
            next_slow = loop.time() + SLOW_INTERVAL_SEC
        await asyncio.sleep(30)
