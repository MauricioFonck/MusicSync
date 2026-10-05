# Estado de la Fase 1 — Domain

La Fase 1 está implementada en `backend/src/musicsync/domain/`.

Incluye value objects inmutables, entidades de Track, DownloadItem, DownloadJob y StorageDevice, servicios de normalización, sanitización, rutas, duplicados y política de descarga, eventos de dominio y puertos para motores, procesamiento multimedia, persistencia y almacenamiento.

Las reglas críticas están cubiertas por pruebas unitarias en `backend/tests/domain/`. Las implementaciones concretas de base de datos, filesystem, USB, yt-dlp y FFmpeg quedan para las fases posteriores y no se importan desde el dominio.
