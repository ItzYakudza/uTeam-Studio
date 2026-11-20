#!/usr/bin/env python3
"""
uTeam-Studio — single entrypoint.

Usage:
  python manage.py doctor
  python manage.py render [--preview] [episode_path]
  python manage.py stats [--deep]
  python manage.py dashboard
  python manage.py import-yt
  python manage.py dedupe
  python manage.py interactive
  python manage.py   # interactive menu
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
YT_DIR = ROOT / "YouTube"
WEB_DIR = ROOT / "web"

# Windows console UTF-8
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# Ensure project paths
for p in (str(YT_DIR), str(WEB_DIR), str(ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)


def cmd_doctor(_args):
    os.chdir(YT_DIR)
    sys.argv = ["build.py", "doctor"]
    import build
    return build.main()


def cmd_render(args):
    os.chdir(YT_DIR)
    argv = ["build.py", "render"]
    if args.preview:
        argv.append("--preview")
    if args.episode:
        argv.append(args.episode)
    sys.argv = argv
    import build
    return build.main()


def cmd_interactive(_args):
    os.chdir(YT_DIR)
    sys.argv = ["build.py"]
    import build
    return build.main()


def cmd_dashboard(_args):
    """Start API (5050) + print UI hint."""
    env = os.environ.copy()
    env.setdefault("PYTHONIOENCODING", "utf-8")
    api = WEB_DIR / "server.py"
    print("Starting API on http://127.0.0.1:5050 …")
    print("UI: cd web/frontend && npm run dev  → http://localhost:5173")
    if api.exists():
        os.chdir(WEB_DIR)
        return subprocess.call([sys.executable, str(api)], env=env)
    print("web/server.py not found")
    return 1


def cmd_stats(args):
    os.chdir(WEB_DIR)
    import worker as W
    if args.deep:
        print("Deep sync (OAuth import + Analytics for videos ≥24h)…")
        try:
            r = W.import_from_oauth(max_videos=100)
            print(r)
        except Exception as e:
            print("import_from_oauth:", e)
    print("Running sync_all…")
    try:
        r = W.sync_all()
        print(r)
    except Exception as e:
        print("sync_all:", e)
        return 1
    return 0


def cmd_import_yt(_args):
    os.chdir(WEB_DIR)
    import worker as W
    r = W.import_from_oauth(max_videos=100)
    print(r)
    return 0 if r.get("ok") else 1


def cmd_dedupe(_args):
    os.chdir(WEB_DIR)
    import db as D
    r = D.dedupe_youtube_episodes(delete_folders=True)
    print(r)
    return 0


def build_parser():
    p = argparse.ArgumentParser(prog="manage.py", description="uTeam-Studio")
    sub = p.add_subparsers(dest="cmd")

    sub.add_parser("doctor", help="Check environment / deps")
    sub.add_parser("interactive", help="Legacy interactive menu (build.py)")
    sub.add_parser("dashboard", help="Start web API")
    sub.add_parser("import-yt", help="Import channel via OAuth")
    sub.add_parser("dedupe", help="Remove duplicate episodes by youtube_id")

    pr = sub.add_parser("render", help="Render episode")
    pr.add_argument("--preview", action="store_true")
    pr.add_argument("episode", nargs="?", help="Episode path or folder name")

    ps = sub.add_parser("stats", help="Sync YouTube stats")
    ps.add_argument("--deep", action="store_true", help="OAuth import + deep Analytics")

    return p


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    if not argv:
        return cmd_interactive(None)

    parser = build_parser()
    args = parser.parse_args(argv)
    cmd = args.cmd
    if cmd == "doctor":
        return cmd_doctor(args) or 0
    if cmd == "render":
        return cmd_render(args) or 0
    if cmd == "interactive":
        return cmd_interactive(args) or 0
    if cmd == "dashboard":
        return cmd_dashboard(args) or 0
    if cmd == "stats":
        return cmd_stats(args) or 0
    if cmd == "import-yt":
        return cmd_import_yt(args) or 0
    if cmd == "dedupe":
        return cmd_dedupe(args) or 0
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
