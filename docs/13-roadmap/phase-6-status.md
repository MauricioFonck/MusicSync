# Estado de la Fase 6 — Download

La Fase 6 está implementada en `backend/src/musicsync/infrastructure/downloaders/` y `backend/src/musicsync/application/download_orchestrator.py`.

Incluye `YtDlpDownloaderAdapter`, que valida URLs HTTP(S), ejecuta `yt-dlp` con argumentos separados y timeout, normaliza metadata a `Track`, descarga una pista analizada, informa progreso inicial/final y controla cancelación por job. `SourceResolver` selecciona el adapter por host y permite fallback a otras fuentes sin llevar esa lógica a los controllers.

`DownloadOrchestrator` coordina análisis, descarga por item, actualización de progreso, aislamiento de errores y estado final del job. La integración de Spotify queda preparada detrás de `DownloaderPort`, sin implementar bypass de DRM ni acceso no autorizado.
