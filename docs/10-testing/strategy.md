# Estrategia de pruebas

## Unit

- TrackNormalizationService
- DuplicateDetectionService
- FilenameSanitizer
- StoragePathService
- DownloadPolicy
- value objects

## Integration

- repositorios SQLite;
- yt-dlp adapter;
- FFmpeg adapter;
- filesystem;
- USB adapter.

## E2E

```text
analyze URL
-> select USB
-> create job
-> download
-> process
-> hash
-> duplicate check
-> atomic move
-> history
```

## Casos críticos

1. Misma URL dos veces.
2. Dos URLs para la misma pista.
3. Archivo con mismo checksum.
4. USB desconectada durante descarga.
5. Aplicación cerrada durante descarga.
6. Poco espacio.
7. Nombre inválido.
8. Path traversal.
9. Fuente no soportada.
10. Error de FFmpeg.
