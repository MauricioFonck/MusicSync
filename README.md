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

### Políticas para Claude

Las reglas viven en [`MUSICSYNC_POLICY.md`](MUSICSYNC_POLICY.md). El servidor MCP las entrega a Claude de cuatro formas: como `instructions` al conectarse, como resource `musicsync://policy`, con la herramienta `get_policy` y con el prompt `sync_songs` (flujo guiado). El archivo se relee en cada consulta: edítalo y aplica sin reiniciar. Son reglas de texto (Claude las sigue, pero no son una barrera); lo único que el servidor hace cumplir es el máximo de canciones por lote (`MUSICSYNC_MAX_BATCH`, 25 por defecto). Otra ruta de política: variable `MUSICSYNC_POLICY`.

## Búsqueda rápida en Spotify (opcional)

Sin claves, la búsqueda de Spotify usa spotDL: devuelve 1 resultado y tarda ~30 s. Con claves de la API oficial devuelve hasta 20 resultados en menos de un segundo:

1. Entra a <https://developer.spotify.com/dashboard> con tu cuenta de Spotify y pulsa **Create app**.
2. Nombre y descripción libres; en *Redirect URI* pon `http://127.0.0.1:8000/callback` (no se usa, pero es obligatorio); marca **Web API**.
3. En *Settings* copia **Client ID** y **Client secret** a un archivo `.env` en la raíz del repo (copia de `.env.example`):
   ```env
   SPOTIFY_CLIENT_ID=tu_client_id
   SPOTIFY_CLIENT_SECRET=tu_client_secret
   ```
4. Reinicia el backend. El aviso lento desaparece del buscador cuando las claves funcionan.

`.env` está en `.gitignore`: las claves no se suben al repo.

## Requisitos de ejecución

`ffmpeg`/`ffprobe`, `yt-dlp` y (para Spotify) `spotdl` deben estar en el `PATH`, o configurarse en `.env` (ver `.env.example`).

Flujo: analizar URL → elegir pistas y USB → descarga a `<USB>/.musicsync-tmp` → FFmpeg (con etiquetas) → validación ffprobe → SHA-256 → movimiento atómico a `<USB>/MUSIC/Artista/Álbum/Título.mp3`. Las pistas ya presentes en la USB se omiten. Los jobs se guardan en SQLite; si el proceso se reinicia en medio de un job, este queda `PAUSED` y se puede reanudar desde Historial.

## Legalidad

MusicSync debe utilizarse únicamente con contenido que el usuario tenga derecho a descargar o que la plataforma permita descargar. No se implementarán mecanismos para evadir DRM, controles de acceso o restricciones técnicas.
