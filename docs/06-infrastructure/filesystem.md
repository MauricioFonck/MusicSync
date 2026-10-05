# Filesystem

## Regla de escritura

```text
download
-> temp
-> process
-> validate
-> checksum
-> duplicate check
-> atomic rename/move
-> database commit
```

## Estructura

```text
MUSIC/
  Artist/
    Album/
      01 - Track.mp3
```

## Seguridad

Proteger contra:

- path traversal;
- nombres inválidos;
- nombres reservados de Windows;
- rutas excesivamente largas;
- colisiones de nombres.

Nunca aceptar una ruta absoluta arbitraria desde el frontend como destino final.
