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
npm start
```

## Legalidad

MusicSync debe utilizarse únicamente con contenido que el usuario tenga derecho a descargar o que la plataforma permita descargar. No se implementarán mecanismos para evadir DRM, controles de acceso o restricciones técnicas.
