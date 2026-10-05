# Núcleo de dominio

Esta capa contiene reglas de negocio puras y no depende de FastAPI, SQLAlchemy, yt-dlp, spotDL, FFmpeg ni APIs del sistema operativo.

- `value_objects/` valida identificadores, metadata, rutas y estados.
- `entities/` modela pistas, trabajos, elementos y dispositivos.
- `services/` encapsula normalización, duplicados, sanitización, rutas y política legal.
- `events/` define eventos inmutables para desacoplar reacciones futuras.
- `ports/` define contratos que implementará la infraestructura.
