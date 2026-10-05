# Requisitos

## Funcionales

### RF-01 Analizar fuente
El sistema debe aceptar una URL y devolver la fuente, metadata y elementos disponibles.

### RF-02 Crear trabajo
Debe permitir crear un trabajo seleccionando destino y configuración.

### RF-03 Descargar
Debe descargar solamente los elementos necesarios.

### RF-04 Evitar duplicados
Debe detectar elementos existentes antes de generar un archivo adicional.

### RF-05 Procesar
Debe convertir/procesar el archivo mediante FFmpeg cuando corresponda.

### RF-06 Validar
Debe validar existencia, tamaño, metadata, duración e integridad antes de finalizar.

### RF-07 USB
Debe detectar conexión y desconexión de dispositivos extraíbles.

### RF-08 Historial
Debe registrar resultados de cada elemento.

### RF-09 Progreso
Debe mostrar progreso por trabajo y por pista.

### RF-10 Recuperación
Debe poder recuperar trabajos interrumpidos de forma segura.

### RF-11 Configuración
Debe permitir modificar formato, calidad, plantilla y preferencias.

### RF-12 Cancelación
Debe permitir cancelar un trabajo sin dejar estados inconsistentes.

## No funcionales

- NFR-01 Arquitectura hexagonal.
- NFR-02 Código testeable.
- NFR-03 Logs estructurados.
- NFR-04 No almacenar secretos en Git.
- NFR-05 Operaciones idempotentes.
- NFR-06 Seguridad contra path traversal.
- NFR-07 Dependencias auditables.
- NFR-08 UI responsive.
- NFR-09 Recuperación segura ante desconexión.
- NFR-10 Evolución a escritorio mediante Tauri.
