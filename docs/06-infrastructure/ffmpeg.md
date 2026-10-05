# FFmpeg

Adaptador:

`FfmpegMediaProcessor`

Responsabilidades:

- convertir;
- inspeccionar;
- validar;
- obtener duración;
- obtener bitrate;
- integrar metadata;
- integrar portada cuando esté disponible.

La aplicación debe invocar FFmpeg de forma segura, sin concatenar input del usuario en comandos shell.
