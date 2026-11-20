#!/usr/bin/env python3
"""
uTeam-Studio Web API
FastAPI backend that wraps build.py functionality for the React UI.
"""

from __future__ import annotations

import os
import sys
import shutil
import asyncio
import traceback
from datetime import datetime
from pathlib import Path
from typing import Optional, List
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

# Make YouTube/ importable
WEB_DIR = Path(__file__).resolve().parent
ROOT = WEB_DIR.parent / "YouTube"  # .../uTeam-Studio/YouTube
sys.path.insert(0, str(ROOT))

from build import (
    list_channels as _list_channels,
    list_episodes as _list_episodes,
    create_channel as _create_channel,
    create_episode as _create_episode,
    next_index,
    CHANNELS,
    render as _render,
    sheet as _sheet,
    write_metadata,
)

app = FastAPI(title="uTeam-Studio", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

executor = ThreadPoolExecutor(max_workers=2)

# In-memory job status for long renders
jobs: dict[str, dict] = {}


# ---------- Models ----------

class ChannelCreate(BaseModel):
    name: str


class EpisodeCreate(BaseModel):
    channel: str
    kind: str  # shorts | long
    short_name: str


class FileUpdate(BaseModel):
    content: str


class RenderRequest(BaseModel):
    path: str
    preview: bool = False
    channel: Optional[str] = None


class SheetRequest(BaseModel):
    path: str
    cols: int = 6


# ---------- Helpers ----------

def ep_info(ep_path: Path) -> dict:
    kind = ep_path.parent.name  # shorts or longs
    has_scenes = (ep_path / "scenes.py").exists()
    has_script = (ep_path / "script.txt").exists()
    has_voice = (ep_path / "voiceover.mp3").exists()
    build_dir = ep_path / "build"
    finals = list(build_dir.glob("final_*.mp4")) if build_dir.exists() else []
    meta = build_dir / "youtube_metadata.txt" if build_dir.exists() else None
    sheet = build_dir / "contact_sheet.png" if build_dir.exists() else None
    return {
        "name": ep_path.name,
        "path": str(ep_path.relative_to(ROOT)),
        "kind": kind,
        "has_scenes": has_scenes,
        "has_script": has_script,
        "has_voice": has_voice,
        "has_final": len(finals) > 0,
        "final_name": finals[0].name if finals else None,
        "has_meta": meta.exists() if meta else False,
        "has_sheet": sheet.exists() if sheet else False,
        "mtime": datetime.fromtimestamp(ep_path.stat().st_mtime).isoformat(),
    }


def channel_info(name: str) -> dict:
    shorts = list_episodes(name, "shorts")
    longs = list_episodes(name, "longs")
    return {
        "name": name,
        "shorts_count": len(shorts),
        "longs_count": len(longs),
        "episodes": [ep_info(p) for _, p in shorts + longs],
    }


def list_episodes(channel: str, kind: str = None):
    return _list_episodes(channel, kind)


# ---------- API ----------

@app.get("/api/health")
def health():
    return {"ok": True, "root": str(ROOT)}


@app.get("/api/channels")
def get_channels():
    names = _list_channels(silent=True)
    return [channel_info(n) for n in names]


@app.post("/api/channels")
def create_channel(body: ChannelCreate):
    name = body.name.strip().lower().replace(" ", "_")
    if not name:
        raise HTTPException(400, "Empty name")
    path = CHANNELS / name
    if path.exists():
        raise HTTPException(400, f"Channel already exists: {name}")
    (path / "videos" / "shorts").mkdir(parents=True, exist_ok=True)
    (path / "videos" / "longs").mkdir(parents=True, exist_ok=True)
    return {"ok": True, "name": name}


@app.delete("/api/channels/{name}")
def delete_channel(name: str):
    path = CHANNELS / name
    if not path.exists():
        raise HTTPException(404, "Channel not found")
    shutil.rmtree(path)
    return {"ok": True}


@app.get("/api/channels/{name}/episodes")
def get_episodes(name: str):
    if not (CHANNELS / name).exists():
        raise HTTPException(404, "Channel not found")
    return channel_info(name)["episodes"]


@app.post("/api/episodes")
def create_episode(body: EpisodeCreate):
    kind = body.kind.lower()
    if kind in ("long", "longs"):
        kind = "longs"
    elif kind in ("short", "shorts"):
        kind = "shorts"
    else:
        raise HTTPException(400, "kind must be shorts or long")

    ch_path = CHANNELS / body.channel
    if not ch_path.exists():
        raise HTTPException(404, f"Channel not found: {body.channel}")

    folder = ch_path / "videos" / kind
    folder.mkdir(parents=True, exist_ok=True)

    idx = next_index(folder)
    date = datetime.now().strftime("%Y-%m-%d")
    time = datetime.now().strftime("%H%M")
    safe = body.short_name.strip().lower().replace(" ", "_")
    ep_name = f"{idx:03d}_{safe}_{date}_{time}"
    ep_path = folder / ep_name
    ep_path.mkdir(parents=True, exist_ok=True)

    mode = "shorts" if kind == "shorts" else "long"
    (ep_path / "script.txt").write_text("# Текст озвучки\n\n", encoding="utf-8")

    scenes_template = f'''"""
Episode: {ep_name}
Channel: {body.channel}
"""

from core.toolkit import *

MODE = "{mode}"
CHANNEL_NAME = "{body.channel}"

TEXTS = [
    "First sentence goes here.",
    "Second sentence goes here.",
]

CHAPTERS = [
    "Hook",
    "Main point",
]

TITLE = "Your Title Here"
DESC = """Description.

SOURCES
- ...
"""
TAGS = "tag1, tag2"

def s01(cv, t, T):
    title(cv, t, "Title", 56, 140)

def s02(cv, t, T):
    title(cv, t, "Second scene", 52, 140)

TRANSITIONS = {{}}   # например {{1: "iris", 2: "zoom:0.5"}}

_FN = {{"s01": s01, "s02": s02}}
_BG = {{"s01": (255, 248, 225), "s02": (232, 240, 255)}}
ORDER = ["s01", "s02"]
SCENES = [(_BG[k], _FN[k]) for k in ORDER]
'''
    (ep_path / "scenes.py").write_text(scenes_template, encoding="utf-8")
    return {"ok": True, "episode": ep_info(ep_path)}


@app.delete("/api/episodes")
def delete_episode(path: str = Query(...)):
    ep_path = (ROOT / path).resolve()
    if not str(ep_path).startswith(str(ROOT.resolve())):
        raise HTTPException(400, "Invalid path")
    if not ep_path.is_dir():
        raise HTTPException(404, "Episode not found")
    shutil.rmtree(ep_path)
    return {"ok": True}


@app.get("/api/file")
def read_file(path: str):
    """Read script.txt, scenes.py or youtube_metadata.txt"""
    fp = (ROOT / path).resolve()
    if not str(fp).startswith(str(ROOT.resolve())):
        raise HTTPException(400, "Invalid path")
    if not fp.is_file():
        raise HTTPException(404, "File not found")
    # Only allow text-ish files
    if fp.suffix not in {".txt", ".py", ".md", ".json"}:
        raise HTTPException(400, "Only text files allowed")
    return {"path": path, "content": fp.read_text(encoding="utf-8")}


@app.put("/api/file")
def write_file(path: str, body: FileUpdate):
    fp = (ROOT / path).resolve()
    if not str(fp).startswith(str(ROOT.resolve())):
        raise HTTPException(400, "Invalid path")
    if fp.suffix not in {".txt", ".py", ".md", ".json"}:
        raise HTTPException(400, "Only text files allowed")
    fp.parent.mkdir(parents=True, exist_ok=True)
    fp.write_text(body.content, encoding="utf-8")
    return {"ok": True}


@app.post("/api/render")
async def start_render(body: RenderRequest, background_tasks: BackgroundTasks):
    ep_path = (ROOT / body.path).resolve()
    if not str(ep_path).startswith(str(ROOT.resolve())) or not ep_path.is_dir():
        raise HTTPException(404, "Episode not found")

    job_id = f"render_{ep_path.name}_{datetime.now().strftime('%H%M%S')}"
    jobs[job_id] = {
        "id": job_id,
        "status": "queued",
        "path": body.path,
        "preview": body.preview,
        "log": [],
        "error": None,
        "started": datetime.now().isoformat(),
        "finished": None,
    }

    def run():
        jobs[job_id]["status"] = "running"
        try:
            # Capture print output roughly by redirecting would be complex;
            # we just call the original render and mark success/fail.
            _render(ep_path, preview=body.preview, channel_override=body.channel)
            jobs[job_id]["status"] = "done"
            jobs[job_id]["log"].append("Render finished successfully")
        except Exception as e:
            jobs[job_id]["status"] = "error"
            jobs[job_id]["error"] = str(e)
            jobs[job_id]["log"].append(traceback.format_exc())
        finally:
            jobs[job_id]["finished"] = datetime.now().isoformat()

    loop = asyncio.get_event_loop()
    loop.run_in_executor(executor, run)
    return {"job_id": job_id}


@app.get("/api/jobs/{job_id}")
def get_job(job_id: str):
    if job_id not in jobs:
        raise HTTPException(404, "Job not found")
    return jobs[job_id]


@app.get("/api/jobs")
def list_jobs():
    return list(jobs.values())


@app.post("/api/sheet")
async def start_sheet(body: SheetRequest):
    ep_path = (ROOT / body.path).resolve()
    if not str(ep_path).startswith(str(ROOT.resolve())) or not ep_path.is_dir():
        raise HTTPException(404, "Episode not found")

    job_id = f"sheet_{ep_path.name}_{datetime.now().strftime('%H%M%S')}"
    jobs[job_id] = {
        "id": job_id,
        "status": "queued",
        "path": body.path,
        "log": [],
        "error": None,
        "started": datetime.now().isoformat(),
        "finished": None,
    }

    def run():
        jobs[job_id]["status"] = "running"
        try:
            _sheet(ep_path, cols=body.cols)
            jobs[job_id]["status"] = "done"
            jobs[job_id]["log"].append("Contact sheet created")
        except Exception as e:
            jobs[job_id]["status"] = "error"
            jobs[job_id]["error"] = str(e)
            jobs[job_id]["log"].append(traceback.format_exc())
        finally:
            jobs[job_id]["finished"] = datetime.now().isoformat()

    loop = asyncio.get_event_loop()
    loop.run_in_executor(executor, run)
    return {"job_id": job_id}


@app.get("/api/download")
def download(path: str):
    """Download any file under ROOT (mp4, png, txt, ...)"""
    fp = (ROOT / path).resolve()
    if not str(fp).startswith(str(ROOT.resolve())) or not fp.is_file():
        raise HTTPException(404, "File not found")
    return FileResponse(fp, filename=fp.name)


# Serve React build if present
FRONTEND_DIST = Path(__file__).parent / "frontend" / "dist"
if FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=5050, reload=True)
