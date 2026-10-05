# WebSocket

Endpoint:

`/ws/downloads/{job_id}`

Eventos:

- `download.started`
- `download.progress`
- `download.completed`
- `download.failed`
- `download.skipped`
- `download.duplicate`
- `storage.connected`
- `storage.disconnected`

Ejemplo:

```json
{
  "event": "download.progress",
  "job_id": "job-123",
  "item_id": "item-456",
  "progress": 63,
  "status": "DOWNLOADING"
}
```
