# Entidades del dominio

## Track

```text
id
source
source_id
title
artist
album
album_artist
duration
track_number
disc_number
genre
release_date
thumbnail_url
original_url
```

## Playlist

```text
id
source
source_id
title
owner
items
original_url
```

## DownloadJob

```text
id
source_url
source_type
destination_device_id
status
total_items
completed_items
failed_items
skipped_items
created_at
started_at
completed_at
```

Estados:

```text
PENDING
ANALYZING
DOWNLOADING
PROCESSING
COMPLETED
PARTIALLY_COMPLETED
FAILED
CANCELLED
PAUSED
```

## DownloadItem

```text
id
job_id
track_id
status
progress
error
output_path
checksum
```

## StorageDevice

```text
id
device_identifier
volume_label
mount_point
filesystem
total_space
free_space
is_available
last_seen
```

## MediaFile

```text
id
track_id
path
filename
extension
size
duration
bitrate
checksum
created_at
```

## DownloadRecord

Historial inmutable de resultados de operaciones.

## Source

Valores iniciales:

```text
YOUTUBE
YOUTUBE_MUSIC
SPOTIFY
OTHER
```
