# Almacenamiento extraíble

`LocalStorageDeviceAdapter` descubre puntos montados y obtiene capacidad, espacio libre, etiqueta y filesystem. La identidad se deriva de un identificador de volumen (`st_dev` en el adaptador local), no de una letra de unidad.

`StorageMonitor` compara snapshots, emite eventos de conexión/desconexión y expone `require_available` para validar disponibilidad y espacio antes de una operación crítica. La reconexión vuelve a aparecer como `StorageConnected`; el caso de uso superior debe validar nuevamente el destino antes de reanudar.

El adaptador es sustituible para integrar enumeración nativa de Windows sin cambiar el dominio.
