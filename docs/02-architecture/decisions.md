# Decisiones arquitectónicas

## ADR-001 Angular

Angular se selecciona por su estructura opinionada, TypeScript, DI, routing, formularios, RxJS y adecuación a aplicaciones modulares.

## ADR-002 FastAPI

FastAPI será el adaptador HTTP. No contiene reglas de negocio.

## ADR-003 SQLite inicial

SQLite minimiza complejidad para una aplicación local. El repositorio debe abstraerse para permitir PostgreSQL posteriormente.

## ADR-004 yt-dlp

Se utiliza como motor general de extracción compatible con múltiples fuentes.

## ADR-005 spotDL

Se utiliza como adaptador especializado para flujos de Spotify.

## ADR-006 FFmpeg

Se utiliza para procesamiento multimedia, conversión y validación.

## ADR-007 Tauri futuro

Tauri se reserva para la fase de empaquetado de escritorio. No debe introducirse antes de estabilizar el MVP.

## ADR-008 Anti-duplicados multinivel

Se combinan source ID, metadata normalizada, duración y checksum para reducir falsos negativos y evitar duplicados físicos.

## ADR-009 Escritura atómica

Los archivos nunca se escriben directamente en su ubicación final.
