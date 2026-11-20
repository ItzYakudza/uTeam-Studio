#!/usr/bin/env python3
"""uTeam-Studio Web API — SQLite + storage/, quiet logs."""
from __future__ import annotations

import sys
import io
import json
import asyncio
import logging
import traceback
import contextlib
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, PlainTextResponse
from pydantic import BaseModel
import uvicorn

logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

WEB_DIR = Path(__file__).resolve().parent
ROOT = WEB_DIR.parent / "YouTube"
sys.path.insert(0, str(ROOT))

import db as D
import youtube_sync as YT
import youtube_data as YD
import worker as W
import oauth_youtube as OYT

D.init_db()
W.start(interval_sec=3600)

app = FastAPI(title="uTeam-Studio", version="2.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
executor = ThreadPoolExecutor(max_workers=2)
render_procs: dict[int, object] = {}  # job_id -> subprocess.Popen | None
cancel_flags: dict[int, bool] = {}


# ---- models ----
class ChannelIn(BaseModel):
    name: str
    description: str = ""


class EpisodeIn(BaseModel):
    channel_id: int
    title: str
    kind: str = "shorts"


class EpisodeUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[str] = None


class FileUpdate(BaseModel):
    content: str


class RenderIn(BaseModel):
    episode_id: int
    preview: bool = False


class SheetIn(BaseModel):
    episode_id: int
    cols: int = 6


class CleanIn(BaseModel):
    episode_id: int
    keep_build: bool = False


# ---- health / doctor / migrate ----
@app.get("/api/health")
def health():
    return {"ok": True, "version": "2.0.0", "db": str(D.DB_PATH), "storage": str(D.STORAGE)}


@app.get("/api/doctor")
def doctor():
    issues = []
    info = {}
    try:
        import moviepy
        info["moviepy"] = getattr(moviepy, "__version__", "ok")
    except ImportError:
        issues.append("moviepy: pip install moviepy")
        info["moviepy"] = None
    try:
        from PIL import Image
        info["pillow"] = "ok"
    except ImportError:
        issues.append("pillow missing")
    try:
        import numpy
        info["numpy"] = numpy.__version__
    except ImportError:
        issues.append("numpy missing")
    import shutil
    ff = shutil.which("ffmpeg")
    if ff:
        info["ffmpeg"] = ff
    else:
        try:
            import imageio_ffmpeg
            info["ffmpeg"] = imageio_ffmpeg.get_ffmpeg_exe()
        except Exception:
            issues.append("ffmpeg not found")
            info["ffmpeg"] = None
    try:
        from core.config import get_format
        info["core"] = "ok"
    except Exception as e:
        issues.append(f"core: {e}")
        info["core"] = None
    info["channels"] = len(D.list_channels())
    info["episodes"] = len(D.list_episodes())
    return {"ok": len(issues) == 0, "issues": issues, "info": info}


@app.post("/api/migrate")
def migrate():
    stats = D.migrate_from_legacy()
    return {"ok": True, **stats}


# ---- channels ----
@app.get("/api/channels")
def channels():
    return D.list_channels()


@app.post("/api/channels")
def create_channel(body: ChannelIn):
    try:
        return D.create_channel(body.name, body.description)
    except ValueError as e:
        raise HTTPException(400, str(e))


@app.delete("/api/channels/{channel_id}")
def delete_channel(channel_id: int):
    try:
        D.delete_channel(channel_id)
        return {"ok": True}
    except ValueError as e:
        raise HTTPException(404, str(e))


# ---- episodes ----
@app.get("/api/episodes")
def episodes(
    channel_id: Optional[int] = None,
    kind: Optional[str] = None,
    status: Optional[str] = None,
    q: Optional[str] = None,
):
    rows = D.list_episodes(channel_id=channel_id, kind=kind, status=status, q=q)
    out = []
    for ep in rows:
        disp = YD.display_meta(Path(ep["disk_path"]))
        e = dict(ep)
        if disp.get("title"):
            e["title"] = disp["title"]
        e["has_preview"] = bool(disp.get("has_preview"))
        e["has_thumb"] = bool(disp.get("has_preview"))
        e["youtube_available"] = disp.get("youtube_available")
        e["display_source"] = disp.get("source")
        if disp.get("views") is not None:
            e["yt_views"] = disp.get("views")
        out.append(e)
    return out


@app.get("/api/episodes/{ep_id}")
def episode(ep_id: int):
    ep = D.get_episode(ep_id)
    if not ep:
        raise HTTPException(404, "Эпизод не найден")
    return ep


@app.post("/api/episodes")
def create_episode(body: EpisodeIn):
    try:
        return D.create_episode(body.channel_id, body.title, body.kind)
    except ValueError as e:
        raise HTTPException(400, str(e))


@app.patch("/api/episodes/{ep_id}")
def patch_episode(ep_id: int, body: EpisodeUpdate):
    fields = {k: v for k, v in body.model_dump().items() if v is not None}
    try:
        return D.update_episode(ep_id, **fields)
    except Exception as e:
        raise HTTPException(400, str(e))


@app.delete("/api/episodes/{ep_id}")
def delete_episode(ep_id: int):
    try:
        D.delete_episode(ep_id)
        return {"ok": True}
    except ValueError as e:
        raise HTTPException(404, str(e))


@app.post("/api/episodes/{ep_id}/refresh")
def refresh_episode(ep_id: int):
    ep = D.get_episode(ep_id)
    if not ep:
        raise HTTPException(404, "Эпизод не найден")
    return ep


# ---- files ----
@app.get("/api/episodes/{ep_id}/file")
def read_ep_file(ep_id: int, name: str = Query(..., pattern="^(script\\.txt|scenes\\.py|youtube_metadata\\.txt)$")):
    ep = D.get_episode(ep_id)
    if not ep:
        raise HTTPException(404, "Эпизод не найден")
    if name == "youtube_metadata.txt":
        fp = Path(ep["disk_path"]) / "build" / name
    else:
        fp = Path(ep["disk_path"]) / name
    if not fp.exists():
        return {"name": name, "content": ""}
    return {"name": name, "content": fp.read_text(encoding="utf-8")}


@app.put("/api/episodes/{ep_id}/file")
def write_ep_file(ep_id: int, name: str, body: FileUpdate):
    if name not in ("script.txt", "scenes.py"):
        raise HTTPException(400, "Only script.txt / scenes.py")
    ep = D.get_episode(ep_id)
    if not ep:
        raise HTTPException(404, "Эпизод не найден")
    fp = Path(ep["disk_path"]) / name
    fp.parent.mkdir(parents=True, exist_ok=True)
    fp.write_text(body.content, encoding="utf-8")
    # sync TITLE in DB if scenes
    if name == "scenes.py":
        for line in body.content.splitlines():
            if line.strip().startswith("TITLE"):
                try:
                    title = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if title:
                        D.update_episode(ep_id, title=title)
                except Exception:
                    pass
                break
    return D.get_episode(ep_id)


@app.post("/api/episodes/{ep_id}/voice")
async def upload_voice(ep_id: int, file: UploadFile = File(...)):
    ep = D.get_episode(ep_id)
    if not ep:
        raise HTTPException(404, "Эпизод не найден")
    data = await file.read()
    if len(data) < 500:
        raise HTTPException(400, "Файл слишком маленький")
    dest = Path(ep["disk_path"]) / "voiceover.mp3"
    dest.write_bytes(data)
    return D.get_episode(ep_id)


@app.post("/api/clean")
def clean(body: CleanIn):
    ep = D.get_episode(body.episode_id)
    if not ep:
        raise HTTPException(404, "Эпизод не найден")
    base = Path(ep["disk_path"])
    removed = []
    for name in ("source", "__pycache__"):
        p = base / name
        if p.exists():
            import shutil
            shutil.rmtree(p)
            removed.append(name)
    if not body.keep_build:
        p = base / "build"
        if p.exists():
            import shutil
            shutil.rmtree(p)
            removed.append("build")
    return {"ok": True, "removed": removed, "episode": D.get_episode(body.episode_id)}


# ---- render / sheet ----
@app.post("/api/render")
async def render(body: RenderIn):
    ep = D.get_episode(body.episode_id)
    if not ep:
        raise HTTPException(404, "Эпизод не найден")
    if not ep["has_scenes"] or not ep["has_voice"]:
        raise HTTPException(400, "Нужны scenes.py и voiceover.mp3")

    job = D.create_job(body.episode_id, "render", preview=body.preview)
    job_id = job["id"]
    cancel_flags[job_id] = False
    title = ep.get("title") or ep.get("folder") or str(ep["id"])

    def run():
        import subprocess
        logs = [
            "STAGE:prepare|Подготовка",
            f"episode={title}",
            f"preview={body.preview}",
        ]
        D.update_job(job_id, status="running", log=logs)
        ep_path = str(Path(ep["disk_path"]))
        cmd = [sys.executable, str(ROOT / "build.py"), "render", ep_path]
        if body.preview:
            cmd.append("--preview")
        # quiet if supported
        cmd.append("--quiet") if False else None
        cmd = [c for c in cmd if c is not None]
        try:
            # Prefer subprocess so we can kill on cancel (Windows-friendly)
            creation = 0
            if sys.platform == "win32":
                creation = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
            proc = subprocess.Popen(
                cmd,
                cwd=str(ROOT),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                creationflags=creation,
            )
            render_procs[job_id] = proc
            assert proc.stdout is not None
            for line in proc.stdout:
                if cancel_flags.get(job_id):
                    break
                line = line.rstrip()
                if not line:
                    continue
                logs.append(line)
                low = line.lower()
                if "[1/" in line or "голос" in low:
                    logs.append("STAGE:voice|Голос и тайминги")
                elif "valid" in low or "validator" in low:
                    logs.append("STAGE:validate|Проверка сцен")
                elif "[2/" in line or "музык" in low or "sfx" in low:
                    logs.append("STAGE:audio|Музыка и SFX")
                elif "[3/" in line or "сведение" in low:
                    logs.append("STAGE:mix|Сведение аудио")
                elif "[4/" in line or "кодир" in low:
                    logs.append("STAGE:encode|Кодирование MP4")
                # keep log bounded
                if len(logs) > 80:
                    logs = logs[-80:]
                D.update_job(job_id, log=list(logs))
            rc = proc.wait(timeout=1) if not cancel_flags.get(job_id) else None
            if cancel_flags.get(job_id):
                try:
                    if sys.platform == "win32":
                        import signal as _sig
                    proc.send_signal(getattr(_sig, "CTRL_BREAK_EVENT", _sig.SIGTERM))
                    proc.terminate()
                except Exception:
                    try:
                        proc.kill()
                    except Exception:
                        pass
                try:
                    proc.wait(timeout=5)
                except Exception:
                    pass
                logs.append("STAGE:cancelled|Отменено")
                logs.append("Cancelled by user")
                D.update_job(job_id, status="cancelled", log=logs, error="cancelled", finished_at=D._now())
                return
            rc = proc.poll()
            if rc == 0:
                if YD.local_preview_path(Path(ep["disk_path"])):
                    logs.append("preview file present")
                else:
                    logs.append("no preview file — cover skipped")
                logs.append("STAGE:done|Готово")
                logs.append("Done")
                D.update_job(job_id, status="done", log=logs, finished_at=D._now())
                D.get_episode(body.episode_id)
            else:
                logs.append(f"exit code {rc}")
                D.update_job(job_id, status="error", log=logs, error=f"render exit {rc}", finished_at=D._now())
                D.update_episode(body.episode_id, status="error", error_msg=f"render exit {rc}")
        except Exception as e:
            logs.append(traceback.format_exc()[-1200:])
            D.update_job(job_id, status="error", log=logs, error=str(e), finished_at=D._now())
            D.update_episode(body.episode_id, status="error", error_msg=str(e))
        finally:
            render_procs.pop(job_id, None)

    asyncio.get_event_loop().run_in_executor(executor, run)
    return {"job_id": job_id, "episode_id": body.episode_id, "title": title}



@app.post("/api/sheet")
async def sheet(body: SheetIn):
    ep = D.get_episode(body.episode_id)
    if not ep:
        raise HTTPException(404, "Эпизод не найден")
    job = D.create_job(body.episode_id, "sheet", preview=False)

    def run():
        logs = []
        D.update_job(job["id"], status="running")
        try:
            from build import sheet as _sheet
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                _sheet(Path(ep["disk_path"]), cols=body.cols)
            out = buf.getvalue().strip()
            if out:
                logs.extend(out.splitlines()[-20:])
            logs.append("Sheet done")
            D.update_job(job["id"], status="done", log=logs, finished_at=D._now())
            D.get_episode(body.episode_id)
        except Exception as e:
            logs.append(traceback.format_exc()[-800:])
            D.update_job(job["id"], status="error", log=logs, error=str(e), finished_at=D._now())

    asyncio.get_event_loop().run_in_executor(executor, run)
    return {"job_id": job["id"]}


@app.get("/api/jobs")
def jobs():
    return D.list_jobs()




@app.post("/api/jobs/{job_id}/cancel")
def cancel_job(job_id: int):
    j = D.get_job(job_id)
    if not j:
        raise HTTPException(404, "Job not found")
    if j["status"] not in ("queued", "running"):
        return {"ok": False, "reason": f"status={j['status']}"}
    cancel_flags[job_id] = True
    proc = render_procs.get(job_id)
    if proc is not None:
        try:
            import signal
            if sys.platform == "win32":
                try:
                    proc.send_signal(signal.CTRL_BREAK_EVENT)
                except Exception:
                    proc.terminate()
            else:
                proc.terminate()
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass
    # if still queued/running without proc, mark cancelled
    j2 = D.get_job(job_id)
    if j2 and j2["status"] in ("queued", "running"):
        logs = j2.get("log") or []
        if isinstance(logs, str):
            try:
                logs = json.loads(logs)
            except Exception:
                logs = [logs]
        logs = list(logs) + ["STAGE:cancelled|Отменено", "Cancel requested"]
        D.update_job(job_id, status="cancelled", log=logs, error="cancelled", finished_at=D._now())
    return {"ok": True, "job": D.get_job(job_id)}


@app.get("/api/jobs/active")
def active_jobs():
    items = D.list_jobs(limit=50)
    active = [j for j in items if j.get("status") in ("queued", "running")]
    # enrich titles
    out = []
    for j in active:
        row = dict(j)
        if j.get("episode_id"):
            ep = D.get_episode(j["episode_id"])
            if ep:
                row["episode_title"] = ep.get("title")
                row["episode_kind"] = ep.get("kind")
                row["channel_name"] = ep.get("channel_name")
        out.append(row)
    return out

@app.get("/api/jobs/{job_id}")
def job(job_id: int):
    j = D.get_job(job_id)
    if not j:
        raise HTTPException(404, "Job not found")
    return j


@app.get("/api/download")
def download(episode_id: int, kind: str = Query("video")):
    ep = D.get_episode(episode_id)
    if not ep:
        raise HTTPException(404, "Эпизод не найден")
    base = Path(ep["disk_path"]) / "build"
    if kind == "video":
        files = list(base.glob("final_*.mp4")) if base.exists() else []
        if not files:
            raise HTTPException(404, "Нет mp4")
        fp = files[0]
    elif kind == "meta":
        fp = base / "youtube_metadata.txt"
    elif kind == "sheet":
        fp = base / "contact_sheet.png"
    else:
        raise HTTPException(400, "kind: video|meta|sheet")
    if not fp.exists():
        raise HTTPException(404, "Файл не найден")
    return FileResponse(fp, filename=fp.name)



@app.post("/api/regenerate-thumbs")
def regenerate_thumbs():
    eps = D.list_episodes()
    ok = 0
    for ep in eps:
        if _make_thumb(Path(ep["disk_path"])):
            D.get_episode(ep["id"])
            ok += 1
    return {"ok": True, "thumbs": ok}





class YoutubeLinkIn(BaseModel):
    url: str
    sync_stats: bool = True
    update_title: bool = True


@app.post("/api/episodes/{ep_id}/youtube")
def link_youtube(ep_id: int, body: YoutubeLinkIn):
    """Bind URL and write storage/.../youtube_data/"""
    ep = D.get_episode(ep_id)
    if not ep:
        raise HTTPException(404, "Эпизод не найден")
    result = YD.sync_episode_folder(Path(ep["disk_path"]), body.url)
    if not result.get("available"):
        raise HTTPException(404, (result.get("info") or {}).get("error") or "Видео не найдено на YouTube")
    meta = result["meta"]
    fields = {
        "youtube_id": meta.get("video_id"),
        "youtube_url": meta.get("url"),
    }
    if body.update_title and meta.get("title"):
        fields["title"] = meta["title"]
    if meta.get("duration_sec"):
        fields["duration_sec"] = meta["duration_sec"]
    ep = D.update_episode(ep_id, **fields)
    stats_row = None
    if body.sync_stats and result.get("stats"):
        s = result["stats"]
        stats_row = D.upsert_video_stats(
            ep_id,
            s.get("date") or YT.today(),
            views=s.get("views") or 0,
            likes=s.get("likes") or 0,
            comments=s.get("comments") or 0,
            source=s.get("source") or "youtube",
            note="youtube_data sync",
        )
    disp = YD.display_meta(Path(ep["disk_path"]))
    return {"episode": ep, "youtube_data": result, "display": disp, "stats": stats_row}


@app.post("/api/episodes/{ep_id}/youtube/sync")
def sync_youtube(ep_id: int, update_title: bool = False):
    ep = D.get_episode(ep_id)
    if not ep:
        raise HTTPException(404, "Эпизод не найден")
    ref = ep.get("youtube_id") or ep.get("youtube_url")
    if not ref:
        raise HTTPException(400, "Сначала привяжи YouTube-ссылку")
    result = YD.sync_episode_folder(Path(ep["disk_path"]), ref)
    if not result.get("available"):
        YD.mark_unavailable(Path(ep["disk_path"]), (result.get("info") or {}).get("error") or "unavailable")
        raise HTTPException(404, (result.get("info") or {}).get("error") or "Видео недоступно")
    meta = result["meta"]
    fields = {"youtube_id": meta.get("video_id"), "youtube_url": meta.get("url")}
    if update_title and meta.get("title"):
        fields["title"] = meta["title"]
    if meta.get("duration_sec"):
        fields["duration_sec"] = meta["duration_sec"]
    ep = D.update_episode(ep_id, **fields)
    s = result.get("stats") or {}
    stats_row = D.upsert_video_stats(
        ep_id,
        s.get("date") or YT.today(),
        views=s.get("views") or 0,
        likes=s.get("likes") or 0,
        comments=s.get("comments") or 0,
        source=s.get("source") or "youtube",
        note="manual sync",
    )
    return {"episode": ep, "youtube_data": result, "display": YD.display_meta(Path(ep["disk_path"])), "stats": stats_row}


@app.post("/api/youtube/sync-all")
def sync_all_youtube(update_title: bool = False):
    return W.sync_all()


@app.get("/api/youtube/check")
def youtube_check(url: str):
    return YT.fetch_video(url)


@app.get("/api/worker/status")
def worker_status():
    return W.get_state()


@app.post("/api/worker/run")
def worker_run_now():
    return W.sync_all()


@app.get("/api/episodes/{ep_id}/display")
def episode_display(ep_id: int):
    ep = D.get_episode(ep_id)
    if not ep:
        raise HTTPException(404, "Эпизод не найден")
    disp = YD.display_meta(Path(ep["disk_path"]))
    ep = dict(ep)
    ep["display"] = disp
    # prefer display title for UI
    if disp.get("title"):
        ep["title"] = disp["title"]
    ep["has_preview"] = disp.get("has_preview")
    ep["has_thumb"] = disp.get("has_preview")
    return ep


@app.get("/api/analytics/export")
def analytics_export(format: str = "json"):
    """Export full analytics package for another AI / archive."""
    eps = D.list_episodes()
    items = []
    for ep in eps:
        disp = YD.display_meta(Path(ep["disk_path"]))
        hist = YD.load_stats_history(Path(ep["disk_path"]))
        latest = hist[-1] if hist else None
        include = True
        if latest and latest.get("include_in_aggregate") is False:
            include = False
        st = YD.read_json(YD.yt_dir(Path(ep["disk_path"])) / "status.json") or {}
        if st.get("available") is False:
            include = False
        items.append({
            "id": ep["id"],
            "title": disp.get("title") or ep.get("title"),
            "channel": ep.get("channel_name"),
            "kind": ep.get("kind"),
            "youtube_id": disp.get("youtube_id") or ep.get("youtube_id"),
            "youtube_url": disp.get("youtube_url") or ep.get("youtube_url"),
            "privacy": disp.get("privacy"),
            "published_at": disp.get("published_at"),
            "duration_sec": disp.get("duration_sec") or ep.get("duration_sec"),
            "available_on_youtube": st.get("available"),
            "include_in_aggregate": include,
            "latest_stats": latest,
            "history": hist,
            "description": disp.get("description"),
            "tags": disp.get("tags"),
        })
    summary = D.analytics_summary()
    # recompute aggregate only for include_in_aggregate
    agg_views = sum((i.get("latest_stats") or {}).get("views") or 0 for i in items if i.get("include_in_aggregate"))
    payload = {
        "exported_at": D._now(),
        "summary": summary,
        "aggregate_views_active_only": agg_views,
        "videos": items,
        "notes": [
            "avg_view_duration / retention / swipe-away требуют YouTube Studio API (OAuth) — публично недоступны",
            "unavailable videos kept in history but excluded from aggregate",
        ],
    }
    if format == "md" or format == "markdown":
        lines = [f"# uTeam Analytics Export", f"Exported: {payload['exported_at']}", ""]
        lines.append(f"Active aggregate views: {agg_views}")
        lines.append(f"Videos: {len(items)}")
        lines.append("")
        for i in items:
            lines.append(f"## {i['title']}")
            lines.append(f"- channel: {i['channel']} ({i['kind']})")
            lines.append(f"- youtube: {i.get('youtube_url')}")
            lines.append(f"- available: {i.get('available_on_youtube')} aggregate: {i.get('include_in_aggregate')}")
            ls = i.get("latest_stats") or {}
            lines.append(f"- views: {ls.get('views')} likes: {ls.get('likes')} comments: {ls.get('comments')}")
            lines.append(f"- duration_sec: {i.get('duration_sec')} published: {i.get('published_at')}")
            if i.get("tags"):
                lines.append(f"- tags: {i.get('tags')}")
            lines.append("")
        return PlainTextResponse("\n".join(lines), media_type="text/markdown")
    return payload




class ChannelUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    youtube_channel_url: Optional[str] = None


@app.patch("/api/channels/{channel_id}")
def patch_channel(channel_id: int, body: ChannelUpdate):
    fields = {k: v for k, v in body.model_dump().items() if v is not None}
    if not fields:
        raise HTTPException(400, "Nothing to update")
    ch = D.update_channel(channel_id, **fields)
    if not ch:
        raise HTTPException(404, "Channel not found")
    return ch


class AggregateIn(BaseModel):
    include: bool = True


@app.post("/api/episodes/{ep_id}/aggregate")
def set_aggregate(ep_id: int, body: AggregateIn):
    ep = D.get_episode(ep_id)
    if not ep:
        raise HTTPException(404, "Эпизод не найден")
    ep = D.update_episode(ep_id, include_in_aggregate=1 if body.include else 0)
    # mirror into youtube_data latest.json
    try:
        latest = YD.read_json(YD.yt_dir(Path(ep["disk_path"])) / "latest.json") or {}
        latest["include_in_aggregate"] = bool(body.include)
        YD.write_json(YD.yt_dir(Path(ep["disk_path"])) / "latest.json", latest)
    except Exception:
        pass
    return ep


@app.get("/api/episodes/{ep_id}/analytics")
def episode_analytics(ep_id: int):
    ep = D.get_episode(ep_id)
    if not ep:
        raise HTTPException(404, "Эпизод не найден")
    disp = YD.display_meta(Path(ep["disk_path"]))
    hist = YD.load_stats_history(Path(ep["disk_path"]))
    status = YD.read_json(YD.yt_dir(Path(ep["disk_path"])) / "status.json") or {}
    meta = YD.read_json(YD.yt_dir(Path(ep["disk_path"])) / "meta.json") or {}
    return {
        "episode": ep,
        "display": disp,
        "meta": meta,
        "status": status,
        "history": hist,
        "include_in_aggregate": bool(ep.get("include_in_aggregate", 1)),
    }


@app.post("/api/channels/{channel_id}/youtube/auto-link")
def auto_link_channel(channel_id: int, limit: int = 30):
    """Match channel videos from YouTube to local episodes by title."""
    ch = D.get_channel(channel_id)
    if not ch:
        raise HTTPException(404, "Channel not found")
    url = ch.get("youtube_channel_url")
    if not url:
        raise HTTPException(400, "Сначала укажи youtube_channel_url у канала")
    try:
        candidates = YT.list_channel_videos(url, limit=limit)
    except Exception as e:
        raise HTTPException(400, str(e))
    eps = D.list_episodes(channel_id=channel_id)
    linked = []
    skipped = []
    for ep in eps:
        if ep.get("youtube_id"):
            skipped.append({"episode_id": ep["id"], "reason": "already linked"})
            continue
        match = YT.best_title_match(ep.get("title") or "", candidates)
        if not match:
            skipped.append({"episode_id": ep["id"], "reason": "no match"})
            continue
        try:
            result = YD.sync_episode_folder(Path(ep["disk_path"]), match["video_id"])
            if result.get("available"):
                meta = result["meta"]
                D.update_episode(
                    ep["id"],
                    youtube_id=meta.get("video_id"),
                    youtube_url=meta.get("url"),
                    duration_sec=meta.get("duration_sec"),
                )
                s = result.get("stats") or {}
                D.upsert_video_stats(
                    ep["id"],
                    s.get("date") or YT.today(),
                    views=s.get("views") or 0,
                    likes=s.get("likes") or 0,
                    comments=s.get("comments") or 0,
                    source=s.get("source") or "youtube",
                    note="auto-link",
                )
                linked.append({
                    "episode_id": ep["id"],
                    "title": ep.get("title"),
                    "youtube_id": match["video_id"],
                    "match_score": match.get("match_score"),
                    "yt_title": match.get("title"),
                })
            else:
                skipped.append({"episode_id": ep["id"], "reason": "yt unavailable"})
        except Exception as e:
            skipped.append({"episode_id": ep["id"], "reason": str(e)})
    return {"ok": True, "candidates": len(candidates), "linked": linked, "skipped": skipped}




@app.get("/api/oauth/youtube/status")
def oauth_status():
    return OYT.status()


@app.get("/api/oauth/youtube/start")
def oauth_start():
    try:
        url = OYT.auth_url()
    except Exception as e:
        raise HTTPException(400, str(e))
    return {"auth_url": url}


@app.get("/api/oauth/youtube/callback")
def oauth_callback(code: str = "", state: str = "", error: str = ""):
    from fastapi.responses import HTMLResponse
    if error:
        return HTMLResponse(f"<h2>OAuth error: {error}</h2><p>Можно закрыть окно.</p>", status_code=400)
    if not code:
        return HTMLResponse("<h2>Нет code</h2>", status_code=400)
    try:
        tok = OYT.exchange_code(code)
        title = tok.get("channel_title") or tok.get("channel_id") or "OK"
        return HTMLResponse(
            f"""<!doctype html><html><body style="font-family:sans-serif;background:#111;color:#eee;padding:40px">
            <h2>YouTube подключён</h2>
            <p>Канал: <b>{title}</b></p>
            <p>Можно закрыть это окно и вернуться в uTeam Studio.</p>
            <script>setTimeout(()=>window.close(), 1500)</script>
            </body></html>"""
        )
    except Exception as e:
        return HTMLResponse(f"<h2>Ошибка</h2><pre>{e}</pre>", status_code=400)


@app.post("/api/oauth/youtube/disconnect")
def oauth_disconnect():
    OYT.clear_token()
    return {"ok": True}


@app.post("/api/oauth/youtube/refresh-channel")
def oauth_refresh_channel():
    try:
        ch = OYT.fetch_mine_channel()
        tok = OYT.load_token() or {}
        tok.update(ch)
        OYT.save_token(tok)
        return ch
    except Exception as e:
        raise HTTPException(400, str(e))


@app.get("/api/oauth/youtube/video/{video_id}/studio")
def oauth_video_studio(video_id: str, days: int = 90):
    try:
        return OYT.video_studio_stats(video_id, days=days)
    except Exception as e:
        raise HTTPException(400, str(e))


@app.post("/api/fix-titles")
def fix_titles():
    n = D.fix_all_titles()
    return {"ok": True, "fixed": n}


class StatsIn(BaseModel):
    episode_id: int
    date: str  # YYYY-MM-DD
    views: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    watch_time_h: float = 0
    subscribers: int = 0
    ctr: float = 0
    note: str = ""


@app.get("/api/analytics/summary")
def analytics_summary(channel_id: Optional[int] = None):
    base = D.analytics_summary(channel_id=channel_id)
    # enrich with per-episode latest from youtube_data, respect include_in_aggregate
    eps = D.list_episodes(channel_id=channel_id)
    active = []
    excluded = []
    for ep in eps:
        hist = YD.load_stats_history(Path(ep["disk_path"]))
        latest = hist[-1] if hist else None
        incl = bool(ep.get("include_in_aggregate", 1))
        st = YD.read_json(YD.yt_dir(Path(ep["disk_path"])) / "status.json") or {}
        if st.get("available") is False:
            incl = False
        row = {
            "episode_id": ep["id"],
            "title": ep.get("title"),
            "channel_name": ep.get("channel_name"),
            "kind": ep.get("kind"),
            "youtube_id": ep.get("youtube_id"),
            "include_in_aggregate": incl,
            "available": st.get("available"),
            "views": (latest or {}).get("views") or 0,
            "likes": (latest or {}).get("likes") or 0,
            "comments": (latest or {}).get("comments") or 0,
            "history_points": len(hist),
            "published_at": (YD.read_json(YD.yt_dir(Path(ep["disk_path"])) / "meta.json") or {}).get("published_at"),
            "duration_sec": ep.get("duration_sec") or (latest or {}).get("duration_sec"),
        }
        if incl:
            active.append(row)
        else:
            excluded.append(row)
    active_sorted = sorted(active, key=lambda x: x["views"], reverse=True)
    base["top_videos"] = active_sorted[:15]
    base["all_videos"] = active_sorted + excluded
    base["total_views"] = sum(v["views"] for v in active)
    base["total_likes"] = sum(v["likes"] for v in active)
    base["total_comments"] = sum(v["comments"] for v in active)
    base["excluded_count"] = len(excluded)
    base["active_count"] = len(active)
    return base


@app.get("/api/analytics/stats")
def analytics_stats(episode_id: Optional[int] = None, channel_id: Optional[int] = None):
    return D.list_video_stats(episode_id=episode_id, channel_id=channel_id)


@app.post("/api/analytics/stats")
def analytics_stats_upsert(body: StatsIn):
    return D.upsert_video_stats(
        body.episode_id,
        body.date,
        views=body.views,
        likes=body.likes,
        comments=body.comments,
        shares=body.shares,
        watch_time_h=body.watch_time_h,
        subscribers=body.subscribers,
        ctr=body.ctr,
        note=body.note,
        source="manual",
    )


@app.get("/api/episodes/{ep_id}/thumb")
def episode_thumb(ep_id: int):
    ep = D.get_episode(ep_id)
    if not ep:
        raise HTTPException(404, "Эпизод не найден")
    fp = YD.local_preview_path(Path(ep["disk_path"]))
    if not fp:
        raise HTTPException(404, "Нет превью (нужен preview.png/jpg или youtube_data/thumb)")
    return FileResponse(fp, filename=fp.name)

def _make_thumb(ep_path: Path) -> bool:
    """Do NOT extract frames. Only report whether a real preview file exists."""
    return YD.local_preview_path(Path(ep_path)) is not None


DIST = WEB_DIR / "frontend" / "dist"
if DIST.exists():
    app.mount("/", StaticFiles(directory=str(DIST), html=True), name="ui")


if __name__ == "__main__":
    print(f"uTeam-Studio API  http://127.0.0.1:5050")
    print(f"DB  = {D.DB_PATH}")
    print(f"STOR= {D.STORAGE}")
    uvicorn.run(app, host="127.0.0.1", port=5050, log_level="warning", access_log=False)
