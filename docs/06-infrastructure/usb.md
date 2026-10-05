# Detección USB

## WindowsStorageDeviceAdapter

Debe detectar:

- conexión;
- desconexión;
- volumen;
- etiqueta;
- filesystem;
- capacidad;
- espacio libre;
- identificador estable disponible.

No usar la letra `E:`/`F:` como identidad del dispositivo.

## Desconexión

Durante una operación:

```text
USB disconnected
-> PAUSED
-> preserve state
-> wait
-> USB connected
-> validate destination
-> resume
```

Nunca borrar archivos parciales automáticamente sin verificar su propiedad y estado.
