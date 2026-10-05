# Estado de la Fase 5 — Media

La Fase 5 está implementada en `backend/src/musicsync/infrastructure/ffmpeg.py`.

Incluye `FfmpegMediaProcessor`, que invoca FFmpeg y FFprobe mediante argumentos separados y sin shell. El adaptador convierte a MP3, FLAC o WAV, aplica bitrate para MP3, inspecciona duración y bitrate, calcula SHA-256, valida que exista una pista de audio y elimina salidas parciales cuando una conversión falla.

Los errores de herramienta, inspección, validación y conversión están separados en `backend/src/musicsync/infrastructure/media_errors.py`. Las pruebas cubren metadata, checksum, rutas con espacios y caracteres especiales, validación de contenido sin audio y limpieza de resultados incompletos.
