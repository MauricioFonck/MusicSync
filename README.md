# MusicSync

Sistema local-first para gestionar, procesar y sincronizar contenido musical autorizado hacia memorias USB.

## Estado

Bootstrap inicial del monorepo. La arquitectura y el alcance están definidos en [`docs/`](docs/README.md).

## Estructura

- `backend/` — API FastAPI y núcleo de dominio.
- `frontend/` — aplicación Angular.
- `docs/` — especificación funcional y técnica.
- `.github/workflows/` — validaciones de CI.

## Backend

```bash
cd backend
uv sync --dev
uv run pytest
uv run ruff check .
uv run mypy src
uv run uvicorn musicsync.main:app --reload
```

Health check: `GET http://127.0.0.1:8000/api/v1/health`

## Frontend

```bash
cd frontend
npm install
npm start   # http://localhost:4200, /api y /ws se redirigen al backend (proxy.conf.json)
npm test -- --watch=false
```

## Usar MusicSync desde Claude (MCP)

El repo incluye `.mcp.json` en la raíz: Claude Code lo detecta al abrir el proyecto (aprueba el servidor `musicsync`). Con el backend corriendo, Claude puede buscar canciones en YouTube/Spotify y sincronizarlas con estas herramientas: `search_music`, `analyze_url`, `list_devices`, `start_sync`, `queue_songs` (lote «Artista - Título»), `job_status`, `list_jobs`, `cancel_job`.

Ejemplo: «Descarga estas 10 canciones a la USB: …». Úsalo solo con contenido que tengas derecho a descargar.

## Requisitos de ejecución

`ffmpeg`/`ffprobe`, `yt-dlp` y (para Spotify) `spotdl` deben estar en el `PATH`, o configurarse en `.env` (ver `.env.example`).

Flujo: analizar URL → elegir pistas y USB → descarga a `<USB>/.musicsync-tmp` → FFmpeg (con etiquetas) → validación ffprobe → SHA-256 → movimiento atómico a `<USB>/MUSIC/Artista/Álbum/Título.mp3`. Las pistas ya presentes en la USB se omiten. Los jobs se guardan en SQLite; si el proceso se reinicia en medio de un job, este queda `PAUSED` y se puede reanudar desde Historial.

## Legalidad

MusicSync debe utilizarse únicamente con contenido que el usuario tenga derecho a descargar o que la plataforma permita descargar. No se implementarán mecanismos para evadir DRM, controles de acceso o restricciones técnicas.
