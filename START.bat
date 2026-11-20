@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"

echo [uTeam-Studio] starting API on :5050 ...
start "uTeam-API" cmd /k call "%~dp0web\start-api.bat"

timeout /t 2 /nobreak >nul

echo [uTeam-Studio] starting UI on :5173 ...
start "uTeam-UI" cmd /k call "%~dp0web\start-ui.bat"

echo.
echo API:  http://127.0.0.1:5050
echo UI:   http://localhost:5173
echo.
