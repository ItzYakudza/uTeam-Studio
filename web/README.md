# uTeam Studio — Web UI

Красивый веб-интерфейс для uTeam-Studio.  
Функционал тот же (каналы, эпизоды, рендер, sheet), но открывается в браузере на localhost.

## Стек

- **Backend**: FastAPI (`web/server.py`) — обёртка над `build.py`
- **Frontend**: React + Vite

## Запуск

### 1. Backend

```bash
cd YouTube
# зависимости рендера (если ещё нет)
pip install fastapi uvicorn pillow numpy moviepy

cd web
pip install -r requirements.txt
python server.py
```

API будет на **http://127.0.0.1:5050**

### 2. Frontend (dev)

```bash
cd YouTube/web/frontend
npm install
npm run dev
```

Открой **http://localhost:5173**

Vite проксирует `/api` на backend.

### Production-сборка UI

```bash
cd YouTube/web/frontend
npm run build
```

После `build` backend сам раздаёт `frontend/dist` с того же порта 5050.

## Возможности UI

- Список каналов и эпизодов
- Создание / удаление каналов и эпизодов
- Редактор `script.txt` и `scenes.py` прямо в браузере
- Тумблер **Preview / Full quality**
- Кнопки «Рендер» и «Контактный лист»
- Скачивание готового mp4, metadata, contact sheet
- Статус джобов внизу

## Важно

- `voiceover.mp3` по-прежнему нужно класть в папку эпизода вручную (ElevenLabs и т.п.).
- Рендер выполняется локально через MoviePy — это может занимать время.
- Большие mp4 из репозитория намеренно не клонировались; структура каналов создаётся через UI.
