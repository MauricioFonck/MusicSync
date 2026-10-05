# Estado de la Fase 2 — Persistence

La Fase 2 está implementada en `backend/src/musicsync/infrastructure/database/`.

Incluye modelos SQLAlchemy 2 para las tablas documentadas, engine y sesiones SQLite, repositorios para `Track`, `MediaFile` y `DownloadJob`, migración inicial versionada con Alembic y pruebas de integración sobre bases SQLite temporales.

Los repositorios traducen entre entidades/value objects del dominio y filas ORM. El dominio no importa SQLAlchemy. Para desarrollo se puede ejecutar `uv run alembic upgrade head`; las migraciones ya aplicadas no se modifican.
