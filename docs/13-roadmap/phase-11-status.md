# Estado de la Fase 11 — Packaging

La evaluación de packaging queda cerrada sin introducir Tauri todavía, conforme a ADR-007: el MVP debe estabilizarse antes de añadir un runtime de escritorio.

## Decisión actual

- **Distribución reproducible inmediata:** Docker para el backend y build estático de Angular.
- **Runtime multimedia:** el Dockerfile instala FFmpeg desde los paquetes del sistema, elimina caches de apt y ejecuta la aplicación con el usuario no root `musicsync`.
- **Instalador futuro:** Tauri sigue siendo la opción recomendada para `MusicSync-Setup.exe` cuando el flujo API, persistencia, USB y recuperación estén estabilizados.
- **Versionado:** usar SemVer (`MAJOR.MINOR.PATCH`) y publicar notas de release con cambios, migraciones y binarios requeridos.

## Checklist de release futuro

1. Compilar frontend en modo producción.
2. Empaquetar backend, frontend compilado, FFmpeg, yt-dlp y spotDL.
3. Crear configuración inicial sin secretos.
4. Ejecutar pruebas backend, lint, mypy y smoke test HTTP.
5. Validar detección USB, desconexión, reanudación y cancelación en el sistema objetivo.
6. Generar instalador Tauri firmado y publicar checksum.
