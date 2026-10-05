# Arquitectura

MusicSync usa arquitectura hexagonal.

```text
Angular
   |
HTTP / WebSocket
   |
Adapters
   |
Application
   |
Domain
   |
Ports
   |
Infrastructure
   +-- yt-dlp
   +-- spotDL
   +-- FFmpeg
   +-- SQLite/PostgreSQL
   +-- Windows USB
   +-- Filesystem
```

## Regla de dependencias

```text
Adapters -> Application -> Domain
Infrastructure -> Ports
```

El dominio no puede importar:

- FastAPI;
- Angular;
- SQLAlchemy;
- yt-dlp;
- spotDL;
- FFmpeg;
- Windows APIs.

## Backend

```text
backend/src/musicsync/
├── domain/
├── application/
├── infrastructure/
└── adapters/
```

## Frontend

Angular se organiza por funcionalidades:

```text
core/
shared/
features/
layout/
```

No se debe convertir `shared/` en un cajón de sastre. Solo contiene elementos realmente reutilizables.
