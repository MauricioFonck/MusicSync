# Casos de uso

Implementar:

- `AnalyzeSourceUseCase`
- `CreateDownloadJobUseCase`
- `StartDownloadJobUseCase`
- `CancelDownloadJobUseCase`
- `ResumeDownloadJobUseCase`
- `GetDownloadJobUseCase`
- `GetDownloadHistoryUseCase`
- `DetectStorageDevicesUseCase`
- `SelectStorageDeviceUseCase`
- `CheckDuplicateUseCase`
- `ProcessMediaUseCase`

## DownloadOrchestrator

Flujo:

```text
validate destination
-> analyze source
-> resolve adapter
-> obtain tracks
-> check DB
-> check filesystem
-> detect duplicates
-> download
-> process
-> hash
-> validate
-> atomic move
-> persist
-> emit progress
```
