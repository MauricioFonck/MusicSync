# Motores de descarga

## yt-dlp

Adaptador:

`YtDlpDownloaderAdapter`

Responsabilidades:

- validar/analizar URL;
- extraer metadata;
- procesar playlists;
- descargar;
- informar progreso;
- devolver resultados normalizados.

La integración debe usar un wrapper interno y no exponer objetos propios de yt-dlp al dominio.

## spotDL

Adaptador:

`SpotDlDownloaderAdapter`

Se utilizará para flujos de Spotify cuando corresponda. Debe estar detrás de `DownloaderPort`.

## SourceResolver

```text
URL
 |
SourceResolver
 |
 +-- Spotify -> spotDL
 |
 +-- demás fuentes compatibles -> yt-dlp
```

No colocar esta lógica en el controller de FastAPI.
