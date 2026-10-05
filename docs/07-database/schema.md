# Modelo de datos

Tablas:

```text
tracks
sources
playlists
playlist_items
download_jobs
download_items
download_records
media_files
storage_devices
settings
```

## Relaciones

```text
source 1---N tracks
playlist 1---N playlist_items
download_job 1---N download_items
track 1---N media_files
track 1---N download_records
storage_device 1---N download_jobs
```

## Índices

- `(source, source_id)` en tracks cuando aplique.
- `checksum` en media_files.
- `track_id` en media_files.
- `device_identifier` en storage_devices.
- `job_id` en download_items.
