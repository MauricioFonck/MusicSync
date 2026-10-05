# Servicios de dominio

## DuplicateDetectionService

Evalúa:

1. source + source_id;
2. metadata normalizada;
3. duración;
4. checksum cuando exista.

Devuelve una decisión:

```text
NEW
DUPLICATE
POSSIBLE_DUPLICATE
```

## TrackNormalizationService

Normaliza artista y título sin destruir información musical relevante.

## StoragePathService

Construye rutas seguras:

```text
MUSIC/Artist/Album/01 - Title.mp3
```

## FilenameSanitizer

Elimina caracteres inválidos de Windows y evita nombres reservados.

## DownloadPolicy

Valida que la operación cumpla las reglas del sistema antes de iniciarse.
