@echo off
setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul
title uTeam-Studio Web

cd /d "%~dp0"
set "WEB_DIR=%CD%"

echo.
echo  ============================================
echo   uTeam-Studio Web
echo  ============================================
echo   %WEB_DIR%
echo.

:: --- find python ---
set "PY="
where python >nul 2>&1 && set "PY=python"
if not defined PY (
  where py >nul 2>&1 && set "PY=py -3"
)
if not defined PY (
  echo [ERR] Python не найден. Установи с python.org и поставь галочку Add to PATH
  pause
  exit /b 1
)
echo [OK] Python: 
%PY% --version

:: --- node ---
where npm >nul 2>&1
if errorlevel 1 (
  echo [ERR] npm не найден. Установи Node.js LTS: https://nodejs.org
  pause
  exit /b 1
)
echo [OK] npm:
call npm --version

:: --- server.py check ---
if not exist "%WEB_DIR%\server.py" (
  echo [ERR] server.py не найден в %WEB_DIR%
  echo       Запускай start.bat из папки web\
  pause
  exit /b 1
)

:: --- deps ---
echo.
echo [1/3] Python packages...
%PY% -c "import fastapi,uvicorn" 2>nul
if errorlevel 1 (
  echo      pip install fastapi uvicorn python-multipart
  %PY% -m pip install fastapi uvicorn python-multipart
  if errorlevel 1 (
    echo [ERR] pip install failed
    pause
    exit /b 1
  )
)

:: --- frontend ---
echo [2/3] Frontend...
if not exist "%WEB_DIR%\frontend\package.json" (
  echo [ERR] Нет frontend\package.json
  pause
  exit /b 1
)
if not exist "%WEB_DIR%\frontend\node_modules\" (
  echo      npm install...
  pushd "%WEB_DIR%\frontend"
  call npm install
  if errorlevel 1 (
    echo [ERR] npm install failed
    popd
    pause
    exit /b 1
  )
  popd
)

echo [3/3] Starting...
echo.

:: Backend
start "uTeam-API" cmd /k "cd /d "%WEB_DIR%" && title uTeam-API :5050 && %PY% server.py"

timeout /t 2 /nobreak >nul

:: Frontend
start "uTeam-UI" cmd /k "cd /d "%WEB_DIR%\frontend" && title uTeam-UI :5173 && npm run dev -- --host 0.0.0.0"

timeout /t 3 /nobreak >nul
start "" http://localhost:5173

echo.
echo   API  http://127.0.0.1:5050
echo   UI   http://localhost:5173
echo.
echo   Два окна cmd открыты. Их нельзя закрывать, пока работаешь.
echo   Это окно можно закрыть.
echo.
pause
endlocal
