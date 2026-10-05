# Instrucciones para Claude Code — MusicSync

Este archivo define las reglas operativas para desarrollar MusicSync.

## Prioridad

La documentación de `docs/` y este archivo son la fuente de verdad del proyecto.

## Reglas arquitectónicas

1. Mantener arquitectura hexagonal.
2. No poner lógica de negocio en FastAPI.
3. No importar yt-dlp, spotDL, FFmpeg o SQLAlchemy dentro del dominio.
4. Definir puertos en el núcleo e implementarlos en infraestructura.
5. Mantener adaptadores reemplazables.
6. Angular debe organizarse por `core`, `shared`, `features` y `layout`.
7. Usar TypeScript strict.
8. Usar Signals/RxJS apropiadamente.
9. No crear un store global innecesario.
10. Toda funcionalidad nueva debe tener pruebas.

## Reglas de descargas

1. Nunca escribir directamente al destino final.
2. Usar directorio temporal.
3. Procesar.
4. Validar.
5. Calcular checksum.
6. Detectar duplicado.
7. Mover atómicamente.
8. Persistir el resultado.
9. Actualizar progreso.

## Reglas USB

- No confiar en la letra de unidad como identidad.
- Comprobar disponibilidad antes de cada operación crítica.
- Pausar ante desconexión.
- No borrar archivos sin verificar estado.

## Anti-duplicados

Evaluar, en orden:

1. source + source_id;
2. archivo existente;
3. metadata normalizada + duración;
4. checksum.

No crear variantes como `(1)`, `(2)` para ocultar duplicados.

## Dependencias

Antes de introducir una librería:

- comprobar mantenimiento;
- revisar licencia;
- evaluar necesidad;
- documentar motivo;
- aislarla si es infraestructura.

## Desarrollo

Antes de implementar una feature compleja:

1. leer la documentación relacionada;
2. identificar el caso de uso;
3. identificar puertos;
4. implementar dominio;
5. implementar infraestructura;
6. conectar adapter;
7. crear tests;
8. actualizar documentación.

## Primera ejecución

Antes de implementar descargas reales:

1. crear estructura del monorepo;
2. configurar backend;
3. configurar Angular;
4. configurar lint;
5. configurar tests;
6. configurar CI;
7. implementar dominio;
8. demostrar tests del dominio.

No saltar directamente al frontend ni al downloader.

## Calidad

No aceptar:

- imports circulares;
- lógica duplicada;
- `Any` innecesario;
- comandos shell inseguros;
- secretos en código;
- rutas arbitrarias;
- endpoints que accedan directamente a ORM;
- tests inexistentes para lógica crítica.

## Documentación

Cada módulo relevante debe explicar:

- propósito;
- responsabilidades;
- dependencias;
- interfaces;
- entradas;
- salidas;
- errores;
- tests.

## Legalidad

MusicSync debe utilizarse con contenido autorizado. No desarrollar mecanismos para evadir DRM, controles de acceso o restricciones de plataformas.
