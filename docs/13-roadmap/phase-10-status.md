# Estado de la Fase 10 — spotDL

La Fase 10 está implementada en `backend/src/musicsync/infrastructure/downloaders/spot_dl.py`.

`SpotDlDownloaderAdapter` se mantiene detrás de `DownloaderPort`, valida exclusivamente URLs de Spotify, transforma metadata JSON a entidades `Track`, descarga mediante argumentos separados y comparte los errores normalizados del motor general. `SourceResolver` puede seleccionar el adapter Spotify sin que controllers o dominio conozcan detalles del CLI.

La integración se prueba con runners simulados para mantener la suite determinista y no ejecutar descargas reales ni acceder a contenido no autorizado.
