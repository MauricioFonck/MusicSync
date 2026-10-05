# Value Objects

Se recomiendan:

- `TrackId`
- `JobId`
- `StorageDeviceId`
- `SourceId`
- `Checksum`
- `MediaPath`
- `NormalizedTitle`
- `NormalizedArtist`
- `Duration`
- `Quality`
- `MediaFormat`
- `DownloadStatus`

Los value objects deben ser inmutables y validar su propio estado.

Ejemplo conceptual:

```python
Checksum(value: str)
```

Debe rechazar valores vacíos o con formato inválido.
