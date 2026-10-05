# Plan de implementación

## Fase 0 — Bootstrap

- repositorio;
- estructura;
- Python;
- Angular;
- lint;
- tests;
- CI.

## Fase 1 — Domain

- entidades;
- value objects;
- servicios;
- eventos;
- puertos;
- tests.

## Fase 2 — Persistence

- SQLAlchemy;
- SQLite;
- Alembic;
- repositories;
- tests.

## Fase 3 — Filesystem

- paths;
- sanitización;
- temp;
- atomic move;
- checksum.

## Fase 4 — Storage

- detección USB;
- eventos;
- espacio;
- desconexión.

## Fase 5 — Media

- FFmpeg adapter;
- metadata;
- validación.

## Fase 6 — Download

- yt-dlp adapter;
- resolver;
- orchestration;
- progreso.

## Fase 7 — API

- FastAPI;
- DTOs;
- endpoints;
- WebSocket.

## Fase 8 — Angular

- shell;
- dashboard;
- downloads;
- storage;
- history;
- settings.

## Fase 9 — Robustez

- reintentos;
- recuperación;
- idempotencia;
- cancelación;
- errores.

## Fase 10 — spotDL

Integrar Spotify detrás del mismo puerto.

## Fase 11 — Packaging

Evaluar Tauri, instalador y actualizaciones.
