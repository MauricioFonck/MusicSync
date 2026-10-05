# Estado de la Fase 4 — Storage

La Fase 4 está implementada en `backend/src/musicsync/infrastructure/storage/`.

Incluye un adaptador local sustituible para descubrir puntos montados, identidad basada en volumen y no en letra de unidad, etiqueta, filesystem, capacidad y espacio libre. `StorageMonitor` compara snapshots y emite `StorageConnected`/`StorageDisconnected`, conserva el último dispositivo desconectado como no disponible y exige una nueva validación antes de operar o reanudar.

También se añadió persistencia SQLAlchemy para dispositivos y errores explícitos de dispositivo no disponible y espacio insuficiente. El código no borra archivos parciales automáticamente durante una desconexión.
