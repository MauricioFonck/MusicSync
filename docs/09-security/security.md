# Seguridad

## Principios

- Validar todo input.
- No ejecutar shell con strings concatenados.
- Sanitizar nombres.
- Evitar path traversal.
- No registrar secretos.
- Limitar operaciones al dispositivo seleccionado.
- Usar timeouts.
- Controlar procesos hijos.
- Validar archivos generados.

## URL

Las URLs deben validarse antes de enviarse a un motor externo.

## Procesos

Preferir `subprocess` con argumentos separados.

## Secretos

Nunca subir:

- tokens;
- cookies;
- credenciales;
- archivos `.env` reales.

## Contenido

La aplicación debe respetar los derechos de uso del contenido. No implementar bypass de DRM o controles de acceso.
