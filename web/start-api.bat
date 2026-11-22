@echo off
chcp 65001 >nul
cd /d "%~dp0"
title uTeam-API :5050
echo Starting API on http://127.0.0.1:5050 ...
python -c "import fastapi,uvicorn" 2>nul || python -m pip install -q fastapi uvicorn python-multipart
python server.py
pause
