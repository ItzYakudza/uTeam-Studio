@echo off
chcp 65001 >nul
title uTeam Studio — Web UI
cd /d "%~dp0"

echo ============================================================
echo   uTeam Studio — Web UI
echo ============================================================
echo.

:: --- check Python ---
where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python не найден. Установи Python 3.10+ и добавь в PATH.
    pause
    exit /b 1
)

:: --- check Node ---
where node >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js не найден. Установи Node.js 18+ и добавь в PATH.
    pause
    exit /b 1
)

:: --- install Python deps if needed ---
echo [1/4] Проверка Python-зависимостей...
python -c "import fastapi, uvicorn" 2>nul
if errorlevel 1 (
    echo       Устанавливаю fastapi uvicorn...
    python -m pip install fastapi uvicorn pydantic -q
)

:: --- install frontend deps if needed ---
echo [2/4] Проверка frontend (npm)...
if not exist "web\frontend\node_modules" (
    echo       npm install...
    pushd web\frontend
    call npm install --no-audit --no-fund
    popd
)

:: --- start backend ---
echo [3/4] Запуск backend  http://127.0.0.1:5050
start "uTeam-Backend" cmd /k "cd /d "%~dp0web" && python -m uvicorn server:app --host 127.0.0.1 --port 5050"

:: small delay so API is up before frontend opens
timeout /t 2 /nobreak >nul

:: --- start frontend ---
echo [4/4] Запуск frontend  http://localhost:5173
start "uTeam-Frontend" cmd /k "cd /d "%~dp0web\frontend" && npx vite --host 127.0.0.1 --port 5173"

timeout /t 3 /nobreak >nul

echo.
echo ============================================================
echo   Готово.
echo   Открой в браузере:  http://localhost:5173
echo.
echo   Окна Backend и Frontend оставлены открытыми.
echo   Закрой их, когда закончишь работу.
echo ============================================================
echo.

:: open browser
start "" "http://localhost:5173"

pause
