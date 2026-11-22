@echo off
chcp 65001 >nul
cd /d "%~dp0frontend"
title uTeam-UI :5173
if not exist "node_modules\" call npm install
echo Starting UI on http://localhost:5173 ...
npm run dev -- --host 0.0.0.0
pause
