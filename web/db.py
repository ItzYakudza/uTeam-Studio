"""
SQLite storage for uTeam-Studio.
Episodes/channels live in DB; media files stay on disk under storage/.
"""
from __future__ import annotations

import json
import sqlite3
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

try:
    import titles as titlelib
except ImportError:
    titlelib = None

WEB_DIR = Path(__file__).resolve().parent
ROOT = WEB_DIR.parent / "YouTube"
STORAGE = ROOT / "storage"
DB_PATH = ROOT / "studio.db"


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def connect() -> sqlite3.Connection:
    STORAGE.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    conn = connect()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS channels (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            slug        TEXT NOT NULL UNIQUE,
            description TEXT DEFAULT '',
            youtube_channel_url TEXT,
            created_at  TEXT NOT NULL,
            updated_at  TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS episodes (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_id   INTEGER NOT NULL REFERENCES channels(id) ON DELETE CASCADE,
            title        TEXT NOT NULL,
            kind         TEXT NOT NULL CHECK(kind IN ('shorts','long')),
            status       TEXT NOT NULL DEFAULT 'draft',
            -- draft | scripted | voiced | ready | rendered | error
            description  TEXT DEFAULT '',
            tags         TEXT DEFAULT '',
            folder       TEXT NOT NULL,
            has_script   INTEGER DEFAULT 0,
            has_scenes   INTEGER DEFAULT 0,
            has_voice    INTEGER DEFAULT 0,
            has_video    INTEGER DEFAULT 0,
            has_meta     INTEGER DEFAULT 0,
            has_thumb    INTEGER DEFAULT 0,
            youtube_url  TEXT,
            youtube_id   TEXT,
            include_in_aggregate INTEGER DEFAULT 1,
            duration_sec REAL,
            error_msg    TEXT,
            created_at   TEXT NOT NULL,
            updated_at   TEXT NOT NULL,
            UNIQUE(channel_id, folder)
        );

        CREATE TABLE IF NOT EXISTS jobs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            episode_id  INTEGER REFERENCES episodes(id) ON DELETE SET NULL,
            kind        TEXT NOT NULL,
            status      TEXT NOT NULL DEFAULT 'queued',
            preview     INTEGER DEFAULT 0,
            log         TEXT DEFAULT '[]',
            error       TEXT,
            created_at  TEXT NOT NULL,
            finished_at TEXT
        );

        CREATE TABLE IF NOT EXISTS video_stats (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            episode_id  INTEGER NOT NULL REFERENCES episodes(id) ON DELETE CASCADE,
            date        TEXT NOT NULL,
            views       INTEGER DEFAULT 0,
            likes       INTEGER DEFAULT 0,
            comments    INTEGER DEFAULT 0,
            shares      INTEGER DEFAULT 0,
            watch_time_h REAL DEFAULT 0,
            subscribers INTEGER DEFAULT 0,
            ctr         REAL DEFAULT 0,
            source      TEXT DEFAULT 'manual',
            note        TEXT DEFAULT '',
            created_at  TEXT NOT NULL,
            UNIQUE(episode_id, date)
        );

        CREATE TABLE IF NOT EXISTS channel_stats (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_id  INTEGER NOT NULL REFERENCES channels(id) ON DELETE CASCADE,
            date        TEXT NOT NULL,
            subscribers INTEGER DEFAULT 0,
            views       INTEGER DEFAULT 0,
            watch_time_h REAL DEFAULT 0,
            note        TEXT DEFAULT '',
            created_at  TEXT NOT NULL,
            UNIQUE(channel_id, date)
        );

        CREATE INDEX IF NOT EXISTS idx_ep_channel ON episodes(channel_id);
        CREATE INDEX IF NOT EXISTS idx_ep_status ON episodes(status);
        CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
        """
    )
    conn.commit()
    cols = {r[1] for r in conn.execute("PRAGMA table_info(episodes)").fetchall()}
    if "has_thumb" not in cols:
        conn.execute("ALTER TABLE episodes ADD COLUMN has_thumb INTEGER DEFAULT 0")
    if "youtube_url" not in cols:
        conn.execute("ALTER TABLE episodes ADD COLUMN youtube_url TEXT")
    if "youtube_id" not in cols:
        conn.execute("ALTER TABLE episodes ADD COLUMN youtube_id TEXT")
    if "include_in_aggregate" not in cols:
        conn.execute("ALTER TABLE episodes ADD COLUMN include_in_aggregate INTEGER DEFAULT 1")
    cols_c = {r[1] for r in conn.execute("PRAGMA table_info(channels)").fetchall()}
    if "youtube_channel_url" not in cols_c:
        conn.execute("ALTER TABLE channels ADD COLUMN youtube_channel_url TEXT")
    conn.commit()
    conn.close()


def row_to_dict(row: sqlite3.Row | None) -> Optional[dict]:
    if row is None:
        return None
    return dict(row)


def slugify(text: str) -> str:
    s = text.strip().lower().replace(" ", "_")
    out = []
    for ch in s:
        if ch.isalnum() or ch in ("_", "-"):
            out.append(ch)
    return "".join(out)[:64] or "item"


# ---- channels ----

def list_channels() -> list[dict]:
    conn = connect()
    rows = conn.execute(
        """
        SELECT c.*,
               (SELECT COUNT(*) FROM episodes e WHERE e.channel_id = c.id AND e.kind='shorts') AS shorts_count,
               (SELECT COUNT(*) FROM episodes e WHERE e.channel_id = c.id AND e.kind='long') AS longs_count,
               (SELECT COUNT(*) FROM episodes e WHERE e.channel_id = c.id) AS episodes_count
        FROM channels c
        ORDER BY c.name
        """
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_channel(channel_id: int) -> Optional[dict]:
    conn = connect()
    row = conn.execute("SELECT * FROM channels WHERE id=?", (channel_id,)).fetchone()
    conn.close()
    return row_to_dict(row)


def get_channel_by_slug(slug: str) -> Optional[dict]:
    conn = connect()
    row = conn.execute("SELECT * FROM channels WHERE slug=?", (slug,)).fetchone()
    conn.close()
    return row_to_dict(row)


def create_channel(name: str, description: str = "") -> dict:
    slug = slugify(name)
    now = _now()
    conn = connect()
    try:
        cur = conn.execute(
            "INSERT INTO channels(name, slug, description, created_at, updated_at) VALUES (?,?,?,?,?)",
            (name.strip(), slug, description, now, now),
        )
        conn.commit()
        cid = cur.lastrowid
    except sqlite3.IntegrityError:
        conn.close()
        raise ValueError(f"Канал уже существует: {slug}")
    conn.close()
    # disk
    for kind in ("shorts", "longs"):
        (STORAGE / slug / kind).mkdir(parents=True, exist_ok=True)
    return get_channel(cid)  # type: ignore


def delete_channel(channel_id: int) -> None:
    ch = get_channel(channel_id)
    if not ch:
        raise ValueError("Канал не найден")
    conn = connect()
    conn.execute("DELETE FROM channels WHERE id=?", (channel_id,))
    conn.commit()
    conn.close()
    disk = STORAGE / ch["slug"]
    if disk.exists():
        shutil.rmtree(disk, ignore_errors=True)


# ---- episodes ----

def _refresh_flags(ep_id: int) -> dict:
    """Sync has_* flags from disk."""
    conn = connect()
    row = conn.execute("SELECT * FROM episodes WHERE id=?", (ep_id,)).fetchone()
    if not row:
        conn.close()
        raise ValueError("Эпизод не найден")
    ep = dict(row)
    ch = conn.execute("SELECT slug FROM channels WHERE id=?", (ep["channel_id"],)).fetchone()
    conn.close()
    if not ch:
        return ep
    folder = STORAGE / ch["slug"] / ("shorts" if ep["kind"] == "shorts" else "longs") / ep["folder"]
    has_script = (folder / "script.txt").exists()
    has_scenes = (folder / "scenes.py").exists()
    has_voice = (folder / "voiceover.mp3").exists()
    build = folder / "build"
    finals = list(build.glob("final_*.mp4")) if build.exists() else []
    has_video = len(finals) > 0
    has_meta = (build / "youtube_metadata.txt").exists() if build.exists() else False
    has_thumb = False
    try:
        import youtube_data as YD
        has_thumb = YD.local_preview_path(folder) is not None
    except Exception:
        if build.exists():
            has_thumb = any(
                (build / n).exists()
                for n in (
                    "preview.jpg", "preview.png", "preview.jpeg",
                    "Preview.jpg", "Preview.png",
                    "thumb.jpg", "thumb.png",
                )
            )

    status = ep["status"]
    if has_video:
        status = "rendered"
    elif has_voice and has_scenes:
        status = "ready"
    elif has_voice:
        status = "voiced"
    elif has_script or has_scenes:
        status = "scripted"
    else:
        status = "draft"

    conn = connect()
    conn.execute(
        """
        UPDATE episodes SET
            has_script=?, has_scenes=?, has_voice=?, has_video=?, has_meta=?, has_thumb=?,
            status=?, updated_at=?
        WHERE id=?
        """,
        (
            int(has_script),
            int(has_scenes),
            int(has_voice),
            int(has_video),
            int(has_meta),
            int(has_thumb),
            status,
            _now(),
            ep_id,
        ),
    )
    conn.commit()
    row = conn.execute(
        """
        SELECT e.*, c.name AS channel_name, c.slug AS channel_slug
        FROM episodes e JOIN channels c ON c.id = e.channel_id
        WHERE e.id=?
        """,
        (ep_id,),
    ).fetchone()
    conn.close()
    d = dict(row)
    d["disk_path"] = str(
        STORAGE / d["channel_slug"] / ("shorts" if d["kind"] == "shorts" else "longs") / d["folder"]
    )
    if has_video and finals:
        d["final_name"] = finals[0].name
    else:
        d["final_name"] = None
    return d


def list_episodes(
    channel_id: Optional[int] = None,
    kind: Optional[str] = None,
    status: Optional[str] = None,
    q: Optional[str] = None,
) -> list[dict]:
    conn = connect()
    sql = """
        SELECT e.*, c.name AS channel_name, c.slug AS channel_slug
        FROM episodes e
        JOIN channels c ON c.id = e.channel_id
        WHERE 1=1
    """
    params: list[Any] = []
    if channel_id:
        sql += " AND e.channel_id=?"
        params.append(channel_id)
    if kind:
        sql += " AND e.kind=?"
        params.append(kind)
    if status:
        sql += " AND e.status=?"
        params.append(status)
    if q:
        sql += " AND (e.title LIKE ? OR e.tags LIKE ? OR e.description LIKE ?)"
        params.extend([f"%{q}%"] * 3)
    sql += " ORDER BY e.updated_at DESC"
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        d["disk_path"] = str(
            STORAGE
            / d["channel_slug"]
            / ("shorts" if d["kind"] == "shorts" else "longs")
            / d["folder"]
        )
        result.append(d)
    return result


def get_episode(ep_id: int) -> Optional[dict]:
    try:
        return _refresh_flags(ep_id)
    except ValueError:
        return None


def create_episode(channel_id: int, title: str, kind: str = "shorts") -> dict:
    kind = "shorts" if kind in ("short", "shorts") else "long"
    ch = get_channel(channel_id)
    if not ch:
        raise ValueError("Канал не найден")

    conn = connect()
    # next index
    folder_base = STORAGE / ch["slug"] / ("shorts" if kind == "shorts" else "longs")
    folder_base.mkdir(parents=True, exist_ok=True)
    existing = [p.name for p in folder_base.iterdir() if p.is_dir()]
    nums = []
    for name in existing:
        try:
            nums.append(int(name.split("_")[0]))
        except Exception:
            pass
    idx = max(nums, default=0) + 1
    date = datetime.now().strftime("%Y-%m-%d")
    time = datetime.now().strftime("%H%M")
    safe = slugify(title)
    folder = f"{idx:03d}_{safe}_{date}_{time}"

    now = _now()
    cur = conn.execute(
        """
        INSERT INTO episodes(
            channel_id, title, kind, status, folder,
            has_script, has_scenes, created_at, updated_at
        ) VALUES (?,?,?,?,?,?,?,?,?)
        """,
        (channel_id, title.strip(), kind, "scripted", folder, 1, 1, now, now),
    )
    conn.commit()
    ep_id = cur.lastrowid
    conn.close()

    ep_path = folder_base / folder
    ep_path.mkdir(parents=True, exist_ok=True)
    mode = "shorts" if kind == "shorts" else "long"
    (ep_path / "script.txt").write_text("# Текст озвучки\n\n", encoding="utf-8")
    scenes = f'''"""
Episode: {title}
Channel: {ch["slug"]}
"""

from core.toolkit import *

MODE = "{mode}"
CHANNEL_NAME = "{ch["slug"]}"

TEXTS = [
    "First sentence goes here.",
    "Second sentence goes here.",
]

CHAPTERS = ["Hook", "Main"]

TITLE = {title!r}
DESC = """Description.

SOURCES
- ...
"""
TAGS = "tag1, tag2"

def s01(cv, t, T):
    title(cv, t, {title!r}, 56, 140)

def s02(cv, t, T):
    title(cv, t, "Scene 2", 52, 140)

TRANSITIONS = {{}}

_FN = {{"s01": s01, "s02": s02}}
_BG = {{"s01": (255, 248, 225), "s02": (232, 240, 255)}}
ORDER = ["s01", "s02"]
SCENES = [(_BG[k], _FN[k]) for k in ORDER]
'''
    (ep_path / "scenes.py").write_text(scenes, encoding="utf-8")
    return get_episode(ep_id)  # type: ignore


def update_episode(ep_id: int, **fields) -> dict:
    allowed = {"title", "description", "tags", "status", "error_msg", "duration_sec", "youtube_url", "youtube_id", "include_in_aggregate"}
    sets = []
    params = []
    for k, v in fields.items():
        if k in allowed:
            sets.append(f"{k}=?")
            params.append(v)
    if not sets:
        return get_episode(ep_id)  # type: ignore
    sets.append("updated_at=?")
    params.append(_now())
    params.append(ep_id)
    conn = connect()
    conn.execute(f"UPDATE episodes SET {', '.join(sets)} WHERE id=?", params)
    conn.commit()
    conn.close()
    return get_episode(ep_id)  # type: ignore


def delete_episode(ep_id: int) -> None:
    ep = get_episode(ep_id)
    if not ep:
        raise ValueError("Эпизод не найден")
    conn = connect()
    conn.execute("DELETE FROM episodes WHERE id=?", (ep_id,))
    conn.commit()
    conn.close()
    disk = Path(ep["disk_path"])
    if disk.exists():
        shutil.rmtree(disk, ignore_errors=True)


def episode_disk_path(ep: dict) -> Path:
    return Path(ep["disk_path"])


# ---- jobs ----

def create_job(episode_id: int, kind: str, preview: bool = False) -> dict:
    now = _now()
    conn = connect()
    cur = conn.execute(
        "INSERT INTO jobs(episode_id, kind, status, preview, log, created_at) VALUES (?,?,?,?,?,?)",
        (episode_id, kind, "queued", int(preview), "[]", now),
    )
    conn.commit()
    jid = cur.lastrowid
    row = conn.execute("SELECT * FROM jobs WHERE id=?", (jid,)).fetchone()
    conn.close()
    return dict(row)


def update_job(job_id: int, **fields) -> dict:
    allowed = {"status", "log", "error", "finished_at"}
    sets, params = [], []
    for k, v in fields.items():
        if k in allowed:
            if k == "log" and not isinstance(v, str):
                v = json.dumps(v, ensure_ascii=False)
            sets.append(f"{k}=?")
            params.append(v)
    if not sets:
        conn = connect()
        row = conn.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
        conn.close()
        return dict(row)
    params.append(job_id)
    conn = connect()
    conn.execute(f"UPDATE jobs SET {', '.join(sets)} WHERE id=?", params)
    conn.commit()
    row = conn.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
    conn.close()
    return dict(row)


def list_jobs(limit: int = 30) -> list[dict]:
    conn = connect()
    rows = conn.execute(
        """
        SELECT j.*, e.title AS episode_title
        FROM jobs j
        LEFT JOIN episodes e ON e.id = j.episode_id
        ORDER BY j.id DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    conn.close()
    out = []
    for r in rows:
        d = dict(r)
        try:
            d["log"] = json.loads(d["log"] or "[]")
        except Exception:
            d["log"] = []
        out.append(d)
    return out


def get_job(job_id: int) -> Optional[dict]:
    conn = connect()
    row = conn.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
    conn.close()
    if not row:
        return None
    d = dict(row)
    try:
        d["log"] = json.loads(d["log"] or "[]")
    except Exception:
        d["log"] = []
    return d


# ---- migrate from old channels/ folder ----

def migrate_from_legacy() -> dict:
    """Import channels/episodes from old YouTube/channels/* layout into DB + storage."""
    legacy = ROOT / "channels"
    stats = {"channels": 0, "episodes": 0, "skipped": 0}
    if not legacy.exists():
        return stats
    init_db()
    for ch_dir in sorted(legacy.iterdir()):
        if not ch_dir.is_dir():
            continue
        slug = ch_dir.name
        existing = get_channel_by_slug(slug)
        if not existing:
            try:
                ch = create_channel(slug)
                stats["channels"] += 1
            except ValueError:
                ch = get_channel_by_slug(slug)
        else:
            ch = existing
        if not ch:
            continue
        for kind, folder_name in (("shorts", "shorts"), ("long", "longs")):
            src_kind = ch_dir / "videos" / folder_name
            if not src_kind.exists():
                continue
            for ep_dir in sorted(src_kind.iterdir()):
                if not ep_dir.is_dir():
                    continue
                # already in DB?
                conn = connect()
                row = conn.execute(
                    "SELECT id FROM episodes WHERE channel_id=? AND folder=?",
                    (ch["id"], ep_dir.name),
                ).fetchone()
                conn.close()
                if row:
                    stats["skipped"] += 1
                    continue
                title = titlelib.resolve_title(ep_dir, ep_dir.name) if titlelib else ep_dir.name
                dest = STORAGE / ch["slug"] / folder_name / ep_dir.name
                if not dest.exists():
                    shutil.copytree(ep_dir, dest)
                now = _now()
                conn = connect()
                conn.execute(
                    """
                    INSERT INTO episodes(
                        channel_id, title, kind, status, folder,
                        created_at, updated_at
                    ) VALUES (?,?,?,?,?,?,?)
                    """,
                    (ch["id"], title, kind if kind == "shorts" else "long", "draft", ep_dir.name, now, now),
                )
                conn.commit()
                ep_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
                conn.close()
                _refresh_flags(ep_id)
                stats["episodes"] += 1
    return stats


# ---- analytics ----

def upsert_video_stats(episode_id: int, date: str, **fields) -> dict:
    allowed = {"views", "likes", "comments", "shares", "watch_time_h", "subscribers", "ctr", "source", "note"}
    data = {k: v for k, v in fields.items() if k in allowed}
    now = _now()
    conn = connect()
    row = conn.execute(
        "SELECT id FROM video_stats WHERE episode_id=? AND date=?",
        (episode_id, date),
    ).fetchone()
    if row:
        if data:
            sets = ", ".join(f"{k}=?" for k in data)
            params = list(data.values()) + [row["id"]]
            conn.execute(f"UPDATE video_stats SET {sets} WHERE id=?", params)
    else:
        cols = ["episode_id", "date", "created_at"] + list(data.keys())
        placeholders = ",".join("?" * len(cols))
        params = [episode_id, date, now] + list(data.values())
        conn.execute(
            f"INSERT INTO video_stats({','.join(cols)}) VALUES ({placeholders})",
            params,
        )
    conn.commit()
    row = conn.execute(
        "SELECT * FROM video_stats WHERE episode_id=? AND date=?",
        (episode_id, date),
    ).fetchone()
    conn.close()
    return dict(row)


def list_video_stats(episode_id=None, channel_id=None):
    conn = connect()
    sql = """
        SELECT vs.*, e.title AS episode_title, e.kind, c.name AS channel_name, c.id AS channel_id
        FROM video_stats vs
        JOIN episodes e ON e.id = vs.episode_id
        JOIN channels c ON c.id = e.channel_id
        WHERE 1=1
    """
    params = []
    if episode_id:
        sql += " AND vs.episode_id=?"
        params.append(episode_id)
    if channel_id:
        sql += " AND e.channel_id=?"
        params.append(channel_id)
    sql += " ORDER BY vs.date DESC, vs.id DESC"
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def analytics_summary(channel_id=None):
    eps = list_episodes(channel_id=channel_id)
    stats = list_video_stats(channel_id=channel_id)
    total_views = sum(s.get("views") or 0 for s in stats)
    total_likes = sum(s.get("likes") or 0 for s in stats)
    total_comments = sum(s.get("comments") or 0 for s in stats)
    total_watch = sum(s.get("watch_time_h") or 0 for s in stats)
    by_ep = {}
    for s in stats:
        eid = s["episode_id"]
        if eid not in by_ep:
            by_ep[eid] = {
                "episode_id": eid,
                "title": s.get("episode_title"),
                "channel_name": s.get("channel_name"),
                "kind": s.get("kind"),
                "views": 0,
                "likes": 0,
                "comments": 0,
                "watch_time_h": 0,
            }
        by_ep[eid]["views"] += s.get("views") or 0
        by_ep[eid]["likes"] += s.get("likes") or 0
        by_ep[eid]["comments"] += s.get("comments") or 0
        by_ep[eid]["watch_time_h"] += s.get("watch_time_h") or 0
    top = sorted(by_ep.values(), key=lambda x: x["views"], reverse=True)[:10]
    by_date = {}
    for s in stats:
        d = s["date"]
        if d not in by_date:
            by_date[d] = {"date": d, "views": 0, "likes": 0, "comments": 0}
        by_date[d]["views"] += s.get("views") or 0
        by_date[d]["likes"] += s.get("likes") or 0
        by_date[d]["comments"] += s.get("comments") or 0
    timeline = sorted(by_date.values(), key=lambda x: x["date"])
    return {
        "episodes_total": len(eps),
        "episodes_rendered": sum(1 for e in eps if e.get("has_video")),
        "stats_rows": len(stats),
        "total_views": total_views,
        "total_likes": total_likes,
        "total_comments": total_comments,
        "total_watch_time_h": round(total_watch, 2),
        "top_videos": top,
        "timeline": timeline,
    }


def fix_all_titles() -> int:
    if not titlelib:
        return 0
    conn = connect()
    rows = conn.execute(
        """
        SELECT e.id, e.folder, c.slug, e.kind
        FROM episodes e JOIN channels c ON c.id = e.channel_id
        """
    ).fetchall()
    conn.close()
    fixed = 0
    for r in rows:
        kind_folder = "shorts" if r["kind"] == "shorts" else "longs"
        ep_dir = STORAGE / r["slug"] / kind_folder / r["folder"]
        if not ep_dir.exists():
            continue
        title = titlelib.resolve_title(ep_dir, r["folder"])
        conn = connect()
        conn.execute(
            "UPDATE episodes SET title=?, updated_at=? WHERE id=?",
            (title, _now(), r["id"]),
        )
        conn.commit()
        conn.close()
        fixed += 1
    return fixed


def update_channel(channel_id: int, **fields) -> dict:
    allowed = {"name", "description", "youtube_channel_url"}
    sets, params = [], []
    for k, v in fields.items():
        if k in allowed:
            sets.append(f"{k}=?")
            params.append(v)
    if not sets:
        return get_channel(channel_id)
    sets.append("updated_at=?")
    params.append(_now())
    params.append(channel_id)
    conn = connect()
    conn.execute(f"UPDATE channels SET {', '.join(sets)} WHERE id=?", params)
    conn.commit()
    conn.close()
    return get_channel(channel_id)
